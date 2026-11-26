import docker
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Docker Monitor", "docker-monitor-mcp", "0.1.0")

client = docker.from_env()