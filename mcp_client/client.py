
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio


server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", "-m", "mcp_server.server"]
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover available tools
            tools = await session.list_tools()

            print("Available MCP tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description.strip()}")

            # Execute a tool
            result = await session.call_tool(
                "list_containers",
                arguments={"include_stopped": True}
            )

            print("\nTool execution result:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())