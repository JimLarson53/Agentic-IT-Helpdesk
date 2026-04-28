# Phase 6 Gate Report

Date: 2026-04-25
Phase: 6 - Evaluation, QA, and Red-Team Testing

## 1. Phase Name

Evaluation, QA, and Red-Team Testing

## 2. AI LLM Agent Used

Evaluation Scientist Agent was recommended.

Substitution used: Evaluation Scientist Agent is not separately available in this Codex session, so the strongest available Codex reasoning model was used with evaluation and QA focus.

## 3. Lead Team

Team 5 - Evaluation, QA, and Red Team

## 4. Supporting Teams

- Team 3 - Development and Integration
- Team 4 - Safety, Security, and Human Approval

## 5. Objective

Build repeatable tests and evaluation cases for hallucination, unsafe commands, bad retrieval, prompt injection, citation correctness, classification accuracy, answer quality, KB generation, and approval workflow regressions.

## 6. Research Performed

Sources reviewed:
- NIST AI RMF and NIST AI RMF Generative AI Profile for lifecycle evaluation and risk-management framing.
- OWASP LLM Top 10 2025 risk categories, especially prompt injection, sensitive information disclosure, excessive agency, vector/embedding weaknesses, and misinformation.
- FastAPI testing guidance from the previous integration phase.
- Existing Phase 3, Phase 4, and Phase 5 tests and implementation contracts.

## 7. Key Findings

- Evaluation cases need explicit expected behavior, unacceptable behavior, rubric text, pass thresholds, and machine-checkable signals.
- Safety-critical evals must include negative/adversarial cases, not just normal support tickets.
- The deterministic local workflow enables repeatable CI-friendly evaluation.
- Production readiness will still require live-model and larger-corpus testing later.

## 8. Decisions Made

- Implemented a JSON fixture-driven evaluation suite.
- Implemented Pydantic evaluation case and report schemas.
- Implemented an evaluation runner with CLI JSON output and nonzero failure exit.
- Implemented scoring checks for classification, citations, insufficient retrieval, uncertainty, safety findings, command risk, approval records, blocked-command approval prevention, KB sections, and required/forbidden answer terms.
- Added tests that validate eval coverage and run the full suite.

## 9. Alternatives Considered

- Manual QA-only review: rejected because Phase 6 requires repeatable tests and regression fixtures.
- Provider-model evals: deferred because no production model/provider configuration is part of the MVP yet.
- External eval frameworks: deferred to keep the repository dependency-light and fully offline-runnable.
- Snapshot-only output comparison: rejected because structured checks are more robust for deterministic MVP behavior.

## 10. Risks and Mitigations

- Eval cases too easy: mitigated with adversarial prompt injection, destructive command, secret leakage, and bad retrieval cases.
- False confidence from deterministic tests: documented as residual risk; live-model evals remain future work.
- Citation claims unsupported: mitigated with expected source checks and minimum citation assertions.
- Unsafe command edge cases: mitigated with blocked command eval and command safety unit tests.
- Vague rubric: mitigated with explicit machine-checkable expected signals.

## 11. Deliverables Produced

Code:
- `src/itsupport_copilot/evals/__init__.py`
- `src/itsupport_copilot/evals/schemas.py`
- `src/itsupport_copilot/evals/scoring.py`
- `src/itsupport_copilot/evals/runner.py`

Fixtures:
- `evals/cases/support_eval_cases.json`

Tests:
- `tests/unit/test_evaluation_suite.py`

Documentation:
- `docs/phase-6/evaluation-suite.md`
- `docs/phase-6/qa-report.md`
- `docs/phase-6/phase-6-gate-report.md`

## 12. Acceptance Criteria Check

- Unit tests: met.
- Integration tests: met.
- Evaluation test cases: met.
- Unsafe command test cases: met.
- Bad retrieval test cases: met.
- Hallucination test cases: met.
- Prompt injection test cases: met.
- Citation correctness checks: met.
- Classification accuracy checks: met.
- Answer-quality rubric: met.
- QA report: met.

Verification:
- Full test suite:
  - 21 tests ran.
  - 21 tests passed.
- Evaluation runner:
  - 7 cases ran.
  - 7 cases passed.
  - Overall score: 1.0.

## 13. Signoff Status

Team 5 QA/evaluation signoff: complete.
Team 3 regression alignment: complete.
Team 4 safety test alignment: complete for Phase 6, with final security validation required in Phase 7.

## 14. Gate Result: PASS or BLOCKED

PASS

## 15. Handoff Recommendation

Proceed to Phase 7 only after explicit user approval. Phase 7 should perform security, privacy, prompt-injection, command-safety, approval-gate, dependency, and compliance validation.

## 16. Recommended Next Phase Agent

Security and Responsible AI Reviewer Agent.
