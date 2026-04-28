"""Command suggestion tool for safe IT diagnostics."""

from __future__ import annotations

from uuid import uuid4

from itsupport_copilot.safety.command_safety import check_command_safety
from itsupport_copilot.schemas.commands import CommandSuggestion, ShellType
from itsupport_copilot.schemas.tickets import Classification, Platform, TicketInput


def suggest_commands(ticket: TicketInput, classification: Classification) -> list[CommandSuggestion]:
    """Suggest diagnostic commands only when useful."""

    commands: list[CommandSuggestion] = []
    text = f"{ticket.title} {ticket.description} {ticket.environment or ''}".lower()

    if _contains_unsafe_command_request(text):
        commands.append(
            _make_suggestion(
                shell=ShellType.BASH,
                target_os="linux",
                intent="Blocked unsafe destructive command requested by ticket.",
                command="rm -rf /",
                explanation="This request is destructive and cannot be recommended.",
                expected_output="No command should be run.",
                rollback_or_recovery="Escalate to an administrator and preserve evidence.",
            )
        )
        return commands

    if classification.platform in {Platform.WINDOWS, Platform.NETWORK} and (
        "vpn" in text or "error 809" in text
    ):
        commands.append(
            _make_suggestion(
                shell=ShellType.POWERSHELL,
                target_os="windows",
                intent="Check whether the approved VPN hostname resolves in DNS.",
                command="Resolve-DnsName vpn.example.test",
                explanation="Read-only DNS lookup for the VPN gateway referenced by the KB.",
                expected_output="DNS response with one or more address records, or a resolution failure.",
                rollback_or_recovery="No rollback required because the command is read-only.",
            )
        )
        commands.append(
            _make_suggestion(
                shell=ShellType.POWERSHELL,
                target_os="windows",
                intent="Review recent VPN client errors from the Windows RasClient log.",
                command="Get-WinEvent -LogName Application -MaxEvents 20 | Where-Object {$_.ProviderName -like '*RasClient*'}",
                explanation="Collects recent local VPN error events for human review.",
                expected_output="Recent RasClient events or no matching entries.",
                rollback_or_recovery="Treat event output as potentially sensitive diagnostic data.",
            )
        )

    if classification.platform == Platform.LINUX and ("disk" in text or "space" in text):
        commands.append(
            _make_suggestion(
                shell=ShellType.BASH,
                target_os="linux",
                intent="Inspect filesystem usage.",
                command="df -h",
                explanation="Read-only filesystem usage check.",
                expected_output="Mounted filesystems with size, used, available, and percent-used columns.",
                rollback_or_recovery="No rollback required because the command is read-only.",
            )
        )
        commands.append(
            _make_suggestion(
                shell=ShellType.BASH,
                target_os="linux",
                intent="Inspect journald disk usage.",
                command="journalctl --disk-usage",
                explanation="Read-only journal size check.",
                expected_output="Total journal disk usage.",
                rollback_or_recovery="No rollback required because the command is read-only.",
            )
        )

    return commands


def _make_suggestion(
    *,
    shell: ShellType,
    target_os: str,
    intent: str,
    command: str,
    explanation: str,
    expected_output: str,
    rollback_or_recovery: str,
) -> CommandSuggestion:
    safety = check_command_safety(
        shell=shell,
        target_os=target_os,
        command=command,
        intent=intent,
    )
    return CommandSuggestion(
        command_id=f"cmd_{uuid4().hex[:12]}",
        shell=shell,
        target_os=target_os,
        intent=intent,
        command=command,
        risk_level=safety.risk_level,
        explanation=explanation,
        expected_output=expected_output,
        rollback_or_recovery=rollback_or_recovery,
        requires_human_approval=safety.requires_human_approval,
        blocked_reason="; ".join(finding.message for finding in safety.findings)
        if safety.blocked
        else None,
    )


def _contains_unsafe_command_request(text: str) -> bool:
    return any(
        marker in text
        for marker in (
            "rm -rf /",
            "remove-item -recurse -force c:\\",
            "disable defender",
            "dump passwords",
            "mimikatz",
        )
    )
