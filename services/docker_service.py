import docker
import logging
from security.sanitizer import sanitize_logs

from requests.exceptions import Timeout, ConnectionError
from utils.log_normalizer import normalize_logs
from utils.log_analyzer import classify_log


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


def get_container_logs(container_name: str, lines: int = 50) -> str:
    """
    Get sanitized logs of a specific Docker container.
    """
    if not 1 <= lines <= 1000:
        return "Please specify a number of lines between 1 and 1000."

    try:
        container = client.containers.get(container_name)
        logs = container.logs(tail=lines)

        #return sanitize_logs(logs.decode("utf-8", errors="replace"))
        decoded_logs = logs.decode("utf-8", errors="replace")
        normalized_logs = normalize_logs(decoded_logs)
        sanitized_logs = sanitize_logs(normalized_logs)

        return sanitized_logs

    except docker.errors.NotFound:
        return f"Container '{container_name}' not found."


    except Timeout as e:
        logger.error(
            f"Network error while fetching logs for container '{container_name}': {e}"
            )
        return "Network error occurred while retrieving container logs."


    except ConnectionError as e:
        logger.error(
            f"Connection error while fetching logs for container '{container_name}': {e}"
            )
        return "Connection error occurred while retrieving container logs."
    

    except docker.errors.APIError as e:
        logger.error(f"Error fetching logs for container '{container_name}': {e}")
        return "Failed to retrieve container logs."
    

def check_container_health(container_name: str) -> dict:
    """
    Check the health status of a specific Docker container.
    """
    try:
        container = client.containers.get(container_name)
        state = container.attrs.get("State", {})

        return {
            "name": container.name,
            "status": state.get("Status"),
            "health": state.get("Health", {}).get(
                "Status", "not_configured"
            ),
            "restart_count": container.attrs.get("RestartCount", 0),
            "oom_killed": state.get("OOMKilled"),
            "exit_code": state.get("ExitCode")
        }

    except docker.errors.NotFound:
        return {"error": f"Container '{container_name}' not found."}

    except docker.errors.APIError as e:
        logger.error("Error checking container health: %s", e)
        return {"error": "Failed to retrieve container health status."}


def get_container_stats(container_name: str) -> dict:
    """
    Get CPU, memory and network statistics of a Docker container.
    """
    try:
        container = client.containers.get(container_name)

        # Verify that the container is running
        if container.status != "running":
            return {
                "error": f"Container '{container_name}' is not running."
            }

        # Retrieve container statistics
        stats = container.stats(stream=False)

        # CPU statistics
        cpu_stats = stats.get("cpu_stats", {})
        precpu_stats = stats.get("precpu_stats", {})

        cpu_usage = cpu_stats.get("cpu_usage", {}).get("total_usage")
        prev_cpu_usage = precpu_stats.get("cpu_usage", {}).get("total_usage")

        system_usage = cpu_stats.get("system_cpu_usage")
        prev_system_usage = precpu_stats.get("system_cpu_usage")

        online_cpus = cpu_stats.get("online_cpus") or len(
            cpu_stats.get("cpu_usage", {}).get("percpu_usage") or []
        )

        # Calculate CPU utilization
        cpu_percent = None

        if None not in (
            cpu_usage, prev_cpu_usage,
            system_usage, prev_system_usage
        ):
            cpu_delta = cpu_usage - prev_cpu_usage
            system_delta = system_usage - prev_system_usage

            if system_delta > 0 and cpu_delta >= 0 and online_cpus > 0:
                cpu_percent = (
                    (cpu_delta / system_delta) * online_cpus * 100
                )

        # Memory statistics
        memory_stats = stats.get("memory_stats", {})
        memory_usage = memory_stats.get("usage")
        memory_limit = memory_stats.get("limit")

        # Calculate memory utilization
        memory_percent = (
            (memory_usage / memory_limit) * 100
            if memory_usage is not None and memory_limit and memory_limit > 0
            else None
        )

        # Return structured monitoring data
        return {
            "name": container.name,
            "status": container.status,

            "cpu_percent": round(cpu_percent, 2)
            if cpu_percent is not None else None,

            "memory_usage_mib": round(memory_usage / (1024 ** 2), 2)
            if memory_usage is not None else None,

            "memory_limit_mib": round(memory_limit / (1024 ** 2), 2)
            if memory_limit is not None else None,

            "memory_percent": round(memory_percent, 2)
            if memory_percent is not None else None,

            "network_io": stats.get("networks", {}),
        }

    except docker.errors.NotFound:
        return {"error": f"Container '{container_name}' not found."}

    except docker.errors.APIError as e:
        logger.error("Error fetching container stats: %s", e)
        return {"error": "Failed to retrieve container statistics."}



def detect_errors(container_name: str, lines: int = 100) -> dict:
    """
    Analyze recent Docker container logs for errors and warnings.
    """

    # Validate the number of requested lines
    if not 1 <= lines <= 1000:
        return {"error": "Lines must be between 1 and 1000."}

    try:
        # Retrieve container and logs
        container = client.containers.get(container_name)
        logs = container.logs(tail=lines).decode(
            "utf-8", errors="replace"
        )

        # Split logs into individual lines
        #log_lines = logs.splitlines()
        normalized_logs = normalize_logs(logs)
        log_lines = normalized_logs.splitlines()

        errors = []
        warnings = []

        # Analyze each log entry
        for line in log_lines:
            severity = classify_log(line)

            if severity == "error":
                errors.append(sanitize_logs(line))

            elif severity == "warning":
                warnings.append(sanitize_logs(line))

        # Return structured monitoring results
        return {
            "name": container.name,
            "total_lines_analyzed": len(log_lines),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
        }

    except docker.errors.NotFound:
        return {"error": f"Container '{container_name}' not found."}


    except Timeout as e:
        logger.error(
            f"Network error while analyzing logs for container '{container_name}': {e}"
        )
        return {"error": "Network error occurred while analyzing container logs."}

    except ConnectionError as e:
        logger.error(
            f"Connection error while analyzing logs for container '{container_name}': {e}"
        )
        return {"error": "Connection error occurred while analyzing container logs."}

    except docker.errors.APIError as e:
        logger.error("Error analyzing container logs: %s", e)
        return {"error": "Failed to analyze container logs."}