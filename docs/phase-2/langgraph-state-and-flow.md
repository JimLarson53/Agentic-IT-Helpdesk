# LangGraph State and Flow Design

Date: 2026-04-25
Phase: 2 - Architecture Lock, Threat Model, and Repository Plan

## Required Flow

The graph implements this required sequence:

intake -> classify -> retrieve -> reason -> draft_solution -> safety_check -> final_answer

The graph may branch only for safe fallbacks:
- Retrieval insufficient: continue to reason with uncertainty and missing-information request.
- Prompt injection detected in retrieved chunks: mark unsafe chunks, exclude them from evidence, and continue if enough safe evidence remains.
- High-risk command suggested: final answer may mention that a high-risk action was blocked or requires high-risk review, but no execution is possible.

## Graph Runtime Pattern

The MVP will use the LangGraph Graph API because the required workflow is a clear state machine. LangGraph interrupts are reserved for future true pause/resume approval flows. In the MVP, approval records are created after final answer generation and are managed by application services, because no command execution occurs.

Future execution-enabled mode may use LangGraph interrupts at the action boundary. If implemented, interrupts must:
- Use a durable checkpointer.
- Use stable thread IDs.
- Pass JSON-serializable approval payloads only.
- Avoid side effects before interrupt points.
- Resume only through approval service decisions.

## State Object

The graph state must track:

| Field | Type Concept | Owner | Notes |
| --- | --- | --- | --- |
| `run_id` | string | workflow service | Stable audit correlation ID |
| `ticket` | object | intake node | Validated ticket input |
| `classification` | object | classify node | Category, severity, platform, domain, command need |
| `retrieved_sources` | list | retrieve node | Source chunks with citations, scores, flags |
| `retrieval_assessment` | object | retrieve node | Sufficiency, conflicts, unsafe chunks |
| `reasoning_summary` | object | reason node | Concise rationale, assumptions, missing info |
| `draft_solution` | object | draft node | User-facing draft, steps, KB notes |
| `command_suggestions` | list | draft node and safety checker | Structured command suggestions |
| `safety_findings` | list | safety node | Grounding, command, privacy, prompt injection findings |
| `approval_status` | object | approval service | Pending/approved/rejected/expired records |
| `final_answer` | object | final node | Final response, citations, caveats |
| `audit_metadata` | object | workflow service | Timestamps, actor, source channel, config |

## State Schema Requirements

Ticket input:
- `title`.
- `description`.
- `affected_user`.
- `affected_system`.
- `environment`.
- `urgency`.
- `attempted_fixes`.
- `requester_context`.

Classification:
- `issue_type`.
- `category`.
- `severity`: low, medium, high, critical.
- `platform`: windows, linux, macos, cloud, network, application, unknown.
- `likely_domain`.
- `requires_command_suggestions`.
- `security_incident_suspected`.
- `escalation_recommended`.
- `confidence`.

Retrieved source:
- `source_id`.
- `filename`.
- `document_type`.
- `chunk_id`.
- `location`.
- `text_excerpt`.
- `score`.
- `citation_label`.
- `sensitivity`.
- `prompt_injection_flags`.
- `used_in_answer`.

Reasoning summary:
- `evidence_summary`.
- `assumptions`.
- `missing_information`.
- `support_strategy`.
- `escalation_reason`.
- `confidence`.

Command suggestion:
- `command_id`.
- `shell`: powershell or bash.
- `target_os`.
- `intent`.
- `command`.
- `risk_level`: low, medium, high, blocked.
- `explanation`.
- `expected_output`.
- `rollback_or_recovery`.
- `requires_human_approval`.
- `blocked_reason`.

Safety finding:
- `finding_id`.
- `finding_type`: grounding, command, privacy, prompt_injection, policy, retrieval.
- `severity`: info, low, medium, high, critical.
- `message`.
- `affected_item_id`.
- `recommended_action`.

Final answer:
- `summary`.
- `recommended_steps`.
- `commands`.
- `citations`.
- `missing_information`.
- `escalation`.
- `approval_requirements`.
- `safety_notes`.

## Node Responsibilities

### intake

Inputs:
- Validated ticket request.
- Optional run metadata.

Responsibilities:
- Normalize empty fields.
- Redact likely secrets for logs.
- Store original ticket only in state, not in unrestricted logs.
- Create first audit event.

Outputs:
- `ticket`.
- `audit_metadata`.

### classify

Inputs:
- `ticket`.

Responsibilities:
- Classify issue type, severity, platform, likely domain.
- Decide whether command suggestions may be useful.
- Detect suspected security incident or escalation requirement.

Outputs:
- `classification`.

### retrieve

Inputs:
- `ticket`.
- `classification`.

Responsibilities:
- Build retrieval query.
- Retrieve candidate chunks.
- Detect prompt injection indicators.
- Filter or flag unsafe chunks.
- Score retrieval sufficiency.
- Return citation-ready source objects.

Outputs:
- `retrieved_sources`.
- `retrieval_assessment`.

### reason

Inputs:
- `ticket`.
- `classification`.
- `retrieved_sources`.
- `retrieval_assessment`.

Responsibilities:
- Synthesize evidence.
- Identify assumptions and missing details.
- Decide support strategy.
- Preserve uncertainty when evidence is weak.

Outputs:
- `reasoning_summary`.

### draft_solution

Inputs:
- `reasoning_summary`.
- `retrieved_sources`.
- `classification`.

Responsibilities:
- Draft user-facing solution.
- Draft troubleshooting steps.
- Suggest commands only when useful.
- Generate KB-ready notes when requested.

Outputs:
- `draft_solution`.
- `command_suggestions`.

### safety_check

Inputs:
- Full graph state.

Responsibilities:
- Verify citations and retrieval grounding.
- Classify command risk.
- Block unsafe command patterns.
- Check privacy and secret leakage.
- Check prompt injection findings.
- Set answer constraints.

Outputs:
- `safety_findings`.
- Updated `command_suggestions`.

### final_answer

Inputs:
- Full graph state.

Responsibilities:
- Produce final response.
- Include citations when retrieval is used.
- Include missing information and uncertainty.
- Include approval requirements for commands/actions.
- Avoid unsupported claims.

Outputs:
- `final_answer`.

## Bad Retrieval Fallback Rules

If no source passes threshold:
- Do not invent environment-specific steps.
- Provide generic, low-risk diagnostic guidance.
- Ask for missing context.
- Mark citations as unavailable.
- Set safety finding: `retrieval_insufficient`.

If sources conflict:
- Identify conflict.
- Prefer more specific, newer, and higher-confidence sources when metadata supports that.
- Ask for human verification.

If source contains prompt injection:
- Do not follow the instruction.
- Flag the chunk.
- Exclude the malicious instruction from evidence.
- Continue only if enough safe evidence remains.

## Approval Boundary

The graph can create proposed action objects. It cannot approve or execute them.

Approval service owns:
- Approval record creation.
- Approval status changes.
- Approving human identity.
- Timestamps.
- Audit events.

Execution remains out of MVP.
