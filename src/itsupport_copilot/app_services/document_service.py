"""Document ingestion service."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from itsupport_copilot.app_services.audit_service import AuditService
from itsupport_copilot.rag import Retriever
from itsupport_copilot.rag.loaders import load_documents_from_directory, load_text_document
from itsupport_copilot.schemas.documents import DocumentIngestionResult
from itsupport_copilot.schemas.rag import Sensitivity


class DocumentService:
    """Ingest sanitized local documents into the shared retriever."""

    def __init__(
        self,
        *,
        retriever: Retriever,
        audit_service: AuditService,
        allowed_root: str | Path,
    ) -> None:
        self.retriever = retriever
        self.audit_service = audit_service
        self.allowed_root = Path(allowed_root).resolve()

    def ingest_paths(
        self,
        paths: list[str],
        *,
        sensitivity: Sensitivity = Sensitivity.INTERNAL,
        tags: list[str] | None = None,
    ) -> DocumentIngestionResult:
        ingestion_run_id = f"ingest_{uuid4().hex[:16]}"
        warnings: list[str] = []
        documents = []
        for raw_path in paths:
            path = self._resolve_allowed_path(raw_path)
            if path is None:
                warnings.append("Path rejected: outside configured project root")
                continue
            if not path.exists():
                warnings.append(f"Path not found: {path}")
                continue
            if path.is_dir():
                documents.extend(load_documents_from_directory(path, sensitivity=sensitivity, tags=tags))
            elif path.is_file():
                documents.append(load_text_document(path, sensitivity=sensitivity, tags=tags))
            else:
                warnings.append(f"Unsupported path type: {path}")

        chunks = self.retriever.ingest_documents(documents)
        self.audit_service.record(
            run_id=ingestion_run_id,
            event_type="documents_ingested",
            summary=f"Ingested {len(documents)} document(s) and {len(chunks)} chunk(s).",
            metadata={"documents_processed": len(documents), "chunks_created": len(chunks)},
        )
        return DocumentIngestionResult(
            ingestion_run_id=ingestion_run_id,
            documents_processed=len(documents),
            chunks_created=len(chunks),
            chunks_indexed=len(chunks),
            warnings=warnings,
        )

    def _resolve_allowed_path(self, raw_path: str) -> Path | None:
        path = Path(raw_path)
        if not path.is_absolute():
            path = self.allowed_root / path
        try:
            resolved = path.resolve()
            resolved.relative_to(self.allowed_root)
        except (OSError, ValueError):
            return None
        return resolved
