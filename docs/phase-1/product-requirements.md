# Secure Agentic IT Support Copilot - Phase 1 Product Requirements

Date: 2026-04-25
Phase: 1 - Discovery, Research, and Requirements
Lead team: Team 1 - Product, ITSM Research, and Requirements
Supporting teams: Team 4 - Safety, Security, and Human Approval; Team 6 - Release, Documentation, Compliance, and GitHub Authority

## Product Scope

Secure Agentic IT Support Copilot is a Python-first assistant for IT support teams. It triages tickets, retrieves relevant support knowledge, drafts grounded troubleshooting guidance, suggests risk-scored PowerShell or Bash commands, generates KB articles, and records human approval before any command, ticket mutation, external action, or automation.

The MVP will be a local-development application suitable for a GitHub repository and demo environment. It will use sanitized sample data only and will document production hardening requirements separately.

## Target Users

- Help desk analysts who need fast triage, summaries, and next-step guidance.
- System administrators who need safe, auditable command suggestions.
- IT support managers who need consistent ticket handling and KB generation.
- Security-conscious IT teams that require approval gates and audit logs.
- Managed service providers that handle repeated support workflows across clients.
- Technical recruiters and IT staffing teams using resumes and job descriptions as contextual material.
- Developers extending the repository.

## Core User Stories

- As a help desk analyst, I can paste a ticket and receive a concise summary, classification, missing-information checklist, and next best action.
- As a sysadmin, I can receive PowerShell or Bash command suggestions with intent, risk, expected output, rollback notes, and approval requirements.
- As a support manager, I can generate a KB article from a resolved issue with cited sources and revision metadata.
- As a security reviewer, I can see whether an answer is grounded in retrieved evidence and whether any retrieved content appears malicious or instruction-like.
- As a privacy-conscious operator, I can understand what sensitive data may be stored, logged, retrieved, or displayed.
- As a developer, I can run tests and evaluation cases for hallucination, unsafe commands, bad retrieval, prompt injection, citations, and answer quality.

## In-Scope Capabilities

- Document ingestion for sanitized IT documentation, troubleshooting notes, internal KB articles, resumes, job descriptions, and sample tickets.
- Metadata-aware chunking with document type, source filename, source location, and sensitivity labels.
- Vector retrieval with citation tracking and retrieval scores.
- Bad-retrieval detection and refusal or uncertainty when evidence is insufficient.
- Required LangGraph flow: intake -> classify -> retrieve -> reason -> draft_solution -> safety_check -> final_answer.
- Ticket summarization.
- Risk-scored PowerShell and Bash command suggestion.
- KB article generation.
- Human approval records for any proposed command, ticket mutation, file operation, external API action, or workflow automation.
- Audit logging.
- Streamlit UI and FastAPI backend unless Phase 2 justifies a narrower UI boundary.
- Repeatable tests and evaluation fixtures.
- GitHub-ready documentation, CI, and demo script.

## Out of Scope for MVP

- Automatic execution of PowerShell or Bash commands.
- Direct production ticket-system mutation.
- Real external API actions against customer systems.
- Authentication, SSO, RBAC, and multi-tenant production authorization beyond documented interfaces and assumptions.
- Real resumes, real tickets, real employee records, real secrets, or proprietary customer documents in the repository.
- Legal compliance certification.

## Research Findings

- NIST SP 800-61 Rev. 3 is the current incident-response reference as of April 2025 and supersedes Rev. 2. It emphasizes incident response as part of broader cybersecurity risk management and focuses on detect, respond, and recover functions supported by preparation activities.
- The NIST Incident Response project describes a lifecycle where Govern, Identify, and Protect support incident response, while Detect, Respond, and Recover form the incident-response activity layer. This supports building workflows that triage, document, respond, recover, and improve rather than only answer ad hoc questions.
- Axelos describes ITIL incident management as minimizing negative incident impact and restoring normal service operation as quickly as possible. The copilot should therefore optimize for clarity, urgency, workaround/resolution guidance, escalation, and service restoration.
- OWASP's 2025 LLM application guidance highlights that LLM applications have distinct security risks as they become embedded in internal operations. Prompt injection, data leakage, insecure output handling, and excessive agency must be treated as product requirements, not late-stage polish.
- NIST AI RMF and the Generative AI Profile support treating AI system behavior as a risk-management lifecycle with measurable trustworthiness, evaluation, monitoring, and governance controls.
- Privacy requirements must treat tickets, resumes, job descriptions, logs, and retrieved text as potentially sensitive. Microsoft GDPR guidance is not the default US launch law, but it is useful for personal-data concepts, data subject requests, DPIA thinking, minimization, retention, and breach-response planning when EU data is in scope.
- NIST Privacy Framework 1.0 provides a technology- and jurisdiction-agnostic privacy risk-management reference. It is appropriate as a baseline for data inventory, minimization, processing purpose, retention assumptions, and privacy risk review.

