import re

ERROR_LEVELS = {"ERR", "ERROR", "FATAL", "CRITICAL"}
WARNING_LEVELS = {"WRN", "WARN", "WARNING"}
INFO_LEVELS = {"INF", "INFO", "DEBUG", "TRACE"}

SEVERITY_PATTERN = re.compile(
    r"^\s*(?:\d{4}[-/]\d{2}[-/]\d{2}\s+\S+\s+)?"
    r"\[?(ERR|ERROR|FATAL|CRITICAL|WRN|WARN|WARNING|INF|INFO|DEBUG|TRACE)\b\]?",
    re.IGNORECASE
)

ERROR_PATTERN = re.compile(
    r"\b(error|fatal|critical|exception|timed out|"
    r"connection refused|connection failed|"
    r"out of memory|permission denied)\b",
    re.IGNORECASE
)

WARNING_PATTERN = re.compile(
    r"\b(warning|warn)\b",
    re.IGNORECASE
)

def classify_log(line: str) -> str:
    """
    Classify a log entry using severity levels
    and fallback keyword detection.
    """
    match = SEVERITY_PATTERN.search(line)

    if match:
        severity = match.group(1).upper()

        if severity in ERROR_LEVELS:
            return "error"

        if severity in WARNING_LEVELS:
            return "warning"

        if severity in INFO_LEVELS:
            return "info"

    # Fallback keyword detection
    if ERROR_PATTERN.search(line):
        return "error"

    if WARNING_PATTERN.search(line):
        return "warning"

    return "unknown"