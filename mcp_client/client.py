
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from config.settings import MCP_SERVER_URL

async def main():
    async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover available tools
            tools = await session.list_tools()

            print("Available MCP tools:")

            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Execute a tool
            result = await session.call_tool(
                "list_containers",
                arguments={"include_stopped": True}
            )

            print("\nTool execution result:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())