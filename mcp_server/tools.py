from mcp.server.fastmcp import FastMCP
from services import docker_service


def register_tools(mcp: FastMCP):

    @mcp.tool()
    def list_containers(include_stopped: bool = True) -> list[dict]:
        """
        List Docker containers, including stopped containers by default.
        """
        return docker_service.list_containers(include_stopped)