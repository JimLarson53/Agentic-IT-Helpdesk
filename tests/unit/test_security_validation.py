from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from itsupport_copilot.app_services.bootstrap import create_app_container
from itsupport_copilot.schemas.documents import DocumentIngestionRequest
from itsupport_copilot.schemas.tickets import TicketInput, Urgency


REPO_ROOT = Path(__file__).resolve().parents[2]


class SecurityValidationTests(unittest.TestCase):
    def test_document_ingestion_rejects_paths_outside_project_root(self) -> None:
        container = create_app_container(REPO_ROOT)
        payload = DocumentIngestionRequest(paths=[str(REPO_ROOT.parent / "outside.md")])

        result = container.document_service.ingest_paths(payload.paths)

        self.assertEqual(result.documents_processed, 0)
        self.assertEqual(result.chunks_created, 0)
        self.assertTrue(any("outside configured project root" in warning for warning in result.warnings))

    def test_status_does_not_expose_absolute_sample_docs_path(self) -> None:
        container = create_app_container(REPO_ROOT)
        status = container.status()

        self.assertNotIn("sample_docs_path", status)
        self.assertEqual(status["document_ingestion_scope"], "project_root_only")

    def test_workflow_model_dump_excludes_raw_ticket_and_full_chunks(self) -> None:
        container = create_app_container(REPO_ROOT)
        response = container.runner.run(
            TicketInput(
                title="Password reset issue",
                description="User pasted password=Summer2026! and needs an MFA reset.",
                affected_user="synthetic.user@example.test",
                environment="Identity support",
                urgency=Urgency.MEDIUM,
            )
        )

        payload = response.model_dump(mode="json")
        serialized = response.model_dump_json()

        self.assertNotIn("ticket", payload)
        self.assertNotIn("Summer2026", serialized)
        self.assertNotIn("source_path", serialized)
        self.assertNotIn('"chunk"', serialized)

    @unittest.skipUnless(
        importlib.util.find_spec("fastapi") is not None
        and importlib.util.find_spec("httpx") is not None,
        "FastAPI/httpx are not installed in the local bundled runtime.",
    )
    def test_fastapi_analyze_response_does_not_echo_raw_ticket_or_chunks(self) -> None:
        from fastapi.testclient import TestClient

        from itsupport_copilot.api.app import create_app

        client = TestClient(create_app(REPO_ROOT))
        response = client.post(
            "/api/v1/tickets/analyze",
            json={
                "title": "Password reset issue",
                "description": "User pasted password=Summer2026! and needs an MFA reset.",
                "affected_user": "synthetic.user@example.test",
                "environment": "Identity support",
                "urgency": "medium",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.text
        self.assertNotIn('"ticket"', body)
        self.assertNotIn("Summer2026", body)
        self.assertNotIn("source_path", body)
        self.assertNotIn('"chunk"', body)


if __name__ == "__main__":
    unittest.main()