## Source-Grounded Design Implications

- The product must restore service faster without hiding risk or inventing unsupported answers.
- Retrieved content is evidence, not instruction. System and safety policies must override tickets, documents, resumes, and KB content.
- AI outputs that propose commands require risk classification, human approval, and auditability.
- Answers must cite retrieved sources when retrieval is used.
- When retrieval is weak, contradictory, malicious, or absent, the assistant must say what is missing and provide safe next steps rather than fabricating.
- Personal data needs purpose limitation, minimization, retention controls, and redaction-aware logging.

## Hidden Requirements

- The UI must show why the assistant reached a recommendation: classification, retrieved sources, command risk, and approval status.
- The evaluation suite must include negative tests, not only happy-path tickets.
- The repository must be useful without private data or paid provider credentials.
- The model layer must be replaceable so local demos can run with deterministic or stubbed behavior when provider keys are unavailable.
- Audit logs must not become a secret or PII leak.
- Resumes and job descriptions must be treated as contextual documents, not as a license for automated hiring decisions.
- The command suggester must distinguish "suggest" from "execute" clearly in both schema and UI.
- The product must degrade gracefully when optional dependencies, vector stores, or LLM providers are unavailable.

## Assumptions

- Primary launch context is the United States.
- The repository will be named `secure-agentic-it-support-copilot`, even though the local parent folder is `IT Support Tool`.
- MVP will support local SQLite audit metadata and local vector storage.
- Sample corpora will be synthetic and sanitized.
- Real command execution will remain disabled by default and is not required for MVP completion.
- Any legal, HR, privacy, or employment-policy use must be reviewed by qualified professionals before production deployment.

## Constraints

- Python-first implementation.
- LangGraph required unless Phase 2 identifies and the user approves a materially better alternative.
- Human approval required before any action.
- No secrets in repository.
- No fake or placeholder implementation may be represented as complete.
- No ungrounded final answer when evidence is insufficient.
- No silent retention of sensitive ticket, resume, job, or support data.

## Definition of Done for Product Release

- Clean local setup launches the application using documented commands.
- LangGraph flow works end to end.
- RAG ingestion and retrieval work with sanitized sample documents.
- Retrieved answers include citations.
- Insufficient evidence produces uncertainty or refusal.
- Ticket summarization works.
- Command suggestions are risk-scored and never auto-executed.
- KB article generation works.
- Approval workflow and audit logging exist.
- Evaluation tests cover hallucination, unsafe commands, bad retrieval, prompt injection, citation correctness, classification, and answer quality.
- Tests pass in CI.
- Security, privacy, documentation, and release gates pass.
- Team 6 issues explicit GO.

## Research Sources

- NIST SP 800-61 Rev. 3: https://csrc.nist.gov/pubs/sp/800/61/r3/final
- NIST Incident Response project: https://csrc.nist.gov/projects/incident-response
- Axelos ITIL 4 Practitioner: Incident Management: https://dev2.axelos.com/certifications/itil-service-management/itil-practices-manager/itil-4-specialist-monitor-support-and-fulfil/itil-4-practitioner-incident-management
- OWASP Top 10 for LLM Applications 2025: https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
- OWASP Top 10 2025: https://owasp.org/Top10/2025/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF Generative AI Profile: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- NIST Privacy Framework: https://www.nist.gov/privacy-framework
- Microsoft GDPR overview: https://learn.microsoft.com/en-us/compliance/regulatory/gdpr
