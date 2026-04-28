"""KB generation service."""

from __future__ import annotations

from itsupport_copilot.schemas.kb import KBArticle
from itsupport_copilot.schemas.tickets import TicketWorkflowResponse
from itsupport_copilot.tools.kb_generator import generate_kb_article


class KBService:
    """Generate KB drafts from completed workflow responses."""

    def generate_from_workflow(self, response: TicketWorkflowResponse) -> KBArticle:
        return generate_kb_article(
            ticket=response.ticket,
            summary=response.summary,
            draft=response.draft_solution,
            citations=response.final_answer.citations,
        )
