"""Node implementations for the support agent workflow."""

from __future__ import annotations

from dataclasses import dataclass

from itsupport_copilot.app_services.approval_service import ApprovalService
from itsupport_copilot.app_services.audit_service import AuditService
from itsupport_copilot.rag import Retriever
from itsupport_copilot.safety.command_safety import check_command_safety
from itsupport_copilot.safety.grounding import check_retrieval_grounding
from itsupport_copilot.safety.privacy import find_sensitive_patterns, redact_sensitive_text
from itsupport_copilot.safety.prompt_injection import detect_prompt_injection
from itsupport_copilot.schemas.commands import RiskLevel
from itsupport_copilot.schemas.rag import RetrievalAssessment, RetrievalResponse
from itsupport_copilot.schemas.tickets import (
    Classification,
    DraftSolution,
    FinalAnswer,
    Platform,
    ReasoningSummary,
    SafetyFinding,
    Severity,
)
from itsupport_copilot.tools.command_suggester import suggest_commands
from itsupport_copilot.tools.ticket_summarizer import summarize_ticket

from .state import SupportAgentState


@dataclass
class NodeContext:
    retriever: Retriever | None
    audit_service: AuditService
    approval_service: ApprovalService


def intake_node(state: SupportAgentState, context: NodeContext) -> SupportAgentState:
    ticket = state.ticket
    context.audit_service.record(
        run_id=state.run_id,
        event_type="workflow_started",
        summary=f"Ticket workflow started: {ticket.title}",
        metadata={"ticket_title": ticket.title, "description": redact_sensitive_text(ticket.description)},
    )
    return state.model_copy(update={"audit_metadata": {"source": "local_agent", "execution": "disabled"}})


def classify_node(state: SupportAgentState, context: NodeContext) -> SupportAgentState:
    del context
    classification = classify_ticket(state.ticket.title, state.ticket.description, state.ticket.urgency.value)
    summary = summarize_ticket(state.ticket, classification)
    return state.model_copy(update={"classification": classification, "ticket_summary": summary})


def retrieve_node(state: SupportAgentState, context: NodeContext) -> SupportAgentState:
    query = redact_sensitive_text(_build_retrieval_query(state))
    if context.retriever is None:
        retrieval = RetrievalResponse(
            query=query,
            results=[],
            assessment=RetrievalAssessment(
                sufficient=False,
                reason="retriever_not_configured",
                min_score=0.0,
            ),
        )
    else:
        retrieval = context.retriever.retrieve(query)
    context.audit_service.record(
        run_id=state.run_id,
        event_type="retrieval_completed",
        summary=f"Retrieval completed with status {retrieval.assessment.reason}.",
        metadata={
            "result_count": retrieval.assessment.result_count,
            "safe_result_count": retrieval.assessment.safe_result_count,
            "unsafe_result_count": retrieval.assessment.unsafe_result_count,
        },
    )
    return state.model_copy(update={"retrieval": retrieval})


def reason_node(state: SupportAgentState, context: NodeContext) -> SupportAgentState:
    del context
    assert state.classification is not None
    assert state.ticket_summary is not None
    assert state.retrieval is not None

    used = [result for result in state.retrieval.results if result.used_in_answer]
    if used:
        evidence = "Relevant evidence found in: " + ", ".join(
            f"{result.citation.filename} ({result.citation.location})" for result in used
        )
        confidence = min(0.9, 0.55 + 0.1 * len(used))
    else:
        evidence = "No sufficient source-grounded evidence was found for this ticket."
        confidence = 0.35

    assumptions = []
    if state.classification.platform != Platform.UNKNOWN:
        assumptions.append(f"Ticket appears related to {state.classification.platform.value}.")
    if not used:
        assumptions.append("Guidance must stay generic until stronger evidence is available.")

    escalation_reason = None
    if state.classification.escalation_recommended:
        escalation_reason = "Severity, suspected security issue, or operational impact requires escalation."

    reasoning = ReasoningSummary(
        evidence_summary=evidence,
        assumptions=assumptions,
        missing_information=state.ticket_summary.missing_information,
        support_strategy=_support_strategy(state.classification, state.retrieval.assessment.sufficient),
        escalation_reason=escalation_reason,
        confidence=confidence,
    )
    return state.model_copy(update={"reasoning_summary": reasoning})


