"""Graph runner for the required support workflow."""

from __future__ import annotations

from typing import Any

from itsupport_copilot.app_services.approval_service import ApprovalService
from itsupport_copilot.app_services.audit_service import AuditService
from itsupport_copilot.rag import Retriever
from itsupport_copilot.schemas.tickets import TicketInput, TicketWorkflowResponse

from .nodes import (
    NodeContext,
    classify_node,
    draft_solution_node,
    final_answer_node,
    intake_node,
    reason_node,
    retrieve_node,
    safety_check_node,
)
from .state import SupportAgentState


FLOW_NODE_NAMES = (
    "intake",
    "classify",
    "retrieve",
    "reason",
    "draft_solution",
    "safety_check",
    "final_answer",
)


class SupportAgentRunner:
    """Run the required agent workflow without executing commands."""

    def __init__(
        self,
        *,
        retriever: Retriever | None = None,
        audit_service: AuditService | None = None,
        approval_service: ApprovalService | None = None,
    ) -> None:
        self.audit_service = audit_service or AuditService()
        self.approval_service = approval_service or ApprovalService(self.audit_service)
        self.context = NodeContext(
            retriever=retriever,
            audit_service=self.audit_service,
            approval_service=self.approval_service,
        )

    def run(self, ticket: TicketInput) -> TicketWorkflowResponse:
        state = SupportAgentState(ticket=ticket)
        for node in (
            intake_node,
            classify_node,
            retrieve_node,
            reason_node,
            draft_solution_node,
            safety_check_node,
            final_answer_node,
        ):
            state = node(state, self.context)

        assert state.ticket_summary is not None
        assert state.classification is not None
        assert state.retrieval is not None
        assert state.reasoning_summary is not None
        assert state.draft_solution is not None
        assert state.final_answer is not None
        self.audit_service.record(
            run_id=state.run_id,
            event_type="workflow_completed",
            summary="Ticket workflow completed.",
            metadata={"approval_count": len(state.approval_records)},
        )
        return TicketWorkflowResponse(
            run_id=state.run_id,
            ticket=state.ticket,
            summary=state.ticket_summary,
            classification=state.classification,
            retrieval=state.retrieval,
            reasoning_summary=state.reasoning_summary,
            draft_solution=state.draft_solution,
            command_suggestions=state.command_suggestions,
            safety_findings=state.safety_findings,
            approval_records=state.approval_records,
            final_answer=state.final_answer,
        )

    def build_langgraph(self) -> Any:
        """Build a LangGraph StateGraph when the optional runtime is installed.

        Tests use the sequential runner because this local environment does not
        include LangGraph. The node order and state contract are identical.
        """

        try:
            from langgraph.graph import END, START, StateGraph
        except ImportError as exc:
            raise RuntimeError("LangGraph is not installed. Install project dependencies.") from exc

        def wrap(node):
            def wrapped(raw_state: dict[str, Any]) -> dict[str, Any]:
                state = SupportAgentState.model_validate(raw_state)
                updated = node(state, self.context)
                return updated.model_dump(mode="python")

            return wrapped

        graph = StateGraph(dict)
        graph.add_node("intake", wrap(intake_node))
        graph.add_node("classify", wrap(classify_node))
        graph.add_node("retrieve", wrap(retrieve_node))
        graph.add_node("reason", wrap(reason_node))
        graph.add_node("draft_solution", wrap(draft_solution_node))
        graph.add_node("safety_check", wrap(safety_check_node))
        graph.add_node("final_answer", wrap(final_answer_node))
        graph.add_edge(START, "intake")
        graph.add_edge("intake", "classify")
        graph.add_edge("classify", "retrieve")
        graph.add_edge("retrieve", "reason")
        graph.add_edge("reason", "draft_solution")
        graph.add_edge("draft_solution", "safety_check")
        graph.add_edge("safety_check", "final_answer")
        graph.add_edge("final_answer", END)
        return graph.compile()
