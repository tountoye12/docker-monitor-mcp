from mcp.server.fastmcp import FastMCP
from services import docker_service


def register_tools(mcp: FastMCP):

    @mcp.tool()
    def list_containers(include_stopped: bool = True) -> list[dict]:
        """
        List Docker containers, including stopped containers by default.
        """
        return docker_service.list_containers(include_stopped)

    @mcp.tool()
    def get_container_logs(container_name: str, lines: int = 50) -> str:
        """
        Get logs of a specific Docker container.
        """
        return docker_service.get_container_logs(container_name, lines)
    
    @mcp.tool()
    def check_container_health(container_name: str) -> dict:
        """
        Check the health status of a specific Docker container.
        """
        return docker_service.check_container_health(container_name)

    @mcp.tool()
    def get_container_stats(container_name: str) -> dict:
        """
        Get CPU, memory, and network statistics of a specific Docker container.
        """
        return docker_service.get_container_stats(container_name)

    @mcp.tool()
    def detect_errors(container_name: str, lines: int = 100) -> dict:
        """
        Analyze recent logs of a Docker container for errors and warnings.
        """
        return docker_service.detect_errors(container_name, lines)