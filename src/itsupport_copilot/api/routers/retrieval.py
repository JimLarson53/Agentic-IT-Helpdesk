"""Retrieval endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from itsupport_copilot.api.dependencies import get_container
from itsupport_copilot.app_services.bootstrap import AppContainer
from itsupport_copilot.schemas.retrieval import RetrievalSearchRequest
from itsupport_copilot.schemas.rag import DocumentType, RetrievalResponse

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("/search", response_model=RetrievalResponse)
def search(
    payload: RetrievalSearchRequest,
    request: Request,
    container: AppContainer = Depends(get_container),
) -> RetrievalResponse:
    del request
    document_types = {DocumentType(item) for item in payload.document_types} if payload.document_types else None
    return container.retriever.retrieve(
        payload.query,
        document_types=document_types,
        top_k=payload.top_k,
        min_score=payload.min_score,
    )
