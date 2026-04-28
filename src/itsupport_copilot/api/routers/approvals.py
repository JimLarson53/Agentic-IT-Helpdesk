"""Approval endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from itsupport_copilot.api.dependencies import get_container
from itsupport_copilot.app_services.bootstrap import AppContainer
from itsupport_copilot.schemas.approvals import ApprovalDecision, ApprovalRecord

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/{approval_id}", response_model=ApprovalRecord)
def get_approval(
    approval_id: str,
    request: Request,
    container: AppContainer = Depends(get_container),
) -> ApprovalRecord:
    del request
    try:
        return container.approval_service.get(approval_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Approval record not found") from exc


@router.post("/{approval_id}/decision", response_model=ApprovalRecord)
def decide_approval(
    approval_id: str,
    decision: ApprovalDecision,
    request: Request,
    container: AppContainer = Depends(get_container),
) -> ApprovalRecord:
    del request
    try:
        return container.approval_service.decide(approval_id, decision)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Approval record not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
