
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
            tools = await session.initialize()
            for tool in tools.tools:
                print(f"Tool: {tool.name}")
                print(f"Description: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())