def draft_solution_node(state: SupportAgentState, context: NodeContext) -> SupportAgentState:
    del context
    assert state.classification is not None
    assert state.ticket_summary is not None
    assert state.retrieval is not None
    assert state.reasoning_summary is not None

    citations = [result.citation for result in state.retrieval.results if result.used_in_answer]
    steps = _draft_steps(state)
    response = _draft_user_response(state, bool(citations))
    commands = suggest_commands(state.ticket, state.classification)
    draft = DraftSolution(
        user_response=response,
        troubleshooting_steps=steps,
        kb_notes=[
            "Document confirmed symptoms, diagnostics, and final resolution.",
            "Link cited sources and record any human-approved command decisions.",
        ],
        citations=citations,
    )
    return state.model_copy(update={"draft_solution": draft, "command_suggestions": commands})


def safety_check_node(state: SupportAgentState, context: NodeContext) -> SupportAgentState:
    assert state.retrieval is not None

    findings = list(state.safety_findings)
    findings.extend(check_retrieval_grounding(state.retrieval))

    ticket_text = f"{state.ticket.title}\n{state.ticket.description}\n{state.ticket.attempted_fixes or ''}"
    for flag in detect_prompt_injection(ticket_text):
        findings.append(
            SafetyFinding(
                finding_type="prompt_injection",
                severity="high",
                message=f"Ticket contains prompt-injection indicator: {flag}.",
                recommended_action="Do not follow instruction-like text from the ticket.",
            )
        )
    for flag in find_sensitive_patterns(ticket_text):
        findings.append(
            SafetyFinding(
                finding_type="privacy",
                severity="high",
                message=f"Ticket contains sensitive pattern: {flag}.",
                recommended_action="Redact the value from logs and advise rotation if it is a credential.",
            )
        )

    checked_commands = []
    approval_records = []
    for command in state.command_suggestions:
        safety = check_command_safety(
            shell=command.shell,
            target_os=command.target_os,
            command=command.command,
            intent=command.intent,
        )
        blocked_reason = command.blocked_reason
        if safety.blocked:
            blocked_reason = "; ".join(finding.message for finding in safety.findings)
            findings.append(
                SafetyFinding(
                    finding_type="command",
                    severity="critical",
                    message=f"Blocked unsafe command: {command.intent}",
                    affected_item_id=command.command_id,
                    recommended_action=safety.safe_alternative or "Use safer diagnostics.",
                )
            )
        updated_command = command.model_copy(
            update={
                "risk_level": safety.risk_level,
                "requires_human_approval": safety.requires_human_approval,
                "blocked_reason": blocked_reason,
            }
        )
        record = context.approval_service.create_for_command(run_id=state.run_id, command=updated_command)
        if record is not None:
            updated_command = updated_command.model_copy(update={"approval_id": record.approval_id})
            approval_records.append(record)
        checked_commands.append(updated_command)

    context.audit_service.record(
        run_id=state.run_id,
        event_type="safety_check_completed",
        summary=f"Safety check completed with {len(findings)} finding(s).",
        metadata={"finding_count": len(findings), "command_count": len(checked_commands)},
    )
    return state.model_copy(
        update={
            "command_suggestions": checked_commands,
            "safety_findings": findings,
            "approval_records": approval_records,
        }
    )


def final_answer_node(state: SupportAgentState, context: NodeContext) -> SupportAgentState:
    del context
    assert state.draft_solution is not None
    assert state.reasoning_summary is not None

    approval_requirements = []
    for command in state.command_suggestions:
        if command.risk_level == RiskLevel.BLOCKED:
            approval_requirements.append(f"{command.command_id}: blocked and not approvable.")
        elif command.approval_id:
            approval_requirements.append(
                f"{command.command_id}: requires human approval record {command.approval_id}."
            )

    safety_notes = [finding.message for finding in state.safety_findings]
    final = FinalAnswer(
        summary=state.draft_solution.user_response,
        recommended_steps=state.draft_solution.troubleshooting_steps,
        commands=state.command_suggestions,
        citations=state.draft_solution.citations,
        missing_information=state.reasoning_summary.missing_information,
        escalation=state.reasoning_summary.escalation_reason,
        approval_requirements=approval_requirements,
        safety_notes=safety_notes,
    )
    return state.model_copy(update={"final_answer": final})


