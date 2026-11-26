import docker
from mcp.server.fastmcp import FasTMCP

mcp = FasTMCP("Docker Monitor", "docker-monitor-mcp", "0.1.0")

client = docker.from_env()