from mcp.server.fastmcp import FASTMCP
import docker


mcp = FASTMCP("Docker Monitor", "docker-monitor-mcp", "0.1.0")

client = docker.from_env()