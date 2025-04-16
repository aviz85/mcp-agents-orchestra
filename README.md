# MCP Agent Orchestration System

A Python implementation of a state-based agent orchestration system using the Model Context Protocol (MCP).

## What is MCP?

The Model Context Protocol (MCP) allows applications to provide context for LLMs in a standardized way, separating the concerns of providing context from the actual LLM interaction. With MCP, you can build servers that expose:

- **Resources**: Data sources that provide information to LLMs
- **Tools**: Functions that allow LLMs to perform actions
- **Prompts**: Reusable templates for LLM interactions

## Installation

### Prerequisites

- Python 3.10 or higher
- MCP Python SDK 1.2.0 or higher

### Setting Up Your Environment

#### Using uv (recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a new directory for our project
uv init mcp-agents-orchestra
cd mcp-agents-orchestra

# Create virtual environment and activate it
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows

# Install dependencies
uv add "mcp[cli]" httpx
```

#### Using pip

```bash
# Create a new directory for our project
mkdir mcp-agents-orchestra
cd mcp-agents-orchestra

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Unix/macOS
venv\Scripts\activate     # On Windows

# Install dependencies
pip install "mcp[cli]" httpx
```

### Clone or Download Project Files

Place the project files in your directory:

- `orchestrator.py` - The main MCP server implementing the state machine
- `orchestrator_client.py` - Client demonstrating the orchestration flow
- `requirements.txt` - Dependencies for the project
- `.gitignore` - Git ignore file

## Project Structure

- `orchestrator.py` - The main MCP server implementing the state machine
- `orchestrator_client.py` - Client demonstrating the orchestration flow
- `requirements.txt` - Dependencies for the project

## Running the Orchestration System

1. Start the orchestration server directly for testing:

```bash
python orchestrator.py
```

2. In a separate terminal, run the client to see the orchestration in action:

```bash
python orchestrator_client.py
```

## Integrating with Claude for Desktop

### 1. Install Claude for Desktop

Make sure you have Claude for Desktop installed. You can download the latest version from [Anthropic's website](https://claude.ai/desktop).

### 2. Configure Claude for Desktop

1. Open your Claude for Desktop configuration file:

   **macOS/Linux:**
   ```bash
   # Create or edit the configuration file
   code ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

   **Windows:**
   ```bash
   # Path may vary depending on your Windows version
   code %APPDATA%\Claude\claude_desktop_config.json
   ```

2. Add the orchestrator server configuration:

   ```json
   {
       "mcpServers": {
           "agent-orchestrator": {
               "command": "python",
               "args": [
                   "/ABSOLUTE/PATH/TO/YOUR/PROJECT/orchestrator.py"
               ]
           }
       }
   }
   ```

   Replace the path with the absolute path to your orchestrator.py file.

3. Save the configuration file and restart Claude for Desktop.

### 3. Using the Orchestrator in Claude

Once configured, you can:

1. Open Claude for Desktop
2. Click on the MCP server icon in the sidebar
3. Select "agent-orchestrator" from the list of available servers
4. Start interacting with the orchestration system

Claude will be able to:
- Transition between different agent states
- Store and retrieve information from the knowledge base
- Maintain conversation context across state transitions
- Access state-specific prompts

## Agent States

The orchestration system implements a state machine with the following states:

- **IDLE**: Waiting for instructions
- **PLANNING**: Creating a structured plan for a task
- **RESEARCHING**: Gathering information needed for a task
- **EXECUTING**: Carrying out planned actions
- **REVIEWING**: Evaluating results and determining next steps
- **ERROR**: Handling errors or unexpected situations

## Customizing the System

### Adding New States

1. Add the state to the `AgentState` enum in `orchestrator.py`
2. Create a prompt function for the new state
3. Update the transition logic in `_get_available_transitions()`
4. Add handlers for the new state in resource access functions

### Creating Custom Tools

Add new tools by creating functions decorated with `@mcp.tool()`:

```python
@mcp.tool()
def my_custom_tool(arg1: str, arg2: int, ctx: Context) -> str:
    """Description of what this tool does
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
    """
    # Implementation here
    return "Result"
```

## Development and Testing

### Using the MCP CLI

The MCP CLI provides tools for development and testing:

```bash
# Install MCP CLI if you haven't already
pip install "mcp[cli]"

# Test your server with the MCP Inspector
mcp dev orchestrator.py

# Install in Claude Desktop
mcp install orchestrator.py
```

### Manual Testing with Python

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(StdioServerParameters(command="python", args=["orchestrator.py"])) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # Test state transitions
        await session.call_tool("transition_state", arguments={"new_state": "PLANNING"})
```

## Resources

- [MCP Python SDK Documentation](https://github.com/anthropics/anthropic-mcp)
- [Model Context Protocol Specification](https://github.com/anthropics/anthropic-mcp/blob/main/README.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 