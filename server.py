from mcp.server.fastmcp import FastMCP, Context, Image

# Create an MCP server with a meaningful name
mcp = FastMCP("Example MCP Server")

# --- Resources ---
@mcp.resource("config://app")
def get_config() -> str:
    """Return the application configuration"""
    return """
    {
        "name": "Example MCP Server",
        "version": "1.0.0",
        "environment": "development"
    }
    """

@mcp.resource("docs://{topic}")
def get_documentation(topic: str) -> str:
    """Return documentation for a specific topic"""
    topics = {
        "overview": "This is an example MCP server that demonstrates core MCP concepts.",
        "resources": "Resources are like GET endpoints that provide data to LLMs.",
        "tools": "Tools allow LLMs to perform actions and computations.",
        "prompts": "Prompts are reusable templates for LLM interactions."
    }
    return topics.get(topic, f"Documentation for '{topic}' not found.")

# --- Tools ---
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.tool()
def format_text(text: str, format_type: str = "uppercase") -> str:
    """Format text according to the specified format type.
    
    Args:
        text: The text to format
        format_type: The formatting to apply (uppercase, lowercase, title)
    """
    if format_type == "uppercase":
        return text.upper()
    elif format_type == "lowercase":
        return text.lower()
    elif format_type == "title":
        return text.title()
    else:
        return text

@mcp.tool()
async def long_running_task(steps: int, ctx: Context) -> str:
    """Simulate a long-running task with progress reporting.
    
    Args:
        steps: Number of steps to simulate
        ctx: The MCP context for progress reporting
    """
    import asyncio
    
    for i in range(steps):
        # Report progress
        await ctx.report_progress(i, steps)
        # Log information
        ctx.info(f"Completed step {i+1} of {steps}")
        # Wait a bit
        await asyncio.sleep(0.5)
    
    return f"Completed all {steps} steps successfully"

# --- Prompts ---
@mcp.prompt()
def help_prompt() -> str:
    """A simple help prompt"""
    return """
    This is an example MCP server. You can:
    - Access documentation with resources like 'docs://overview'
    - Use tools like 'add_numbers' and 'format_text'
    - Interact with prompts for structured interactions
    
    How can I assist you today?
    """

@mcp.prompt()
def analyze_text(text: str) -> str:
    """Create a prompt to analyze text"""
    return f"""
    Please analyze the following text:
    
    {text}
    
    Provide insights on:
    1. The main themes
    2. The tone
    3. Key points
    4. Any recommendations
    """

# Run the server if executed directly
if __name__ == "__main__":
    mcp.run() 