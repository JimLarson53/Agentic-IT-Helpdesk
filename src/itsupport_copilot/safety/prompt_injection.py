"""Prompt-injection heuristics for untrusted tickets and retrieved content."""

from __future__ import annotations

import re


_PROMPT_INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ignore_instructions", re.compile(r"\b(ignore|override|forget)\b.{0,40}\b(instructions?|rules?|policy|policies|previous)\b", re.I)),
    ("system_prompt_request", re.compile(r"\b(system|developer)\s+(prompt|message|instructions?)\b", re.I)),
    ("secret_request", re.compile(r"\b(reveal|print|show|dump|exfiltrate)\b.{0,50}\b(secret|token|api\s*key|password|credential)", re.I)),
    ("safety_bypass", re.compile(r"\b(disable|bypass|turn\s*off)\b.{0,40}\b(safety|guardrail|approval|policy|filter)", re.I)),
    ("auto_approve", re.compile(r"\b(approve|authorize)\b.{0,40}\b(action|command|tool|execution)\b", re.I)),
    ("tool_execution", re.compile(r"\b(run|execute|invoke)\b.{0,40}\b(shell|powershell|bash|command|tool)\b", re.I)),
    ("citation_suppression", re.compile(r"\b(do\s+not|don't)\b.{0,30}\b(cite|mention|disclose)\b.{0,30}\b(source|document|evidence)", re.I)),
    ("jailbreak_marker", re.compile(r"\b(jailbreak|developer\s+mode|dan\s+mode|unrestricted\s+mode)\b", re.I)),
]


def detect_prompt_injection(text: str) -> list[str]:
    """Return prompt-injection flag names found in untrusted text."""

    if not text:
        return []
    flags: list[str] = []
    for name, pattern in _PROMPT_INJECTION_PATTERNS:
        if pattern.search(text):
            flags.append(name)
    return flags


def has_prompt_injection(text: str) -> bool:
    """Return whether text contains prompt-injection indicators."""

    return bool(detect_prompt_injection(text))
