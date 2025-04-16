from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import sqlite3
import os

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.responses import PlainTextResponse

from mcp.server.fastmcp import FastMCP, Context


# --- Database class to demonstrate lifespan ---
class Database:
    def __init__(self, path: str):
        self.path = path
        self.conn = None
    
    async def connect(self):
        """Connect to the SQLite database"""
        # Note: Using synchronous SQLite for simplicity
        # In production, consider using aiosqlite or similar
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables if they don't exist
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        return self
    
    async def disconnect(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def query(self, sql: str, params=None):
        """Execute a query and return results"""
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        return cursor.fetchall()
    
    def execute(self, sql: str, params=None):
        """Execute a query and commit changes"""
        if not self.conn:
            raise RuntimeError("Database not connected")
        
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        self.conn.commit()
        return cursor.lastrowid


# --- AppContext for type-safe lifespan ---
@dataclass
class AppContext:
    db: Database


# --- Lifespan handler ---
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    # Initialize database on startup
    db_path = "notes.db"
    print(f"Initializing database at {db_path}")
    db = await Database(db_path).connect()
    
    try:
        # Seed some data
        if db.query("SELECT COUNT(*) FROM notes")[0][0] == 0:
            db.execute(
                "INSERT INTO notes (title, content) VALUES (?, ?)",
                ("Welcome to MCP", "This is your first note created by the MCP server.")
            )
            db.execute(
                "INSERT INTO notes (title, content) VALUES (?, ?)",
                ("MCP Features", "MCP provides resources, tools, and prompts for LLM integration.")
            )
        
        # Yield the context to the server
        yield AppContext(db=db)
    finally:
        # Cleanup on shutdown
        print("Disconnecting from database")
        await db.disconnect()


# --- Create MCP server with lifespan ---
mcp = FastMCP(
    "Advanced MCP Server",
    lifespan=app_lifespan,
    dependencies=["starlette", "sqlite3"]
)


# --- Resources ---
@mcp.resource("notes://all")
def get_all_notes(ctx: Context) -> str:
    """Get all notes from the database"""
    db = ctx.request_context.lifespan_context.db
    notes = db.query("SELECT id, title, content FROM notes ORDER BY created_at DESC")
    
    result = []
    for note in notes:
        result.append(f"Note #{note['id']}: {note['title']}\n{note['content']}\n")
    
    return "\n".join(result)


@mcp.resource("notes://{note_id}")
def get_note(note_id: str, ctx: Context) -> str:
    """Get a specific note by ID"""
    db = ctx.request_context.lifespan_context.db
    note = db.query("SELECT id, title, content FROM notes WHERE id = ?", (note_id,))
    
    if not note:
        return f"Note with ID {note_id} not found."
    
    note = note[0]
    return f"Note #{note['id']}: {note['title']}\n\n{note['content']}"


@mcp.resource("schema://notes")
def get_schema(ctx: Context) -> str:
    """Get the database schema"""
    db = ctx.request_context.lifespan_context.db
    schema = db.query("SELECT sql FROM sqlite_master WHERE name='notes'")
    return schema[0][0]


# --- Tools ---
@mcp.tool()
def create_note(title: str, content: str, ctx: Context) -> str:
    """Create a new note in the database
    
    Args:
        title: The title of the note
        content: The content of the note
    """
    db = ctx.request_context.lifespan_context.db
    note_id = db.execute(
        "INSERT INTO notes (title, content) VALUES (?, ?)",
        (title, content)
    )
    
    return f"Created note #{note_id} with title: {title}"


@mcp.tool()
def delete_note(note_id: int, ctx: Context) -> str:
    """Delete a note from the database
    
    Args:
        note_id: The ID of the note to delete
    """
    db = ctx.request_context.lifespan_context.db
    result = db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    
    if result:
        return f"Deleted note #{note_id}"
    else:
        return f"Note #{note_id} not found or could not be deleted"


@mcp.tool()
def search_notes(query: str, ctx: Context) -> str:
    """Search notes by title or content
    
    Args:
        query: The search query
    """
    db = ctx.request_context.lifespan_context.db
    notes = db.query(
        "SELECT id, title, content FROM notes WHERE title LIKE ? OR content LIKE ?",
        (f"%{query}%", f"%{query}%")
    )
    
    if not notes:
        return f"No notes found matching query: {query}"
    
    result = [f"Found {len(notes)} matching notes:"]
    for note in notes:
        result.append(f"Note #{note['id']}: {note['title']}\n{note['content'][:100]}...")
    
    return "\n\n".join(result)


# --- Create Starlette app and mount MCP ---
app = Starlette(
    routes=[
        Mount('/mcp', app=mcp.sse_app()),
    ]
)

@app.route('/')
async def homepage(request):
    return PlainTextResponse("Advanced MCP Server\n\nMCP Endpoint: /mcp")


# --- Entry point ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 