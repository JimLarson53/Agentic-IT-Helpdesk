# Phase 7 Privacy Review

Date: 2026-04-25

## Jurisdiction and Legal Assumption

The primary launch context is assumed to be the United States. This review is engineering and product-risk guidance, not legal advice. Real deployment with resumes, job descriptions, employee tickets, or customer support records should be reviewed by qualified privacy, employment, and security counsel.

## Data Types Reviewed

- Support tickets and user questions.
- IT documentation and troubleshooting notes.
- Internal KB articles.
- Resumes and job descriptions.
- Retrieval chunks, citations, and excerpts.
- Command suggestions and approval records.
- Audit records.

## Privacy Risks

- Tickets can contain names, emails, phone numbers, device identifiers, credentials, health information, location, or employment context.
- Resumes and job descriptions can contain HR data and protected-characteristic proxies.
- RAG citations and excerpts can over-disclose sensitive content.
- Audit logs can accidentally preserve secrets if raw ticket text is logged.
- Vector indexes can retain sensitive text after source documents are removed unless retention and deletion are implemented.

## Implemented Privacy Controls

- Sample repository data is sanitized and synthetic.
- Ticket-derived summaries and final answers redact secret-like text.
- Audit metadata redacts sensitive patterns before storage.
- API workflow responses exclude raw ticket payloads.
- Retrieval responses exclude full internal chunks.
- Absolute local source paths are excluded from serialized metadata.
- Retrieval query text is redacted before being placed in response-visible state.
- Ingestion is scoped to the local project root to prevent accidental indexing of unrelated files.
- The application documents that retrieved content is evidence, not trusted instruction.

## Human Resources Data Handling

The application may ingest resumes and job descriptions only as contextual support material. It is not a hiring decision system, candidate ranking tool, protected-characteristic inference tool, or employment-screening authority.

Before production use with HR-adjacent data:

- Confirm lawful basis and internal policy approval.
- Minimize collected resume/job data to the actual support purpose.
- Restrict access by role.
- Define retention and deletion timelines.
- Avoid protected-characteristic inference, candidate scoring, or automated employment decisions.
- Provide user notice and consent where required.

## Retention and Deletion Assumptions

Current MVP:

- Uses local files and in-memory approval/audit services.
- Does not implement long-term retention controls.
- Does not implement deletion propagation from vector indexes.

Production requirement:

- Define retention schedules for tickets, documents, chunks, indexes, audit records, and approval records.
- Provide deletion/re-indexing workflows.
- Encrypt stored data at rest.
- Separate environments and tenants.
- Avoid logging secrets and raw private documents.

## Privacy Validation Results

Security/privacy tests confirmed:

- Raw `ticket` is not serialized in workflow responses.
- Secret-like value `Summer2026` is not present in serialized workflow or FastAPI analyze responses.
- `source_path` is not serialized.
- Full internal `chunk` objects are not serialized.
- Status output does not expose absolute sample document paths.
- Path ingestion outside the project root is rejected.

## Residual Privacy Risks

- Local demo has no authentication or role-based access control.
- In-memory audit and approval records are not durable or governed by retention policy.
- Vector-store deletion and re-indexing workflows are not yet implemented.
- Citation excerpts may still contain sensitive business context if real documents are ingested without preprocessing.
- Production logging, telemetry, and external model-provider data use need separate review.

## Privacy Decision

Phase 7 passes for sanitized local MVP operation. Real private tickets, resumes, job descriptions, or internal KBs require an approved production privacy design before use.
