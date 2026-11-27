
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

            print("\nAvailable MCP tools:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Select a tool
            tool_name = input("\nEnter tool name: ").strip()

            arguments = {}

            if tool_name == "list_containers":
                arguments["include_stopped"] = True

            elif tool_name in [
                "get_container_logs",
                "check_container_health",
                "get_container_stats",
                "detect_errors"
            ]:
                arguments["container_name"] = input(
                    "Container name: "
                ).strip()

            else:
                print("Unknown tool.")
                return

            # Execute selected tool
            result = await session.call_tool(
                tool_name,
                arguments=arguments
            )

            # Display formatted JSON response
            print("\nTool execution result:")
            print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())