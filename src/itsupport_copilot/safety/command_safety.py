"""Deterministic command risk scoring."""

from __future__ import annotations

import re

from itsupport_copilot.schemas.commands import (
    CommandSafetyFinding,
    CommandSafetyResult,
    RiskLevel,
    ShellType,
)


_BLOCKED_RULES: list[tuple[str, re.Pattern[str], str]] = [
    ("destructive_delete_unix_root", re.compile(r"\brm\s+-[^\n]*r[^\n]*f[^\n]*(/|\*)", re.I), "Recursive forced deletion can erase data or operating system files."),
    ("destructive_delete_windows_broad", re.compile(r"\bRemove-Item\b[^\n]*(?:-Recurse|-r)\b[^\n]*(?:-Force|-fo)\b[^\n]*(?:C:\\|/|\*)", re.I), "Recursive forced deletion over a broad path is blocked."),
    ("disk_format", re.compile(r"\b(format|mkfs|diskpart|Initialize-Disk|Clear-Disk)\b", re.I), "Disk formatting or destructive disk operations are blocked."),
    ("credential_dumping", re.compile(r"\b(mimikatz|sekurlsa|lsass|ntds\.dit|/etc/shadow|sam\s+save|hashdump)\b", re.I), "Credential dumping or secret extraction is blocked."),
    ("disable_security", re.compile(r"\b(Set-MpPreference|DisableRealtimeMonitoring|DisableAntiSpyware|ufw\s+disable|setenforce\s+0)\b", re.I), "Disabling security controls is blocked."),
    ("persistence", re.compile(r"\b(schtasks\s+/create|New-Service|crontab\s+-e|reg\s+add\b[^\n]*\\Run)\b", re.I), "Persistence-enabling commands are blocked."),
    ("secret_exfiltration", re.compile(r"\b(curl|Invoke-WebRequest|iwr|wget)\b[^\n]*(password|token|secret|credential|shadow|lsass)", re.I), "Commands that may exfiltrate secrets are blocked."),
]

_HIGH_RULES: list[tuple[str, re.Pattern[str], str]] = [
    ("privilege_or_permission_change", re.compile(r"\b(chmod|chown|icacls|takeown|Set-Acl)\b", re.I), "Permission changes can affect access and availability."),
    ("firewall_change", re.compile(r"\b(New-NetFirewallRule|Set-NetFirewallProfile|iptables|firewall-cmd|netsh advfirewall)\b", re.I), "Firewall changes can disrupt connectivity or weaken security."),
    ("system_service_restart", re.compile(r"\b(Restart-Service|systemctl\s+restart|service\s+\S+\s+restart)\b", re.I), "Restarting system services can affect users."),
    ("package_install", re.compile(r"\b(apt|dnf|yum|brew|winget|choco)\s+(install|upgrade|remove|update)\b", re.I), "Package operations can change system state."),
]

_MEDIUM_RULES: list[tuple[str, re.Pattern[str], str]] = [
    ("user_service_restart", re.compile(r"\b(restart|stop|start)\b", re.I), "Service state changes need review."),
    ("cache_cleanup", re.compile(r"\b(clear|flush|cleanup|purge)\b", re.I), "Cleanup actions can remove useful diagnostic data."),
    ("log_collection", re.compile(r"\b(Get-WinEvent|journalctl|wevtutil|tar|zip)\b", re.I), "Diagnostic collection may expose sensitive logs."),
]

_LOW_READONLY = re.compile(
    r"\b(Resolve-DnsName|nslookup|Test-NetConnection|ping|tracert|df\s+-h|du\s+-sh|"
    r"journalctl\s+--disk-usage|Get-Service|Get-ComputerInfo|whoami|hostname|ipconfig|ifconfig)\b",
    re.I,
)


def check_command_safety(
    *,
    shell: ShellType,
    target_os: str,
    command: str,
    intent: str,
) -> CommandSafetyResult:
    """Score a PowerShell or Bash command without executing it."""

    normalized = " ".join(command.strip().split())
    findings: list[CommandSafetyFinding] = []
    del shell, target_os, intent

    for rule_id, pattern, message in _BLOCKED_RULES:
        if pattern.search(normalized):
            findings.append(CommandSafetyFinding(rule_id=rule_id, message=message, severity="critical"))

    if findings:
        return CommandSafetyResult(
            risk_level=RiskLevel.BLOCKED,
            blocked=True,
            findings=findings,
            requires_human_approval=True,
            safe_alternative="Use read-only diagnostics first and escalate for human review.",
        )

    for rule_id, pattern, message in _HIGH_RULES:
        if pattern.search(normalized):
            findings.append(CommandSafetyFinding(rule_id=rule_id, message=message, severity="high"))

    if findings:
        return CommandSafetyResult(
            risk_level=RiskLevel.HIGH,
            findings=findings,
            requires_human_approval=True,
        )

    for rule_id, pattern, message in _MEDIUM_RULES:
        if pattern.search(normalized):
            findings.append(CommandSafetyFinding(rule_id=rule_id, message=message, severity="medium"))

    if findings:
        return CommandSafetyResult(
            risk_level=RiskLevel.MEDIUM,
            findings=findings,
            requires_human_approval=True,
        )

    if _LOW_READONLY.search(normalized):
        return CommandSafetyResult(
            risk_level=RiskLevel.LOW,
            findings=[
                CommandSafetyFinding(
                    rule_id="read_only_diagnostic",
                    message="Command appears to be a read-only diagnostic.",
                    severity="low",
                )
            ],
            requires_human_approval=True,
        )

    return CommandSafetyResult(
        risk_level=RiskLevel.MEDIUM,
        findings=[
            CommandSafetyFinding(
                rule_id="unknown_command",
                message="Command is not recognized as a low-risk diagnostic.",
                severity="medium",
            )
        ],
        requires_human_approval=True,
    )
