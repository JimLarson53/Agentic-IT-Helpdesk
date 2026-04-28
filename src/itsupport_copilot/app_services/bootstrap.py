"""Application bootstrap and service container."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path

from itsupport_copilot.agents.graph import SupportAgentRunner
from itsupport_copilot.app_services.approval_service import ApprovalService
from itsupport_copilot.app_services.audit_service import AuditService
from itsupport_copilot.app_services.document_service import DocumentService
from itsupport_copilot.app_services.kb_service import KBService
from itsupport_copilot.rag import HashingEmbeddingModel, LocalVectorStore, Retriever
from itsupport_copilot.rag.loaders import load_documents_from_directory
from itsupport_copilot.storage import SQLiteRepository


@dataclass
class AppContainer:
    project_root: Path
    sample_docs_path: Path
    retriever: Retriever
    audit_service: AuditService
    approval_service: ApprovalService
    document_service: DocumentService
    kb_service: KBService
    runner: SupportAgentRunner
    initial_chunks: int

    def status(self) -> dict[str, object]:
        return {
            "status": "ok",
            "version": "0.1.0",
            "execution_enabled": False,
            "llm_mode": "deterministic",
            "embedding_mode": "hashing",
            "vector_store_status": "ready",
            "indexed_chunks": self.retriever.vector_store.count,
            "initial_chunks": self.initial_chunks,
            "database_status": "sqlite_local",
            "audit_storage": "sqlite",
            "approval_storage": "sqlite",
            "fastapi_installed": find_spec("fastapi") is not None,
            "streamlit_installed": find_spec("streamlit") is not None,
            "langgraph_installed": find_spec("langgraph") is not None,
            "sample_docs_loaded": self.sample_docs_path.exists(),
            "document_ingestion_scope": "project_root_only",
        }


def create_app_container(project_root: str | Path | None = None) -> AppContainer:
    root = Path(project_root) if project_root else Path(__file__).resolve().parents[3]
    sample_docs_path = root / "sample_data" / "docs"
    sqlite_store = SQLiteRepository(root / "data" / "app.sqlite3")

    audit_service = AuditService(store=sqlite_store)
    approval_service = ApprovalService(audit_service, store=sqlite_store)
    retriever = Retriever(
        embedding_model=HashingEmbeddingModel(dimensions=256),
        vector_store=LocalVectorStore(),
    )
    initial_chunks = 0
    if sample_docs_path.exists():
        documents = load_documents_from_directory(sample_docs_path)
        initial_chunks = len(retriever.ingest_documents(documents))

    document_service = DocumentService(
        retriever=retriever,
        audit_service=audit_service,
        allowed_root=root,
    )
    kb_service = KBService()
    runner = SupportAgentRunner(
        retriever=retriever,
        audit_service=audit_service,
        approval_service=approval_service,
    )
    return AppContainer(
        project_root=root,
        sample_docs_path=sample_docs_path,
        retriever=retriever,
        audit_service=audit_service,
        approval_service=approval_service,
        document_service=document_service,
        kb_service=kb_service,
        runner=runner,
        initial_chunks=initial_chunks,
    )
