import docker
from mcp.server.fastmcp import FastMCP

import logging

mcp = FastMCP("Docker Monitor", "docker-monitor-mcp", "0.1.0")

client = docker.from_env()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool()
def list_containers():
    """
    List all running Docker containers.
    """
    list_of_containers = client.containers.list()
    return [container.name for container in list_of_containers]




if __name__ == "__main__":
    logger.info("Starting Docker Monitor MCP server...")
    mcp.run(transport="stdio")