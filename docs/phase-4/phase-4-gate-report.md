# Phase 4 Gate Report

Date: 2026-04-25
Phase: 4 - LangGraph Agent, Tools, and Approval Layer Development

## 1. Phase Name

LangGraph Agent, Tools, and Approval Layer Development

## 2. AI LLM Agent Used

GPT-5 Codex Implementation Agent.

## 3. Lead Team

Team 3 - Development and Integration

## 4. Supporting Teams

- Team 2 - Architecture and Agent Orchestration
- Team 4 - Safety, Security, and Human Approval

## 5. Objective

Implement the required agent flow and tools: ticket summarizer, command suggester, KB generator, safety checker integration, approval state handling, and audit logging foundations.

## 6. Research Performed

Sources reviewed:
- LangGraph official overview for StateGraph orientation and low-level stateful agent orchestration.
- LangGraph official interrupts/HITL documentation for future approval pause/resume behavior.
- Phase 2 architecture specification and threat model.
- Phase 3 RAG implementation and retrieval test fixtures.

Local dependency research:
- Bundled Python has Pydantic.
- Bundled Python does not have LangGraph installed.
- The project now declares `langgraph>=0.6` as a runtime dependency.
- Tests run through the sequential node runner while preserving a LangGraph builder for installed environments.

## 7. Key Findings

- The approval layer must remain outside model output and outside command generation.
- The MVP should create approval records but never execute commands.
- LangGraph interrupts should be reserved for a future execution-enabled mode with durable checkpointing.
- Deterministic safety checks are needed after command generation and before final answer generation.
- Existing RAG flags can be carried into the agent state and safety findings.

## 8. Decisions Made

- Implemented the full required flow as deterministic nodes.
- Added an optional `build_langgraph()` method that compiles the same node order into a LangGraph StateGraph when LangGraph is installed.
- Added ticket, command, approval, audit, KB, and workflow schemas.
- Implemented command risk taxonomy in code.
- Implemented approval records for non-blocked command suggestions.
- Prevented blocked commands from becoming approvable.
- Added redacted in-memory audit logging.
- Added KB generation from completed workflow responses.

## 9. Alternatives Considered

- Installing LangGraph during this phase: not attempted because network access is restricted and tests must remain runnable offline.
- Model-based summarization and command generation: deferred because no provider credentials are required for MVP tests, and safety-critical behavior must be deterministic.
- Human-in-the-loop interrupts in MVP: deferred because there is no command execution path; approval records are sufficient and safer for this phase.
- SQLite persistence for approvals in Phase 4: deferred to Phase 5/8 integration polish because in-memory services allow the safety and state model to be tested now.

## 10. Risks and Mitigations

- LangGraph package unavailable locally: mitigated with optional builder and sequential test runner.
- Unsafe commands slipping through: mitigated with blocked/high/medium/low command classifier and tests.
- Approval confused with execution: mitigated by `execution_status=not_applicable` and no execution code.
- Prompt injection in ticket or retrieval: mitigated with deterministic flags and safety findings.
- Logs retaining secrets: mitigated with redaction in audit service.
- Breaking Phase 3 RAG: mitigated by running the full test suite.

## 11. Deliverables Produced

Code:
- `src/itsupport_copilot/agents/state.py`
- `src/itsupport_copilot/agents/nodes.py`
- `src/itsupport_copilot/agents/graph.py`
- `src/itsupport_copilot/tools/ticket_summarizer.py`
- `src/itsupport_copilot/tools/command_suggester.py`
- `src/itsupport_copilot/tools/kb_generator.py`
- `src/itsupport_copilot/safety/command_safety.py`
- `src/itsupport_copilot/safety/grounding.py`
- `src/itsupport_copilot/app_services/approval_service.py`
- `src/itsupport_copilot/app_services/audit_service.py`
- `src/itsupport_copilot/app_services/ticket_service.py`
- `src/itsupport_copilot/app_services/kb_service.py`
- `src/itsupport_copilot/schemas/commands.py`
- `src/itsupport_copilot/schemas/approvals.py`
- `src/itsupport_copilot/schemas/audit.py`
- `src/itsupport_copilot/schemas/tickets.py`
- `src/itsupport_copilot/schemas/kb.py`

Tests:
- `tests/unit/test_agent_workflow.py`

Documentation:
- `docs/phase-4/agent-tools-and-approval.md`
- `docs/phase-4/phase-4-gate-report.md`

## 12. Acceptance Criteria Check

- LangGraph-compatible flow: met.
- Intake/classify/retrieve/reason/draft_solution/safety_check/final_answer: met.
- Ticket summarizer: met.
- Command suggester: met.
- KB generator: met.
- Command safety checker: met.
- Safety checker integration: met.
- Approval state handling: met.
- Audit logging foundation: met.
- No command execution: met.
- Tests: met.

Verification:
- Command run with approved filesystem access:
  - `$env:PYTHONPATH='src'; python -m unittest discover -s tests -p 'test_*.py'`
- Result:
  - 12 tests ran.
  - 12 tests passed.

## 13. Signoff Status

Team 3 implementation signoff: complete.
Team 2 architecture alignment: complete.
Team 4 safety and approval-layer signoff: complete for Phase 4, with final security validation required in Phase 7.

## 14. Gate Result: PASS or BLOCKED

PASS

## 15. Handoff Recommendation

Proceed to Phase 5 only after explicit user approval. Phase 5 should implement Streamlit/FastAPI integration with ticket input, retrieval display, generated answer, command approval workflow, KB generation, and settings.

## 16. Recommended Next Phase Agent

GPT-5 Codex Implementation Agent.
