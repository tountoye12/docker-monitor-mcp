import docker
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Docker Monitor", "docker-monitor-mcp", "0.1.0")

client = docker.from_env()


@mcp.tool()
def list_containers():
    """
    List all running Docker containers.
    """
    list_of_containers = client.containers.list()
    return [container.name for container in list_of_containers]


print("Docker Monitor MCP is running...")
print(list_containers())

if __name__ == "__main__":
    mcp.run(transport="stdio")