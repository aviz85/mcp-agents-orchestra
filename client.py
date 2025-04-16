import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Configure connection to our server
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    # Connect to the server via stdio
    async with stdio_client(server_params) as (read, write):
        # Create a client session
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("Connected to MCP server")

            # --- Explore server capabilities ---
            
            # List available resources
            print("\n--- Available Resources ---")
            resources = await session.list_resources()
            for resource in resources:
                print(f"- {resource.name}: {resource.description}")

            # List available tools
            print("\n--- Available Tools ---")
            tools = await session.list_tools()
            for tool in tools:
                print(f"- {tool.name}: {tool.description}")

            # List available prompts
            print("\n--- Available Prompts ---")
            prompts = await session.list_prompts()
            for prompt in prompts:
                print(f"- {prompt.name}: {prompt.description}")

            # --- Use server capabilities ---
            
            # Read a resource
            print("\n--- Reading Resources ---")
            content, mime_type = await session.read_resource("docs://overview")
            print(f"Resource content: {content}")
            print(f"Mime type: {mime_type}")

            # Call a tool
            print("\n--- Calling Tools ---")
            result = await session.call_tool("add_numbers", arguments={"a": 5, "b": 7})
            print(f"Tool result: {result}")

            # Get a prompt
            print("\n--- Getting Prompts ---")
            prompt = await session.get_prompt("analyze_text", arguments={"text": "MCP is awesome!"})
            print(f"Prompt: {prompt}")


if __name__ == "__main__":
    asyncio.run(main()) 