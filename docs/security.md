# Security and Privacy Overview

Date: 2026-04-25

Secure Agentic IT Support Copilot is a local-development MVP for source-grounded IT support assistance. It is intentionally designed as an approval-recording and suggestion system, not an automation executor.

## Security Boundary

- The application suggests support steps and commands but does not execute PowerShell, Bash, ticket updates, file operations, or external API actions.
- Approval records are audit records only. Approval does not trigger execution.
- Retrieved documents are treated as untrusted evidence, not instructions.
- Prompt injection findings can be raised from both tickets and retrieved documents.
- Command suggestions are risk-scored as low, medium, high, or blocked.
- Blocked commands are not approvable.

## Implemented Controls

- No application shell execution path was found during Phase 7 static review.
- Local audit events and approval records persist to SQLite at `data/app.sqlite3`.
- API workflow responses exclude the raw ticket object.
- Retrieval responses exclude full internal chunks.
- Local source paths are excluded from public metadata serialization.
- Retrieval query text is redacted before being stored in workflow state or returned by API responses.
- Local document ingestion is scoped to the configured project root.
- Health/status output does not expose absolute sample corpus paths.
- Audit metadata is redacted for secret-like values.
- The sample corpus uses sanitized synthetic documents only.

## Residual Risks

- The MVP does not yet include authentication, authorization, tenant separation, production encryption at rest, or managed backups.
- FastAPI and Streamlit are local demo surfaces and must not be exposed directly to untrusted networks.
- Production deployment requires RBAC, request size limits, rate limits, TLS, secret management, retention policies, deletion workflows, and dependency pinning with a release review.
- Real resumes, job descriptions, ticket data, and internal IT documents may contain PII or confidential data and require an approved data handling process before ingestion.

## References

- OWASP LLM01:2025 Prompt Injection: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- OWASP LLM02:2025 Sensitive Information Disclosure: https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/
- OWASP LLM06:2025 Excessive Agency: https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
- OWASP LLM08:2025 Vector and Embedding Weaknesses: https://genai.owasp.org/llmrisk/llm08-excessive-agency/
- OWASP API Security Top 10 2023: https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- NIST Privacy Framework: https://www.nist.gov/privacy-framework
- NIST AI RMF Generative AI Profile: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
