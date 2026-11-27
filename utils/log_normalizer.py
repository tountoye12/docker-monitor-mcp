import re


ANSI_PATTERN = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def normalize_logs(logs: str) -> str:
    """
    Remove ANSI escape sequences from Docker logs.
    """
    normalized_log = ANSI_PATTERN.sub("", logs)

    return normalized_log