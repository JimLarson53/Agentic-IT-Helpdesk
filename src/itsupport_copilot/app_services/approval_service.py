"""Human approval record service."""

from __future__ import annotations

from datetime import UTC, datetime

from itsupport_copilot.app_services.audit_service import AuditService
from itsupport_copilot.schemas.approvals import (
    ActionType,
    ApprovalDecision,
    ApprovalRecord,
    ApprovalStatus,
)
from itsupport_copilot.schemas.commands import CommandSuggestion, RiskLevel
from itsupport_copilot.storage import SQLiteRepository


class ApprovalService:
    """Create and decide approval records without executing actions."""

    def __init__(
        self,
        audit_service: AuditService | None = None,
        store: SQLiteRepository | None = None,
    ) -> None:
        self.audit_service = audit_service or AuditService()
        self.store = store
        self._records: dict[str, ApprovalRecord] = {}

    def create_for_command(self, *, run_id: str, command: CommandSuggestion) -> ApprovalRecord | None:
        if command.risk_level == RiskLevel.BLOCKED:
            self.audit_service.record(
                run_id=run_id,
                event_type="approval_not_created_for_blocked_command",
                summary=f"Blocked command was not made approvable: {command.intent}",
                metadata={"command_id": command.command_id, "risk_level": command.risk_level.value},
            )
            return None

        record = ApprovalRecord(
            run_id=run_id,
            proposed_action=command.command,
            action_type=ActionType.COMMAND,
            risk_level=command.risk_level,
            rationale=command.intent,
            affected_system_or_data=command.target_os,
            safety_findings=[command.blocked_reason] if command.blocked_reason else [],
        )
        self._records[record.approval_id] = record
        if self.store is not None:
            self.store.upsert_approval_record(record)
        self.audit_service.record(
            run_id=run_id,
            event_type="approval_created",
            summary=f"Approval record created for {command.risk_level.value} command.",
            metadata={"approval_id": record.approval_id, "command_id": command.command_id},
        )
        return record

    def decide(self, approval_id: str, decision: ApprovalDecision) -> ApprovalRecord:
        if decision.decision not in {ApprovalStatus.APPROVED, ApprovalStatus.REJECTED}:
            raise ValueError("Approval decision must be approved or rejected")
        record = self._records[approval_id]
        if record.approval_status != ApprovalStatus.PENDING:
            raise ValueError(f"Approval record is already {record.approval_status.value}")

        updated = record.model_copy(
            update={
                "approval_status": decision.decision,
                "approving_human": decision.approving_human,
                "decided_at": datetime.now(UTC),
            }
        )
        self._records[approval_id] = updated
        if self.store is not None:
            self.store.upsert_approval_record(updated)
        self.audit_service.record(
            run_id=updated.run_id,
            event_type="approval_decision",
            actor=decision.approving_human,
            summary=f"Approval {approval_id} marked {decision.decision.value}.",
            metadata={"approval_id": approval_id, "comment": decision.comment or ""},
        )
        return updated

    def get(self, approval_id: str) -> ApprovalRecord:
        if self.store is not None:
            return self.store.get_approval_record(approval_id)
        return self._records[approval_id]

    def list_for_run(self, run_id: str) -> list[ApprovalRecord]:
        if self.store is not None:
            return self.store.list_approval_records(run_id=run_id)
        return [record for record in self._records.values() if record.run_id == run_id]
