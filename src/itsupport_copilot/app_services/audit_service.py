"""Redacted audit logging service."""

from __future__ import annotations

from itsupport_copilot.safety.privacy import redact_sensitive_text
from itsupport_copilot.schemas.audit import AuditEvent
from itsupport_copilot.storage import SQLiteRepository


class AuditService:
    """Redacted audit service with optional SQLite persistence."""

    def __init__(self, store: SQLiteRepository | None = None) -> None:
        self.store = store
        self._events: list[AuditEvent] = []

    def record(
        self,
        *,
        run_id: str,
        event_type: str,
        summary: str,
        actor: str = "system",
        metadata: dict[str, object] | None = None,
    ) -> AuditEvent:
        redacted_metadata = _redact_metadata(metadata or {})
        event = AuditEvent(
            run_id=run_id,
            event_type=event_type,
            actor=actor,
            summary=redact_sensitive_text(summary),
            redacted_metadata=redacted_metadata,
        )
        self._events.append(event)
        if self.store is not None:
            self.store.upsert_audit_event(event)
        return event

    def list_events(self, *, run_id: str | None = None) -> list[AuditEvent]:
        if self.store is not None:
            return self.store.list_audit_events(run_id=run_id)
        if run_id is None:
            return list(self._events)
        return [event for event in self._events if event.run_id == run_id]


def _redact_metadata(metadata: dict[str, object]) -> dict[str, object]:
    redacted: dict[str, object] = {}
    for key, value in metadata.items():
        if isinstance(value, str):
            redacted[key] = redact_sensitive_text(value)
        else:
            redacted[key] = value
    return redacted
