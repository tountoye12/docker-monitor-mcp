import re

SENSITIVE_PATTERNS = [
    r"(?i)(password\s*[:=]\s*)\S+",
    r"(?i)(api_key\s*[:=]\s*)\S+",
    r"(?i)(token\s*[:=]\s*)\S+",
    r"(?i)(secret\s*[:=]\s*)\S+",
    r"(?i)(authorization\s*:\s*Bearer\s+)\S+",
]


def sanitize_log(logs: str) -> str:
    """
    Sanitize sensitive information from logs using predefined patterns.
    """
    sanitized_logs = logs
    for pattern in SENSITIVE_PATTERNS:
        sanitized_logs = re.sub(pattern, r"\1[REDACTED]", sanitized_logs)
    return sanitized_logs