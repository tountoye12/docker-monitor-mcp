
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

            init_result = await session.initialize()

            print("Server information:")
            print(init_result.serverInfo)

            tools_result = await session.list_tools()

            print("\nRaw tools response:")
            print(tools_result)

            print("\nResponse type:")
            print(type(tools_result))

            print("\nAvailable tools:")
            for tool in tools_result.tools:
                print(f"Tool: {tool.name}")
                print(f"Description: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())