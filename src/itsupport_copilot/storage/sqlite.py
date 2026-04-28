"""SQLite persistence for audit events and approval records."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from itsupport_copilot.schemas.approvals import ApprovalRecord
from itsupport_copilot.schemas.audit import AuditEvent


class SQLiteRepository:
    """Small SQLite repository for local development audit metadata."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def upsert_audit_event(self, event: AuditEvent) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                INSERT OR REPLACE INTO audit_events (
                    event_id, run_id, event_type, actor, created_at, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.run_id,
                    event.event_type,
                    event.actor,
                    event.created_at.isoformat(),
                    event.model_dump_json(),
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def list_audit_events(self, *, run_id: str | None = None) -> list[AuditEvent]:
        query = "SELECT payload_json FROM audit_events"
        params: tuple[str, ...] = ()
        if run_id is not None:
            query += " WHERE run_id = ?"
            params = (run_id,)
        query += " ORDER BY created_at ASC, event_id ASC"

        connection = self._connect()
        try:
            rows = connection.execute(query, params).fetchall()
        finally:
            connection.close()
        return [AuditEvent.model_validate_json(row[0]) for row in rows]

    def upsert_approval_record(self, record: ApprovalRecord) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                INSERT OR REPLACE INTO approval_records (
                    approval_id, run_id, approval_status, risk_level, created_at, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.approval_id,
                    record.run_id,
                    record.approval_status.value,
                    record.risk_level.value,
                    record.created_at.isoformat(),
                    record.model_dump_json(),
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def get_approval_record(self, approval_id: str) -> ApprovalRecord:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT payload_json FROM approval_records WHERE approval_id = ?",
                (approval_id,),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            raise KeyError(approval_id)
        return ApprovalRecord.model_validate_json(row[0])

    def list_approval_records(self, *, run_id: str) -> list[ApprovalRecord]:
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM approval_records
                WHERE run_id = ?
                ORDER BY created_at ASC, approval_id ASC
                """,
                (run_id,),
            ).fetchall()
        finally:
            connection.close()
        return [ApprovalRecord.model_validate_json(row[0]) for row in rows]

    def _init_schema(self) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_events_run_id ON audit_events(run_id)"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS approval_records (
                    approval_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    approval_status TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_approval_records_run_id ON approval_records(run_id)"
            )
            connection.commit()
        finally:
            connection.close()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)
