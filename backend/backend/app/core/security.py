"""OAuth2 helpers and input sanitization."""

import html
import re
from typing import Any


def sanitize_input(value: str, max_length: int = 5000) -> str:
    """Strip dangerous characters and limit length."""
    cleaned = html.escape(value.strip())
    return cleaned[:max_length]


def validate_email(email: str) -> bool:
    """Basic email format validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def mask_pii(data: dict[str, Any]) -> dict[str, Any]:
    """Mask PII fields for demo/sandbox logging."""
    sensitive_keys = {"email", "password", "token", "secret", "api_key"}
    masked = {}
    for key, value in data.items():
        if any(s in key.lower() for s in sensitive_keys):
            masked[key] = "***REDACTED***"
        elif isinstance(value, dict):
            masked[key] = mask_pii(value)
        else:
            masked[key] = value
    return masked
