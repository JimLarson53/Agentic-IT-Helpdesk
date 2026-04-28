# Data Inventory and Privacy Requirements

Date: 2026-04-25
Phase: 1 - Discovery, Research, and Requirements

## Data Inventory

### Ticket Data

Examples:
- Ticket title and description.
- Affected user, device, hostname, application, service, network, or site.
- Symptoms, error messages, screenshots transcribed by users, attempted fixes.
- Severity, urgency, impact, and timestamps.

Sensitivity:
- May contain names, work emails, phone numbers, IP addresses, hostnames, business-sensitive incidents, secrets pasted by mistake, and security incident details.

MVP handling:
- Use sanitized fixtures only.
- Redact likely secrets before logging.
- Store audit metadata, not full sensitive payloads unless required for local demo behavior.

### IT Documentation and Troubleshooting Notes

Examples:
- Runbooks.
- SOPs.
- KB articles.
- Known error records.
- Network and application support notes.

Sensitivity:
- May contain internal architecture, hostnames, access patterns, operational workarounds, and security controls.

MVP handling:
- Treat as untrusted evidence.
- Do not allow retrieved text to become instructions.
- Use source metadata and citations.

### Resumes

Examples:
- Candidate experience.
- Skills.
- Certifications.
- Employment history.
- Contact information.

Sensitivity:
- Personal data and HR-related data. May contain protected or sensitive attributes.

MVP handling:
- Use synthetic resume fixtures only.
- Do not rank candidates or make hiring recommendations.
- Do not infer protected characteristics.
- Retrieve resume content only as contextual evidence when explicitly relevant.

### Job Descriptions

Examples:
- Role requirements.
- Skills.
- Technologies.
- Work location.
- Compensation or department information.

Sensitivity:
- Usually lower than resumes but can include internal workforce plans or confidential hiring context.

MVP handling:
- Use synthetic fixtures.
- Treat as contextual reference material.

### Command Suggestions

Examples:
- PowerShell diagnostic commands.
- Bash diagnostic commands.
- System state inspection.
- Service status checks.

Sensitivity:
- Commands can reveal system structure or cause harm if executed.

MVP handling:
- Store suggested commands with risk classification and approval status.
- Never execute commands automatically.
- Block unsafe patterns or require explicit high-risk review.

### Approval Records

Required fields:
- Proposed action.
- Action type.
- Risk level.
- Rationale.
- Affected system or data.
- Approving human.
- Timestamp.
- Approval status: pending, approved, rejected, expired.
- Execution status if execution is ever implemented.

Sensitivity:
- Audit records can reveal incidents and internal systems.

MVP handling:
- SQLite local audit log.
- Redact secrets and avoid unnecessary full-ticket retention.

### Evaluation Fixtures

Examples:
- Synthetic tickets.
- Synthetic documents.
- Malicious prompt-injection snippets.
- Unsafe command requests.
- Bad retrieval cases.

Sensitivity:
- Should contain no real customer or employee data.

MVP handling:
- Commit sanitized fixtures to repository.
- Make adversarial content clearly marked as test data.

## Privacy Requirements

- Identify likely PII and secrets in ticket text, resumes, logs, and retrieved sources.
- Minimize stored personal data.
- Do not log secrets or credentials.
- Provide `.env.example` with no real secrets.
- Document data-retention assumptions.
- Support local deletion/reset of demo data.
- Keep retrieved sensitive snippets out of audit logs unless explicitly needed.
- Cite sources without exposing unnecessary sensitive content.
- Document that production deployments require organization-specific privacy/legal review.

## Secret and Credential Handling

Must redact or flag:
- API keys.
- Passwords.
- Private keys.
- OAuth tokens.
- Session cookies.
- Connection strings.
- Cloud access keys.
- SSH keys.
- Windows credential material.

The assistant must not ask users to paste secrets. If a ticket contains a secret, the response should recommend rotation and removal from the ticketing system according to organization policy.

## Prompt Injection and Untrusted Data Handling

Untrusted inputs:
- User tickets.
- Retrieved documents.
- Resumes.
- Job descriptions.
- KB articles.
- Troubleshooting notes.

Required behavior:
- Treat untrusted content as data, not instructions.
- Detect suspicious phrases such as requests to ignore policy, reveal secrets, disable safety checks, exfiltrate context, or execute commands.
- Down-rank or flag malicious chunks.
- Continue with safe evidence extraction when possible.
- Refuse or escalate when retrieved content attempts to override policy or approval controls.

## Retention Assumptions

MVP:
- Sample documents and generated local data remain on the developer machine.
- Audit logs are stored locally in SQLite.
- The app will document how to clear local data.
- The repository will not contain private data.

Production hardening:
- Retention periods must be configurable.
- Organizations must define deletion, export, legal hold, access control, and breach procedures.
- Jurisdiction-specific review is required before processing real HR or ticket data.

## Compliance Assumptions

- Primary launch context is the United States.
- GDPR concepts are used as privacy engineering references when personal data is involved, especially if EU resident data may be processed.
- State privacy laws, sector rules, employment law, union or works-council obligations, and customer contract requirements are not fully assessed in Phase 1.
- Qualified legal/privacy professionals must review production use.

## Acceptance Criteria

- Every corpus type has a documented sensitivity profile.
- Logs do not intentionally store secrets.
- Sample data is synthetic.
- Prompt injection is treated as a required safety case.
- Approval records are auditable.
- Real resumes and tickets are excluded from repository artifacts.
