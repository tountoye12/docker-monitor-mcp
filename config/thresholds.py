import os


# CPU utilization thresholds (%)
CPU_WARNING = float(os.getenv("CPU_WARNING", "80"))
CPU_CRITICAL = float(os.getenv("CPU_CRITICAL", "95"))

# Memory utilization thresholds (%)
MEMORY_WARNING = float(os.getenv("MEMORY_WARNING", "80"))
MEMORY_CRITICAL = float(os.getenv("MEMORY_CRITICAL", "90"))

# Restart count increase thresholds
RESTART_WARNING = int(os.getenv("RESTART_WARNING", "3"))
RESTART_CRITICAL = int(os.getenv("RESTART_CRITICAL", "5"))

# Log error thresholds
ERROR_WARNING = int(os.getenv("ERROR_WARNING", "1"))
ERROR_CRITICAL = int(os.getenv("ERROR_CRITICAL", "5"))

# Monitoring interval (seconds)
MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", "60"))

def validate_thresholds() -> None:
    """
    Validate monitoring threshold configuration.
    """

    if not 0 < CPU_WARNING < CPU_CRITICAL:
        raise ValueError("Invalid CPU thresholds.")

    if not 0 < MEMORY_WARNING < MEMORY_CRITICAL <= 100:
        raise ValueError("Invalid memory thresholds.")

    if not 0 < RESTART_WARNING < RESTART_CRITICAL:
        raise ValueError("Invalid restart thresholds.")

    if not 0 < ERROR_WARNING < ERROR_CRITICAL:
        raise ValueError("Invalid log error thresholds.")

    if MONITORING_INTERVAL <= 0:
        raise ValueError("Monitoring interval must be positive.")