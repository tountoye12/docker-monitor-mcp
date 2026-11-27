import docker
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = docker.from_env()

def list_containers(include_stopped: bool = True) -> list[dict]:
    """
    List all running Docker containers.
    """
    list_of_containers = client.containers.list(all=include_stopped)
    return [
        
        { 

        "id": container.short_id,
        "name": container.name,
        "status": container.status,
        "image": container.attrs.get("Config", {}).get("Image", "unknown")
         
        } for container in list_of_containers    
    ]