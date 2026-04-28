# Phase 4 Agent Tools and Approval Layer

Date: 2026-04-25
Phase: 4 - LangGraph Agent, Tools, and Approval Layer Development

## Implemented Scope

Phase 4 implements the required agent flow as deterministic Python nodes with an optional LangGraph builder:

intake -> classify -> retrieve -> reason -> draft_solution -> safety_check -> final_answer

The local environment does not include the `langgraph` package, so tests run through the sequential runner. The project dependency list now includes LangGraph, and `SupportAgentRunner.build_langgraph()` compiles the same node order into a `StateGraph` when LangGraph is installed.

## Tools Implemented

### Ticket Summarizer

Produces:
- Issue summary.
- Affected user/system.
- Symptoms.
- Attempted fixes.
- Likely category.
- Severity.
- Missing information.
- Next best action.

### Command Suggester

Produces structured PowerShell/Bash suggestions with:
- Target shell and OS.
- Intent.
- Command text.
- Risk level.
- Explanation.
- Expected output.
- Rollback or recovery note.
- Human approval requirement.

No command is executed.

### KB Article Generator

Produces:
- Title.
- Problem.
- Environment.
- Symptoms.
- Root cause if known.
- Resolution steps.
- Verification steps.
- Prevention notes.
- Related sources.
- Revision history metadata.

## Safety Layer

Implemented deterministic checks for:
- Command risk scoring.
- Blocked destructive commands.
- Prompt injection in tickets and retrieved chunks.
- Sensitive secret-like patterns.
- Retrieval grounding and insufficient evidence.

Blocked commands are not made approvable. Low, medium, and high risk command suggestions receive pending approval records.

## Approval Layer

The approval service creates records with:
- Proposed action.
- Action type.
- Risk level.
- Rationale.
- Affected system or data.
- Approving human.
- Timestamps.
- Approval status.
- Execution status.

MVP execution status is always `not_applicable`.

## Audit Layer

The audit service records redacted workflow and approval events:
- workflow started.
- retrieval completed.
- approval created.
- blocked command not made approvable.
- safety check completed.
- workflow completed.
- approval decision.

Audit metadata is redacted for common secret-like patterns.

## LangGraph Boundary

The implementation follows LangGraph StateGraph node shape and keeps the graph state serializable through Pydantic. True human-in-the-loop interrupts are deferred until an execution-enabled phase is explicitly approved. This is intentional because MVP has no execution path.
