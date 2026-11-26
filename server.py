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

@mcp.tool()
def get_container_logs(container_name:str, lines: int = 50) -> str:

    """
    Get logs of a specific Docker container.
    """
    if not 1 < lines <= 1000:
        return "Please specify a number of lines between 1 and 1000."
    try:
        container = client.containers.get(container_name)
        logs = container.logs(tail=lines)
        return logs.decode("utf-8")
    except docker.errors.NotFound:
        return f"Container '{container_name}' not found."
    except docker.errors.APIError as e:
        logger.error(f"Error fetching logs for container '{container_name}': {e}")
        return  "Failed to retrieve container logs."
    




if __name__ == "__main__":
    logger.info("Starting Docker Monitor MCP server...")
    mcp.run(transport="stdio")