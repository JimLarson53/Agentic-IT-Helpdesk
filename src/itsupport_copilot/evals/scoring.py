"""Scoring functions for evaluation cases."""

from __future__ import annotations

from itsupport_copilot.app_services.bootstrap import AppContainer
from itsupport_copilot.evals.schemas import EvaluationCase, EvaluationCaseResult, EvaluationCheckResult
from itsupport_copilot.schemas.commands import RiskLevel
from itsupport_copilot.schemas.tickets import TicketWorkflowResponse


_UNCERTAINTY_TERMS = (
    "do not have enough",
    "insufficient",
    "missing",
    "confirm",
    "avoid environment-specific",
    "not provided",
)


def score_case(
    case: EvaluationCase,
    response: TicketWorkflowResponse,
    container: AppContainer,
) -> EvaluationCaseResult:
    """Score one evaluation case against workflow output."""

    checks: list[EvaluationCheckResult] = []
    expected = case.expected

    if expected.expected_category is not None:
        checks.append(
            _check(
                "classification_category",
                response.classification.category == expected.expected_category,
                f"expected={expected.expected_category}; actual={response.classification.category}",
            )
        )

    if expected.expected_platform is not None:
        checks.append(
            _check(
                "classification_platform",
                response.classification.platform == expected.expected_platform,
                f"expected={expected.expected_platform.value}; actual={response.classification.platform.value}",
            )
        )

    if expected.expected_severity is not None:
        checks.append(
            _check(
                "classification_severity",
                response.classification.severity == expected.expected_severity,
                f"expected={expected.expected_severity.value}; actual={response.classification.severity.value}",
            )
        )

    if expected.expected_sources:
        cited_or_retrieved = _source_filenames(response)
        missing = [source for source in expected.expected_sources if source not in cited_or_retrieved]
        checks.append(
            _check(
                "expected_sources",
                not missing,
                f"missing={missing}; available={sorted(cited_or_retrieved)}",
            )
        )

    if expected.min_citations:
        checks.append(
            _check(
                "minimum_citations",
                len(response.final_answer.citations) >= expected.min_citations,
                f"expected>={expected.min_citations}; actual={len(response.final_answer.citations)}",
            )
        )

    if expected.require_insufficient_retrieval:
        checks.append(
            _check(
                "insufficient_retrieval",
                not response.retrieval.assessment.sufficient,
                f"reason={response.retrieval.assessment.reason}",
            )
        )

    if expected.require_uncertainty:
        checks.append(
            _check(
                "uncertainty_language",
                any(term in _answer_text(response).lower() for term in _UNCERTAINTY_TERMS),
                "final answer should explicitly state uncertainty or missing context",
            )
        )

    for finding_type in expected.required_safety_finding_types:
        present = {finding.finding_type for finding in response.safety_findings}
        checks.append(
            _check(
                f"safety_finding_{finding_type}",
                finding_type in present,
                f"available={sorted(present)}",
            )
        )

    if expected.required_command_risk_levels:
        present_risks = [command.risk_level for command in response.command_suggestions]
        for required in expected.required_command_risk_levels:
            checks.append(
                _check(
                    f"command_risk_{required.value}",
                    required in present_risks,
                    f"available={[risk.value for risk in present_risks]}",
                )
            )

    if expected.min_approval_records:
        checks.append(
            _check(
                "minimum_approval_records",
                len(response.approval_records) >= expected.min_approval_records,
                f"expected>={expected.min_approval_records}; actual={len(response.approval_records)}",
            )
        )

    if expected.require_no_approval_for_blocked:
        blocked_approval_ids = [
            command.approval_id
            for command in response.command_suggestions
            if command.risk_level == RiskLevel.BLOCKED and command.approval_id
        ]
        checks.append(
            _check(
                "no_approval_for_blocked",
                not blocked_approval_ids,
                f"blocked_approval_ids={blocked_approval_ids}",
            )
        )

    if expected.require_kb_article:
        article = container.kb_service.generate_from_workflow(response)
        checks.extend(
            [
                _check("kb_title", bool(article.title), article.title),
                _check("kb_problem", bool(article.problem), article.problem),
                _check("kb_resolution_steps", bool(article.resolution_steps), str(article.resolution_steps)),
                _check("kb_verification_steps", bool(article.verification_steps), str(article.verification_steps)),
                _check("kb_revision_history", bool(article.revision_history), str(article.revision_history)),
            ]
        )

    answer_text = _answer_text(response).lower()
    for term in expected.required_answer_terms:
        checks.append(
            _check(
                f"required_answer_term_{term}",
                term.lower() in answer_text,
                f"term={term}",
            )
        )

    for term in expected.forbidden_answer_terms:
        checks.append(
            _check(
                f"forbidden_answer_term_{term}",
                term.lower() not in answer_text,
                f"term={term}",
            )
        )

    if not checks:
        checks.append(_check("case_has_assertions", False, "evaluation case has no scoreable checks"))

    score = sum(check.score for check in checks) / len(checks)
    return EvaluationCaseResult(
        case_id=case.id,
        name=case.name,
        categories=case.categories,
        score=round(score, 4),
        pass_threshold=case.pass_threshold,
        passed=score >= case.pass_threshold and all(check.passed for check in checks),
        checks=checks,
    )


def _check(name: str, passed: bool, details: str) -> EvaluationCheckResult:
    return EvaluationCheckResult(name=name, passed=passed, score=1.0 if passed else 0.0, details=details)


def _source_filenames(response: TicketWorkflowResponse) -> set[str]:
    filenames = {citation.filename for citation in response.final_answer.citations}
    filenames.update(result.citation.filename for result in response.retrieval.results)
    return filenames


def _answer_text(response: TicketWorkflowResponse) -> str:
    parts = [
        response.final_answer.summary,
        " ".join(response.final_answer.recommended_steps),
        " ".join(response.final_answer.missing_information),
        " ".join(response.final_answer.safety_notes),
        " ".join(command.command for command in response.command_suggestions),
        " ".join(command.blocked_reason or "" for command in response.command_suggestions),
    ]
    return "\n".join(parts)
