from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from itsupport_copilot.app_services.approval_service import ApprovalService
from itsupport_copilot.app_services.audit_service import AuditService
from itsupport_copilot.schemas.approvals import ApprovalDecision, ApprovalStatus
from itsupport_copilot.schemas.commands import CommandSuggestion, RiskLevel, ShellType
from itsupport_copilot.storage import SQLiteRepository


REPO_ROOT = Path(__file__).resolve().parents[2]


class SQLiteStorageTests(unittest.TestCase):
    def test_audit_and_approval_records_persist_to_sqlite(self) -> None:
        temp_root = REPO_ROOT / ".tmp-tests"
        temp_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as tmp:
            db_path = Path(tmp) / "audit.sqlite3"
            store = SQLiteRepository(db_path)
            audit_service = AuditService(store=store)
            approval_service = ApprovalService(audit_service, store=store)

            audit_service.record(
                run_id="run_release",
                event_type="release_check",
                summary="User pasted password=Summer2026!",
            )
            approval = approval_service.create_for_command(
                run_id="run_release",
                command=CommandSuggestion(
                    command_id="cmd_release_dns",
                    shell=ShellType.POWERSHELL,
                    target_os="windows",
                    intent="Resolve VPN DNS name.",
                    command="Resolve-DnsName vpn.example.test",
                    risk_level=RiskLevel.LOW,
                    explanation="Read-only DNS lookup.",
                    expected_output="DNS response records.",
                    rollback_or_recovery="No rollback required.",
                    requires_human_approval=True,
                ),
            )
            assert approval is not None
            approval_service.decide(
                approval.approval_id,
                ApprovalDecision(
                    decision=ApprovalStatus.APPROVED,
                    approving_human="Release Reviewer",
                    comment="Approved read-only diagnostic.",
                ),
            )

            reloaded = SQLiteRepository(db_path)
            events = reloaded.list_audit_events(run_id="run_release")
            approvals = reloaded.list_approval_records(run_id="run_release")

        self.assertTrue(any(event.event_type == "release_check" for event in events))
        self.assertNotIn("Summer2026", events[0].summary)
        self.assertEqual(len(approvals), 1)
        self.assertEqual(approvals[0].approval_status, ApprovalStatus.APPROVED)
        self.assertEqual(approvals[0].approving_human, "Release Reviewer")


if __name__ == "__main__":
    unittest.main()
