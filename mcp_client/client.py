import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from config.settings import MCP_SERVER_URL
from mcp_client.arguments import collect_arguments


async def main():
    async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()

            available_tools = {
                tool.name: tool
                for tool in tools.tools
            }

            print("\nConnected to MCP server.")

            while True:

                print("\nAvailable MCP tools:")

                for tool in available_tools.values():
                    print(f"- {tool.name}")

                print("\nType 'exit' to close the session.")

                tool_name = input(
                    "\nEnter tool name: "
                ).strip()

                if tool_name.lower() == "exit":
                    print("Closing MCP session.")
                    break

                selected_tool = available_tools.get(tool_name)

                if selected_tool is None:
                    print("Unknown tool.")
                    continue

                try:
                    arguments = collect_arguments(
                        selected_tool.inputSchema
                    )

                    result = await session.call_tool(
                        tool_name,
                        arguments=arguments
                    )

                    print("\nTool execution result:")
                    print(result.model_dump_json(indent=2))

                except Exception as error:
                    print(f"Tool execution failed: {error}")


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except (KeyboardInterrupt, EOFError):
        print("\nMCP client stopped.")