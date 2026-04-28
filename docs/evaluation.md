# Evaluation

Date: 2026-04-25

## Purpose

The evaluation suite proves that core safety and answer-quality behavior remains stable as the app evolves. It is deterministic and offline-runnable for GitHub Actions.

## Coverage

Evaluation cases cover:

- Hallucination and unsupported answer prevention.
- Unsafe command blocking.
- Bad retrieval fallback.
- Direct prompt injection.
- Retrieved-document prompt injection.
- Secret-like ticket redaction.
- Citation correctness.
- Classification accuracy.
- Answer quality.
- KB article generation.
- Approval workflow behavior.

## Case Format

Each case in `evals/cases/support_eval_cases.json` defines:

- Input ticket/question.
- Expected behavior.
- Unacceptable behavior.
- Expected classification signals.
- Expected source/citation signals.
- Required or forbidden final-answer terms.
- Safety finding expectations.
- Pass/fail threshold.

## Runner

Run:

```powershell
$env:PYTHONPATH="src"
python -m itsupport_copilot.evals.runner
```

The runner prints a JSON report and exits nonzero if any case fails.

## Current Result

Phase 8 validation result:

- Total cases: 7
- Passed cases: 7
- Failed cases: 0
- Score: 1.0

## Residual Evaluation Work

Before production use, add live-model evaluations, larger corpora, tenant authorization tests, rate-limit tests, real-world sanitized ticket samples, regression snapshots for UI/API responses, and human expert review of generated KB drafts.
