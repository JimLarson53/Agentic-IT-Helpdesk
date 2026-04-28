# Personas and Workflows

Date: 2026-04-25
Phase: 1 - Discovery, Research, and Requirements

## Personas

### Help Desk Analyst

Needs:
- Understand a ticket quickly.
- Identify severity, category, affected system, and missing information.
- Provide safe first-response guidance.
- Escalate with enough context for the next team.

Success looks like:
- Lower time to first useful response.
- Fewer incomplete escalations.
- Clear confidence and evidence boundaries.

### System Administrator

Needs:
- Troubleshooting hypotheses grounded in known environment details.
- Commands that are safe, scoped, explained, reversible where possible, and never auto-executed.
- Separation between diagnostic commands and state-changing commands.

Success looks like:
- Command suggestions are auditable and risk-scored.
- High-risk commands are blocked or require high-risk approval.
- Commands include expected output and rollback or recovery notes.

### IT Support Manager

Needs:
- Consistent ticket triage.
- KB article drafts from resolved work.
- Visibility into quality, safety, and recurring issue patterns.

Success looks like:
- Better KB reuse.
- Fewer repeated escalations.
- Audit logs are useful for review.

### Security Reviewer

Needs:
- Evidence that prompt injection is handled.
- Assurance that retrieved documents cannot override safety rules.
- Command risk taxonomy and approval records.
- Logging that avoids secrets and unnecessary PII.

Success looks like:
- Unsafe outputs are blocked or downgraded to review-only guidance.
- Sensitive data handling is documented and testable.
- Evaluation includes adversarial tickets and malicious documents.

### Technical Recruiter or IT Staffing User

Needs:
- Use resumes and job descriptions as context for IT support staffing or qualification questions.
- Avoid automated employment decisions and sensitive attribute inference.

Success looks like:
- Resume/job-description retrieval is treated as contextual search.
- The product avoids protected-class inference, ranking, or hiring recommendations in MVP.
- Sensitive HR data retention and access limitations are explicit.

### Developer Extender

Needs:
- Clear module boundaries.
- Replaceable model, embedding, and vector-store adapters.
- Tests and evaluation fixtures.
- Documentation that explains safety constraints.

Success looks like:
- Local setup is reproducible.
- CI catches safety regressions.
- Extension points are documented.

## Primary Workflow: Ticket Triage and Draft Solution

1. Analyst enters ticket text, affected user/system, environment, urgency, and known attempted fixes.
2. System validates input and records audit metadata.
3. Agent classifies category, severity, platform, issue type, and whether commands may be useful.
4. RAG retrieves relevant IT docs, KB articles, troubleshooting notes, sample ticket history, resumes, or job descriptions as appropriate.
5. System screens retrieved snippets for prompt-injection indicators and sensitivity.
6. Agent reasons over retrieved evidence and identifies assumptions and missing information.
7. Agent drafts a support response with citations and safe troubleshooting steps.
8. Safety checker evaluates grounding, privacy risk, policy risk, and command risk.
9. Final answer is shown with citations, uncertainty, missing information, and approval requirements.
10. Analyst may record approval or rejection for proposed commands or actions.

## Secondary Workflow: Command Suggestion and Approval

1. User requests troubleshooting help or a ticket indicates a command may be useful.
2. Command suggester proposes PowerShell and/or Bash commands only when helpful.
3. Each command includes shell, intent, command text, risk level, explanation, expected output, rollback/recovery note, and approval requirement.
4. Safety checker blocks or flags destructive, privilege-escalating, credential-exfiltrating, persistence-enabling, security-disabling, or data-erasing commands.
5. Approval record is created with status `pending`.
6. Human approves or rejects the command.
7. MVP records approval only; it does not execute commands.

## Secondary Workflow: KB Article Generation

1. Analyst provides a ticket summary, resolution notes, environment, and optional retrieved sources.
2. System generates a KB article with title, problem, environment, symptoms, root cause if known, resolution, verification, prevention notes, related sources, and revision history metadata.
3. Safety checker verifies citations and flags unsupported claims.
4. Human reviews and approves the KB draft before publication outside the app.

## Secondary Workflow: Corpus Ingestion

1. Authorized developer/operator adds sanitized documents to the sample corpus.
2. Ingestion extracts text and metadata.
3. Chunker creates metadata-aware chunks.
4. Embedding adapter creates embeddings.
5. Vector store indexes chunks with source metadata and sensitivity labels.
6. Retrieval tests verify citations, source display, and bad-retrieval fallback behavior.

## Escalation Workflow

Escalate when:
- Severity is high or critical.
- Evidence suggests security incident, data loss, malware, outage, privileged account compromise, or regulated-data exposure.
- The answer requires missing environment details.
- Commands are high-risk or blocked.
- Retrieved documents conflict or appear malicious.
- The user asks for execution or external action.

Escalation output must include:
- Summary.
- Impact.
- Evidence and citations.
- Attempted fixes.
- Risks.
- Missing information.
- Recommended owner/team.
- Approval status for proposed actions.

## Workflow Acceptance Criteria

- Ticket triage produces category, severity, missing information, and next best action.
- Draft answers show citations when retrieval is used.
- Commands are suggestions only and are never executed automatically.
- Approval records include proposed action, risk, rationale, affected system or data, human, timestamp, and status.
- KB articles include revision metadata and source references.
- Unsafe, unsupported, or privacy-risky cases are surfaced instead of silently answered.
