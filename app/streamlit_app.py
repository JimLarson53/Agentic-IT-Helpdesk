"""Streamlit demo UI for Secure Agentic IT Support Copilot."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from itsupport_copilot.app_services.bootstrap import create_app_container
from itsupport_copilot.schemas.approvals import ApprovalDecision, ApprovalStatus
from itsupport_copilot.schemas.tickets import TicketInput, TicketWorkflowResponse, Urgency


REPO_ROOT = Path(__file__).resolve().parents[1]


@st.cache_resource(show_spinner=False)
def get_container():
    return create_app_container(REPO_ROOT)


def main() -> None:
    st.set_page_config(page_title="Secure Agentic IT Support Copilot", layout="wide")
    container = get_container()

    st.title("Secure Agentic IT Support Copilot")
    st.caption("Commands are suggestions only. Approval records do not execute actions.")

    intake_tab, result_tab, kb_tab, settings_tab = st.tabs(
        ["Ticket", "Analysis", "KB Draft", "Settings"]
    )

    with intake_tab:
        render_ticket_form(container)

    response = st.session_state.get("last_response")
    if isinstance(response, TicketWorkflowResponse):
        with result_tab:
            render_analysis(response, container)
        with kb_tab:
            render_kb(response, container)
    else:
        with result_tab:
            st.info("Submit a ticket to see analysis, citations, command suggestions, and approvals.")
        with kb_tab:
            st.info("Generate a ticket analysis first.")

    with settings_tab:
        render_settings(container)


def render_ticket_form(container) -> None:
    with st.form("ticket_form"):
        title = st.text_input("Ticket title", value="VPN error 809")
        description = st.text_area(
            "Description",
            value="Windows user receives VPN error 809 when connecting to vpn.example.test.",
            height=140,
        )
        col_a, col_b = st.columns(2)
        affected_user = col_a.text_input("Affected user", value="synthetic.user@example.test")
        affected_system = col_b.text_input("Affected system", value="Windows laptop")
        environment = st.text_input("Environment", value="Windows 11 remote access VPN")
        urgency = st.selectbox("Urgency", [item.value for item in Urgency], index=1)
        attempted_fixes = st.text_area("Attempted fixes", value="User restarted the VPN client.")
        generate_kb = st.checkbox("Prepare KB draft", value=True)
        submitted = st.form_submit_button("Analyze Ticket", type="primary")

    if submitted:
        ticket = TicketInput(
            title=title,
            description=description,
            affected_user=affected_user or None,
            affected_system=affected_system or None,
            environment=environment or None,
            urgency=Urgency(urgency),
            attempted_fixes=attempted_fixes or None,
            generate_kb_draft=generate_kb,
        )
        with st.spinner("Running secure support workflow..."):
            st.session_state["last_response"] = container.runner.run(ticket)
        st.success("Analysis complete.")


def render_analysis(response: TicketWorkflowResponse, container) -> None:
    st.subheader("Summary")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Severity", response.classification.severity.value)
    col_b.metric("Platform", response.classification.platform.value)
    col_c.metric("Category", response.classification.category)

    st.write(response.final_answer.summary)

    st.subheader("Recommended Steps")
    for step in response.final_answer.recommended_steps:
        st.markdown(f"- {step}")

    if response.final_answer.missing_information:
        st.subheader("Missing Information")
        for item in response.final_answer.missing_information:
            st.markdown(f"- {item}")

    st.subheader("Retrieved Sources")
    if response.final_answer.citations:
        st.dataframe(
            [
                {
                    "source": citation.filename,
                    "type": getattr(citation.document_type, "value", citation.document_type),
                    "location": citation.location,
                    "score": citation.score,
                    "excerpt": citation.excerpt,
                }
                for citation in response.final_answer.citations
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.warning("No sufficient source-grounded evidence was found.")

    render_commands(response, container)

    if response.final_answer.safety_notes:
        st.subheader("Safety Notes")
        for note in response.final_answer.safety_notes:
            st.markdown(f"- {note}")


def render_commands(response: TicketWorkflowResponse, container) -> None:
    st.subheader("Command Suggestions")
    if not response.command_suggestions:
        st.info("No command suggestions were produced for this ticket.")
        return

    for command in response.command_suggestions:
        with st.expander(f"{command.risk_level.value.upper()} | {command.intent}", expanded=True):
            st.code(command.command, language="powershell" if command.shell.value == "powershell" else "bash")
            st.write(command.explanation)
            st.write(f"Expected output: {command.expected_output}")
            st.write(f"Recovery note: {command.rollback_or_recovery}")
            if command.blocked_reason:
                st.error(f"Blocked: {command.blocked_reason}")
                continue
            if not command.approval_id:
                st.warning("No approval record exists for this command.")
                continue

            record = container.approval_service.get(command.approval_id)
            st.write(f"Approval status: {record.approval_status.value}")
            col_a, col_b = st.columns(2)
            if col_a.button("Approve Command", key=f"approve_{command.command_id}"):
                container.approval_service.decide(
                    command.approval_id,
                    ApprovalDecision(
                        decision=ApprovalStatus.APPROVED,
                        approving_human="streamlit-demo-user",
                        comment="Approved from Streamlit demo. No execution performed.",
                    ),
                )
                st.rerun()
            if col_b.button("Reject Command", key=f"reject_{command.command_id}"):
                container.approval_service.decide(
                    command.approval_id,
                    ApprovalDecision(
                        decision=ApprovalStatus.REJECTED,
                        approving_human="streamlit-demo-user",
                        comment="Rejected from Streamlit demo.",
                    ),
                )
                st.rerun()


def render_kb(response: TicketWorkflowResponse, container) -> None:
    article = container.kb_service.generate_from_workflow(response)
    st.subheader(article.title)
    st.write(f"Problem: {article.problem}")
    st.write(f"Environment: {article.environment}")
    st.write("Symptoms")
    for symptom in article.symptoms:
        st.markdown(f"- {symptom}")
    st.write("Resolution Steps")
    for step in article.resolution_steps:
        st.markdown(f"- {step}")
    st.write("Verification Steps")
    for step in article.verification_steps:
        st.markdown(f"- {step}")
    st.write("Prevention Notes")
    for note in article.prevention_notes:
        st.markdown(f"- {note}")


def render_settings(container) -> None:
    status = container.status()
    st.subheader("Runtime Status")
    st.json(status)
    st.subheader("Safety Boundary")
    st.markdown("- Command execution is disabled.")
    st.markdown("- Retrieved content is treated as evidence, not instruction.")
    st.markdown("- Approval records are audit records and do not perform external actions.")


if __name__ == "__main__":
    main()
