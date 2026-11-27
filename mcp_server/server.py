import logging
from mcp.server.fastmcp import FastMCP
from mcp_server.tools import register_tools
from config.settings import MCP_HOST, MCP_PORT, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Docker Monitor",
    host=MCP_HOST,
    port=MCP_PORT
)

register_tools(mcp)

if __name__ == "__main__":
    logger.info("Docker Monitor MCP is starting...")
    mcp.run(transport="streamable-http")