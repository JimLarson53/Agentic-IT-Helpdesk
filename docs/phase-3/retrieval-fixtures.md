# Retrieval Test Fixtures

Date: 2026-04-25
Phase: 3 - RAG Data Pipeline and Knowledge Engineering

## Sanitized Corpus

Location: `sample_data/docs`

Documents:
- `kb/windows-vpn-error-809.md`
- `troubleshooting/linux-disk-space.md`
- `it-docs/password-reset-policy.md`
- `resumes/synthetic-helpdesk-resume.md`
- `job-descriptions/synthetic-systems-admin-job.md`
- `security/malicious-prompt-injection-sample.md`

All documents are synthetic or sanitized. No real credentials, resumes, tickets, or customer data are included.

## Retrieval Cases

Location: `evals/fixtures/retrieval_cases.json`

Cases:
- `vpn_error_809`: expected to retrieve the VPN KB with sufficient evidence.
- `bad_retrieval_unknown_payroll`: expected to return insufficient evidence.
- `prompt_injection_fixture`: expected to flag malicious retrieved content and avoid using it for answer grounding.

## Unit Test Coverage

Location: `tests/unit/test_rag_pipeline.py`

Covered behavior:
- Sample document loading.
- VPN KB retrieval with citation.
- Bad retrieval fallback.
- Prompt-injection chunk flagging.
- Document-type filtering.
- Vector-store persistence round trip.
- Sensitive-pattern detection and redaction.
