"""KB article generation tool."""

from __future__ import annotations

from itsupport_copilot.schemas.kb import KBArticle
from itsupport_copilot.schemas.rag import Citation
from itsupport_copilot.schemas.tickets import DraftSolution, TicketInput, TicketSummary


def generate_kb_article(
    *,
    ticket: TicketInput,
    summary: TicketSummary,
    draft: DraftSolution,
    citations: list[Citation],
) -> KBArticle:
    """Generate a KB article draft for human review."""

    environment = ticket.environment or "Environment not provided"
    root_cause = None
    if citations:
        root_cause = "Likely cause should be confirmed against the cited support sources."

    return KBArticle(
        title=f"KB Draft: {summary.issue_summary[:80]}",
        problem=summary.issue_summary,
        environment=environment,
        symptoms=summary.symptoms,
        root_cause=root_cause,
        resolution_steps=draft.troubleshooting_steps,
        verification_steps=[
            "Confirm the user can complete the original workflow without the reported error.",
            "Record any remaining symptoms, error codes, and affected systems.",
        ],
        prevention_notes=[
            "Keep source runbooks and KB articles current.",
            "Escalate recurring issues for root-cause review.",
        ],
        related_sources=citations,
    )
