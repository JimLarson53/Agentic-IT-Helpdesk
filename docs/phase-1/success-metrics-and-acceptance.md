# Success Metrics and Acceptance Criteria

Date: 2026-04-25
Phase: 1 - Discovery, Research, and Requirements

## Product Success Metrics

- Ticket summarization quality: at least 90 percent of evaluation cases include issue summary, affected system/user, symptoms, attempted fixes, likely category, severity, missing information, and next best action.
- Classification accuracy: at least 85 percent on sanitized representative ticket fixtures.
- Retrieval grounding: at least 90 percent of cited answers reference relevant source chunks when relevant documents exist.
- Bad-retrieval behavior: 100 percent of insufficient-evidence cases state uncertainty or ask for missing information rather than fabricate.
- Unsafe command behavior: 100 percent of blocked command fixtures are blocked or high-risk flagged with no auto-execution.
- Prompt injection defense: 100 percent of malicious document fixtures fail to override system or safety policy.
- Citation correctness: at least 90 percent of cited sources support the claims they are attached to.
- KB article quality: at least 85 percent pass rubric review for required sections and source support.
- Test readiness: unit, integration, safety, and evaluation tests pass in CI.
- Repository readiness: clean setup, README, docs, diagrams, demo script, and `.env.example` exist before release.

## Operational Success Metrics

- Time to first useful draft: local demo should return a response fast enough for practical triage on small sample corpora.
- Analyst trust: UI exposes classification, citations, risk findings, and approval status.
- Auditability: every proposed action has a durable approval record.
- Maintainability: model, embedding, vector store, and UI layers can be replaced without rewriting core safety policies.

## Safety Success Metrics

- No automatic command execution.
- No unrestricted agent actions.
- High-risk commands are blocked or require explicit high-risk review.
- Retrieved documents cannot instruct the agent to ignore policy.
- Secrets are redacted from logs and warnings are shown when secret-like input is detected.
- Privacy-sensitive workflows document retention and access assumptions.

## Evaluation Case Requirements

Every evaluation case must include:
- Input ticket or user question.
- Available documents.
- Expected behavior.
- Unacceptable behavior.
- Scoring rubric.
- Pass/fail threshold.

Required evaluation categories:
- Hallucination.
- Unsafe commands.
- Bad retrieval.
- Prompt injection.
- Citation correctness.
- Classification accuracy.
- Answer quality.
- KB generation.
- Approval workflow.

## Phase-Level Acceptance Criteria

Phase 1 acceptance requires:
- Clear product scope.
- User personas and workflows.
- Corpus and data sensitivity inventory.
- Hidden requirements.
- Assumptions and constraints.
- Measurable success metrics.
- Security, privacy, and safety risks identified for later phases.

Status: PASS for Phase 1 if the gate report is accepted.
