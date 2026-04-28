"""Deterministic ticket summarization."""

from __future__ import annotations

import re

from itsupport_copilot.safety.privacy import redact_sensitive_text
from itsupport_copilot.schemas.tickets import Classification, TicketInput, TicketSummary


def summarize_ticket(ticket: TicketInput, classification: Classification) -> TicketSummary:
    """Summarize a ticket into required support fields."""

    symptoms = _extract_symptoms(ticket.description)
    attempted = _split_items(ticket.attempted_fixes or "")
    missing = _missing_information(ticket)
    affected = ticket.affected_system or ticket.affected_user or "Unknown affected user/system"

    if classification.escalation_recommended:
        next_action = "Escalate with collected impact, logs, and affected system details."
    elif classification.requires_command_suggestions:
        next_action = "Run approved read-only diagnostics, review cited sources, and confirm missing context."
    else:
        next_action = "Confirm identity/context, gather missing information, and follow the cited support guidance."

    return TicketSummary(
        issue_summary=redact_sensitive_text(_first_sentence(ticket.description) or ticket.title),
        affected_user_or_system=affected,
        symptoms=[redact_sensitive_text(symptom) for symptom in symptoms],
        attempted_fixes=[redact_sensitive_text(item) for item in attempted],
        likely_category=classification.category,
        severity=classification.severity,
        missing_information=missing,
        next_best_action=next_action,
    )


def _extract_symptoms(description: str) -> list[str]:
    candidates = _split_items(description)
    if candidates:
        return candidates[:5]
    return [_first_sentence(description)] if description.strip() else ["No symptoms provided."]


def _split_items(text: str) -> list[str]:
    parts = re.split(r"(?:\n+|;\s+|\.\s+)", text.strip())
    return [part.strip(" -\t") for part in parts if part.strip(" -\t")]


def _first_sentence(text: str) -> str:
    return _split_items(text)[0] if _split_items(text) else ""


def _missing_information(ticket: TicketInput) -> list[str]:
    missing: list[str] = []
    if not ticket.affected_user:
        missing.append("affected user")
    if not ticket.affected_system:
        missing.append("affected system or asset")
    if not ticket.environment:
        missing.append("environment")
    if not ticket.attempted_fixes:
        missing.append("attempted fixes")
    return missing
