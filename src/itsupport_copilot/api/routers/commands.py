"""Command safety endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from itsupport_copilot.safety.command_safety import check_command_safety
from itsupport_copilot.schemas.commands import CommandCheckRequest, CommandSafetyResult

router = APIRouter(prefix="/commands", tags=["commands"])


@router.post("/check", response_model=CommandSafetyResult)
def check_command(payload: CommandCheckRequest) -> CommandSafetyResult:
    return check_command_safety(
        shell=payload.shell,
        target_os=payload.target_os,
        command=payload.command,
        intent=payload.intent,
    )
