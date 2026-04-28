from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from itsupport_copilot.app_services.bootstrap import create_app_container
from itsupport_copilot.schemas.approvals import ApprovalDecision, ApprovalStatus
from itsupport_copilot.schemas.commands import CommandCheckRequest, RiskLevel, ShellType
from itsupport_copilot.schemas.documents import DocumentIngestionRequest
from itsupport_copilot.schemas.retrieval import RetrievalSearchRequest
from itsupport_copilot.schemas.tickets import TicketInput, Urgency


REPO_ROOT = Path(__file__).resolve().parents[2]


class Phase5IntegrationTests(unittest.TestCase):
    def test_container_bootstraps_sample_corpus_and_status(self) -> None:
        container = create_app_container(REPO_ROOT)

        status = container.status()

        self.assertEqual(status["status"], "ok")
        self.assertFalse(status["execution_enabled"])
        self.assertGreater(status["indexed_chunks"], 0)
        self.assertEqual(status["llm_mode"], "deterministic")

    def test_end_to_end_ticket_workflow_supports_approval_decision(self) -> None:
        container = create_app_container(REPO_ROOT)
        response = container.runner.run(
            TicketInput(
                title="VPN error 809",
                description="Windows user receives VPN error 809 when connecting to vpn.example.test.",
                affected_user="synthetic.user@example.test",
                affected_system="Windows laptop",
                environment="Windows 11 remote access VPN",
                urgency=Urgency.MEDIUM,
                attempted_fixes="User restarted the VPN client.",
                generate_kb_draft=True,
            )
        )

        self.assertTrue(response.final_answer.citations)
        self.assertTrue(response.command_suggestions)
        self.assertTrue(response.approval_records)

        record = response.approval_records[0]
        updated = container.approval_service.decide(
            record.approval_id,
            ApprovalDecision(
                decision=ApprovalStatus.REJECTED,
                approving_human="Integration Tester",
                comment="Rejected during Phase 5 integration test.",
            ),
        )

        self.assertEqual(updated.approval_status, ApprovalStatus.REJECTED)
        self.assertEqual(updated.execution_status.value, "not_applicable")

    def test_retrieval_and_kb_generation_services_are_wired(self) -> None:
        container = create_app_container(REPO_ROOT)
        retrieval_payload = RetrievalSearchRequest(
            query="Windows VPN error 809 vpn.example.test",
            top_k=3,
        )

        retrieval = container.retriever.retrieve(
            retrieval_payload.query,
            top_k=retrieval_payload.top_k,
            min_score=retrieval_payload.min_score,
        )
        self.assertTrue(retrieval.assessment.sufficient)

        response = container.runner.run(
            TicketInput(
                title="VPN error 809",
                description="Windows user receives VPN error 809.",
                affected_system="Windows laptop",
                environment="Windows 11 remote access VPN",
                urgency=Urgency.MEDIUM,
                generate_kb_draft=True,
            )
        )
        article = container.kb_service.generate_from_workflow(response)

        self.assertTrue(article.title.startswith("KB Draft"))
        self.assertTrue(article.related_sources)

    def test_document_ingestion_service_accepts_local_paths(self) -> None:
        container = create_app_container(REPO_ROOT)
        payload = DocumentIngestionRequest(
            paths=[str(REPO_ROOT / "sample_data" / "docs" / "kb" / "windows-vpn-error-809.md")]
        )

        result = container.document_service.ingest_paths(payload.paths)

        self.assertEqual(result.documents_processed, 1)
        self.assertGreater(result.chunks_created, 0)
        self.assertFalse(result.warnings)

    def test_command_check_request_supports_safety_endpoint_contract(self) -> None:
        payload = CommandCheckRequest(
            shell=ShellType.POWERSHELL,
            target_os="windows",
            command="Resolve-DnsName vpn.example.test",
            intent="Check VPN hostname resolution.",
        )

        from itsupport_copilot.safety.command_safety import check_command_safety

        result = check_command_safety(
            shell=payload.shell,
            target_os=payload.target_os,
            command=payload.command,
            intent=payload.intent,
        )

        self.assertEqual(result.risk_level, RiskLevel.LOW)
        self.assertTrue(result.requires_human_approval)

    @unittest.skipUnless(
        importlib.util.find_spec("fastapi") is not None
        and importlib.util.find_spec("httpx") is not None,
        "FastAPI/httpx are not installed in the local bundled runtime.",
    )
    def test_fastapi_app_contract_when_dependencies_are_installed(self) -> None:
        from fastapi.testclient import TestClient

        from itsupport_copilot.api.app import create_app

        client = TestClient(create_app(REPO_ROOT))
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
