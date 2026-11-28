import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from config.settings import MCP_SERVER_URL
from mcp_client.arguments import collect_arguments


async def main():
    async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover available MCP tools
            tools = await session.list_tools()

            available_tools = {
                tool.name: tool
                for tool in tools.tools
            }

            print("\nAvailable MCP tools:")

            for tool in available_tools.values():
                print(f"- {tool.name}: {tool.description}")

            # Select a tool
            tool_name = input("\nEnter tool name: ").strip()

            selected_tool = available_tools.get(tool_name)

            if selected_tool is None:
                print("Unknown tool.")
                return

            # Dynamically collect arguments
            arguments = collect_arguments(
                selected_tool.inputSchema
            )

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