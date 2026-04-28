"""Grounding checks for retrieval-backed answers."""

from __future__ import annotations

from itsupport_copilot.schemas.rag import RetrievalResponse
from itsupport_copilot.schemas.tickets import SafetyFinding


def check_retrieval_grounding(retrieval: RetrievalResponse) -> list[SafetyFinding]:
    """Return safety findings for weak or unsafe retrieval."""

    findings: list[SafetyFinding] = []
    if not retrieval.assessment.sufficient:
        findings.append(
            SafetyFinding(
                finding_type="grounding",
                severity="medium",
                message=f"Retrieved evidence is insufficient: {retrieval.assessment.reason}.",
                recommended_action="State uncertainty, ask for missing information, and avoid environment-specific claims.",
            )
        )
    if retrieval.assessment.unsafe_result_count:
        findings.append(
            SafetyFinding(
                finding_type="prompt_injection",
                severity="high",
                message="One or more retrieved chunks contained prompt-injection indicators.",
                recommended_action="Treat flagged chunks as untrusted and do not use them as grounding evidence.",
            )
        )
    return findings
