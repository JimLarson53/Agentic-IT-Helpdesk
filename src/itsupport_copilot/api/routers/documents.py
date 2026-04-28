"""Document ingestion endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from itsupport_copilot.api.dependencies import get_container
from itsupport_copilot.app_services.bootstrap import AppContainer
from itsupport_copilot.schemas.documents import DocumentIngestionRequest, DocumentIngestionResult

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/ingest", response_model=DocumentIngestionResult)
def ingest_documents(
    payload: DocumentIngestionRequest,
    request: Request,
    container: AppContainer = Depends(get_container),
) -> DocumentIngestionResult:
    del request
    return container.document_service.ingest_paths(payload.paths, sensitivity=payload.sensitivity, tags=payload.tags)
