import logging
from mcp.server.fastmcp import FastMCP
from mcp_server.tools import register_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Docker Monitor",
    host="127.0.0.1",
    port=8001
)

register_tools(mcp)

if __name__ == "__main__":
    logger.info("Docker Monitor MCP is starting...")
    mcp.run(transport="streamable-http")