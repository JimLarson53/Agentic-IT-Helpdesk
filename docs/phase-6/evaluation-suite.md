# Phase 6 Evaluation Suite

Date: 2026-04-25
Phase: 6 - Evaluation, QA, and Red-Team Testing

## Evaluation Design

The evaluation suite is fixture-driven and repeatable. Each case defines:
- Input ticket.
- Categories under test.
- Expected behavior.
- Unacceptable behavior.
- Scoring rubric.
- Pass threshold.
- Machine-checkable expected signals.

The runner executes cases against the same local application container used by FastAPI and Streamlit.

## Implemented Categories

- Hallucination.
- Unsafe commands.
- Bad retrieval.
- Prompt injection.
- Citation correctness.
- Classification accuracy.
- Answer quality.
- KB generation.
- Approval workflow.

## Case File

`evals/cases/support_eval_cases.json`

Current cases:
- `classification_vpn_grounded`
- `classification_linux_disk_space`
- `bad_retrieval_payroll_unknown`
- `unsafe_command_blocked`
- `direct_prompt_injection`
- `secret_in_ticket_redaction`
- `kb_article_generation`

## Runner

Package entrypoint:

```powershell
$env:PYTHONPATH="src"
python -m itsupport_copilot.evals.runner
```

The command emits a JSON report and exits with code `0` only when all cases pass.

## Scoring

The scorer checks:
- Expected category, platform, and severity.
- Expected source filenames in citations or retrieved results.
- Minimum citation count.
- Insufficient retrieval when required.
- Uncertainty language when required.
- Required safety finding types.
- Required command risk levels.
- Approval record counts.
- No approval ID for blocked commands.
- KB article required sections.
- Required and forbidden answer terms.

## Research Basis

- NIST AI RMF and NIST AI RMF Generative AI Profile support lifecycle-based evaluation and risk monitoring for trustworthy AI systems.
- OWASP LLM Top 10 2025 identifies prompt injection, sensitive information disclosure, excessive agency, vector/embedding weaknesses, and misinformation as relevant risk areas.
- FastAPI testing guidance supports executable contract tests around API behavior.

## Limitations

- The current suite evaluates deterministic local behavior, not live provider-model variability.
- The hashing embedder is lower quality than transformer embeddings, so retrieval eval thresholds are tuned to the MVP corpus.
- Human review remains required for production release decisions.
- Phase 7 must perform security/privacy validation beyond these functional and adversarial tests.
