import docker
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Docker Monitor", "docker-monitor-mcp", "0.1.0")

client = docker.from_env()


@mcp.tool()
def list_containers():
    """
    List all running Docker containers.
    """
    return "Docker Monitoring is working"