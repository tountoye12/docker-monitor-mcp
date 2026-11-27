from config.thresholds import (
CPU_WARNING,
CPU_CRITICAL,
MEMORY_WARNING,
MEMORY_CRITICAL,
RESTART_WARNING,
RESTART_CRITICAL,
ERROR_WARNING,
ERROR_CRITICAL,
)

def evaluate_threshold(
    value: float,
    warning: float,
    critical: float
) -> str:
    """
    Evaluate a metric against warning and critical thresholds.
    """

    if value >= critical:
        return "critical"

    elif value >= warning:
        return "warning"

    return "normal"

def evaluate_cpu(cpu_percent: float) -> str:
    return evaluate_threshold(
        cpu_percent, CPU_WARNING, CPU_CRITICAL
    )


def evaluate_memory(memory_percent: float) -> str:
    return evaluate_threshold(
        memory_percent, MEMORY_WARNING, MEMORY_CRITICAL
    )


def evaluate_restarts(restart_increase: int) -> str:
    return evaluate_threshold(
        restart_increase, RESTART_WARNING, RESTART_CRITICAL
    )


def evaluate_errors(error_count: int) -> str:

    return evaluate_threshold(
        error_count, ERROR_WARNING, ERROR_CRITICAL
    )

def evaluate_status(status: str) -> str:
    """
    Evaluate the operational status of an expected running container.
    """
    status = status.lower()

    if status == "running":
        return "normal"

    if status in {"restarting", "paused", "created"}:
        return "warning"

    if status in {"exited", "dead", "removing"}:
        return "critical"

    return "unknown"

def evaluate_health(health: str) -> str:
    """
    Evaluate the Docker container health check status.
    """
    health = health.lower()

    if health == "healthy":
        return "normal"

    if health == "starting":
        return "warning"

    if health == "unhealthy":
        return "critical"

    return "unknown"