def classify_ticket(title: str, description: str, urgency: str) -> Classification:
    text = f"{title} {description}".lower()
    severity = Severity.CRITICAL if urgency == "critical" else Severity(urgency)
    platform = Platform.UNKNOWN
    category = "general_support"
    issue_type = "support_request"
    likely_domain = "service desk"
    requires_commands = False
    security = False
    escalation = severity in {Severity.HIGH, Severity.CRITICAL}
    confidence = 0.55

    if "vpn" in text or "error 809" in text:
        platform = Platform.WINDOWS
        category = "network_vpn"
        issue_type = "connectivity"
        likely_domain = "network access"
        requires_commands = True
        confidence = 0.86
    elif "disk" in text or "filesystem" in text or "space" in text:
        platform = Platform.LINUX if "linux" in text or "ubuntu" in text else Platform.UNKNOWN
        category = "infrastructure_storage"
        issue_type = "capacity"
        likely_domain = "systems"
        requires_commands = True
        confidence = 0.78
    elif "password" in text or "mfa" in text or "reset" in text:
        platform = Platform.IDENTITY
        category = "identity_access"
        issue_type = "access"
        likely_domain = "identity"
        confidence = 0.82
    elif "malware" in text or "ransomware" in text or "compromise" in text:
        category = "security_incident"
        issue_type = "security"
        likely_domain = "security operations"
        security = True
        escalation = True
        confidence = 0.84

    return Classification(
        issue_type=issue_type,
        category=category,
        severity=severity,
        platform=platform,
        likely_domain=likely_domain,
        requires_command_suggestions=requires_commands,
        security_incident_suspected=security,
        escalation_recommended=escalation,
        confidence=confidence,
    )


def _build_retrieval_query(state: SupportAgentState) -> str:
    parts = [
        state.ticket.title,
        state.ticket.description,
        state.ticket.environment or "",
        state.ticket.affected_system or "",
    ]
    if state.classification:
        parts.extend([state.classification.category, state.classification.likely_domain])
    return " ".join(part for part in parts if part).strip()


def _support_strategy(classification: Classification, retrieval_sufficient: bool) -> str:
    if classification.escalation_recommended:
        return "Escalate after collecting safe diagnostics and impact details."
    if retrieval_sufficient:
        return "Use retrieved source-grounded troubleshooting steps and cite sources."
    return "Provide low-risk generic diagnostics and request missing evidence."


def _draft_steps(state: SupportAgentState) -> list[str]:
    assert state.classification is not None
    assert state.retrieval is not None

    if not state.retrieval.assessment.sufficient:
        return [
            "Confirm the affected user, system, environment, exact error, and recent changes.",
            "Avoid environment-specific remediation until a relevant KB or runbook is available.",
            "Escalate if the issue is widespread, security-related, or business-critical.",
        ]

    if state.classification.category == "network_vpn":
        return [
            "Confirm the user is not on captive portal or guest Wi-Fi.",
            "Verify the VPN profile uses the approved gateway name from the cited KB.",
            "Run only approved read-only diagnostics after human approval is recorded.",
            "Escalate to network engineering if DNS fails or multiple users are affected.",
        ]
    if state.classification.category == "infrastructure_storage":
        return [
            "Check filesystem usage with approved read-only diagnostics.",
            "Identify large log directories without deleting arbitrary system files.",
            "Use application-specific cleanup procedures and escalate before production data removal.",
        ]
    if state.classification.category == "identity_access":
        return [
            "Verify user identity through approved channels.",
            "Do not collect passwords, one-time codes, recovery codes, or tokens in the ticket.",
            "Proceed with the approved reset workflow only after verification.",
        ]
    return [
        "Review retrieved sources and confirm the issue details.",
        "Ask for missing information listed by the assistant.",
        "Escalate when impact, safety, or evidence gaps require a specialist.",
    ]


def _draft_user_response(state: SupportAgentState, has_citations: bool) -> str:
    assert state.ticket_summary is not None
    if has_citations:
        return f"Based on the retrieved support sources, this appears to be {state.ticket_summary.likely_category}: {state.ticket_summary.issue_summary}"
    return f"I do not have enough relevant source evidence to give environment-specific remediation for: {state.ticket_summary.issue_summary}"
