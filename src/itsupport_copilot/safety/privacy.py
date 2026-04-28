"""Sensitive-pattern detection and redaction helpers."""

from __future__ import annotations

import re


_SENSITIVE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private_key", re.compile(r"-----BEGIN\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE\s+KEY-----", re.I)),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}\b", re.I)),
    ("api_key_assignment", re.compile(r"\b(api[_-]?key|token|secret|password)\s*[:=]\s*[^\s`'\"<>]{6,}", re.I)),
    ("connection_string", re.compile(r"\b(server|host|uid|user id|password|pwd)\s*=\s*[^;]+;.*", re.I)),
    ("ssn_like", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
]


def find_sensitive_patterns(text: str) -> list[str]:
    """Return names of secret or sensitive-data patterns found in text."""

    if not text:
        return []
    flags: list[str] = []
    for name, pattern in _SENSITIVE_PATTERNS:
        if pattern.search(text):
            flags.append(name)
    return flags


def redact_sensitive_text(text: str) -> str:
    """Redact common secret-like values while preserving enough context for review."""

    redacted = text
    for name, pattern in _SENSITIVE_PATTERNS:
        redacted = pattern.sub(f"[REDACTED:{name}]", redacted)
    return redacted
