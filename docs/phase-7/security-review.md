# Phase 7 Security Review

Date: 2026-04-25

## Objective

Validate security controls for command safety, prompt injection resistance, RAG data handling, API exposure, approval gates, dependency consistency, and local development limitations.

## Research Performed

Primary references reviewed:

- OWASP LLM01:2025 Prompt Injection for direct and indirect prompt injection risks and the need for untrusted-content segregation, filtering, least privilege, adversarial testing, and human approval for high-risk actions.
- OWASP LLM02:2025 Sensitive Information Disclosure for PII, credentials, confidential business data, redaction, access control, and transparent data usage requirements.
- OWASP LLM06:2025 Excessive Agency for the risk created when LLM outputs can trigger tools or external actions.
- OWASP LLM08:2025 Vector and Embedding Weaknesses for RAG data leakage, poisoning, cross-context leakage, and access-control concerns.
- OWASP API Security Top 10 2023 for broken authorization, excessive property exposure, unrestricted resource consumption, and security misconfiguration.
- NIST AI RMF and NIST AI RMF Generative AI Profile for governance, measurement, risk mapping, adversarial testing, and residual-risk framing.
- Existing Phase 2 threat model, Phase 4 safety implementation, Phase 5 API/UI integration, and Phase 6 evaluation results.

## Code Review Scope

Reviewed security-sensitive implementation paths:

- `src/itsupport_copilot/agents/nodes.py`
- `src/itsupport_copilot/app_services/bootstrap.py`
- `src/itsupport_copilot/app_services/document_service.py`
- `src/itsupport_copilot/app_services/approval_service.py`
- `src/itsupport_copilot/app_services/audit_service.py`
- `src/itsupport_copilot/safety/command_safety.py`
- `src/itsupport_copilot/safety/privacy.py`
- `src/itsupport_copilot/safety/prompt_injection.py`
- `src/itsupport_copilot/schemas/rag.py`
- `src/itsupport_copilot/schemas/tickets.py`
- `src/itsupport_copilot/api/routers/*.py`
- `tests/unit/test_security_validation.py`

## Security Fixes Implemented

- Scoped local document ingestion to the configured project root, rejecting paths outside that root.
- Removed absolute sample document path exposure from container status output.
- Excluded raw `TicketWorkflowResponse.ticket` from serialized API/model responses.
- Excluded internal `RetrievalResult.chunk` from serialized API/model responses.
- Excluded `DocumentMetadata.source_path` from serialized output while preserving internal loader use and vector-store persistence compatibility.
- Redacted secret-like retrieval query text before storing it in workflow state or returning it through API responses.
- Added security validation tests for path scope, status path disclosure, raw ticket disclosure, full chunk disclosure, source path disclosure, and secret echo behavior.

## Command Safety Validation

Current behavior:

- Command suggestions are generated as structured suggestions with target shell, intent, command, risk level, explanation, expected output, rollback note, and approval requirement.
- Commands are never executed by the application.
- Approval records are created for approvable suggestions only.
- Blocked commands do not receive approval records.
- Static scan found no application use of `subprocess`, `os.system`, `Popen`, `shell=True`, `eval`, or `exec` in runtime code.

Known blocked patterns include broad destructive deletion, credential exfiltration, security control disabling, privilege escalation, and persistence-enabling commands.

## Prompt Injection Validation

Implemented defenses:

- Direct ticket prompt injection detection.
- Retrieved-document prompt injection flags during chunking.
- Unsafe retrieved chunks are not used as grounded evidence.
- Final answers preserve source-grounding and uncertainty behavior when retrieval is insufficient or unsafe.
- Phase 6 red-team evals for direct prompt injection and malicious retrieved documents passed.

Residual risk remains because prompt injection is not fully preventable at the model layer. The application reduces impact through no execution path, evidence filtering, command risk checks, and approval gates.

## API Exposure Validation

Issues found and fixed:

- API response objects could expose too much internal data through default Pydantic serialization.
- Local ingestion accepted arbitrary filesystem paths.
- Status output exposed an absolute sample document path.

Mitigations implemented:

- Public workflow responses exclude raw ticket payloads.
- Public retrieval responses exclude full internal chunks and absolute source paths.
- Ingestion rejects paths outside the project root.
- Status output exposes only safe capability flags.

Residual production API requirements:

- Add authentication and RBAC before network exposure.
- Add request size limits, rate limits, and tenant-aware retrieval filters.
- Add schema-based response validation at the API boundary.
- Add durable audit storage with retention controls.

## Dependency and Build Validation

Commands run:

- `python -m unittest discover -s tests -p "test_*.py"`
- `python -m itsupport_copilot.evals.runner`
- `python -m pip check`
- `python -m compileall -q src app api tests`
- Static search for command execution and sensitive exposure patterns.

Results:

- Unit/integration/security tests: 25 passed.
- Evaluation suite: 7 of 7 passed, score 1.0.
- Dependency check: no broken requirements found.
- Compile check: passed.
- Static search: no runtime command execution path found.

## Residual Security Risks

- No production authentication or authorization yet.
- No tenant isolation for future multi-user deployments.
- No durable SQLite audit log yet.
- No configured TLS, rate limiting, or request body size limits.
- Dependency versions are not yet locked with hashes.
- Local Streamlit session state can hold the last demo response until cleared.
- Real external action execution remains out of scope and would require a new design, implementation, and security review.

## Security Decision

Phase 7 security validation passes for the local MVP boundary: no command execution, approval records only, redacted public outputs, scoped local ingestion, synthetic fixtures, and passing adversarial evaluations.

Production deployment is not approved until Phase 8 release readiness and future hardening items are completed.
