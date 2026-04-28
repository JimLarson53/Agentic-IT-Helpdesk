"""Evaluation runner for Secure Agentic IT Support Copilot."""

from __future__ import annotations

import json
from pathlib import Path

from itsupport_copilot.app_services.bootstrap import AppContainer, create_app_container
from itsupport_copilot.evals.schemas import EvaluationCase, EvaluationReport
from itsupport_copilot.evals.scoring import score_case


DEFAULT_CASES_PATH = Path(__file__).resolve().parents[3] / "evals" / "cases" / "support_eval_cases.json"


class EvaluationRunner:
    """Load and run evaluation cases against the local app container."""

    def __init__(self, container: AppContainer) -> None:
        self.container = container

    def load_cases(self, path: str | Path = DEFAULT_CASES_PATH) -> list[EvaluationCase]:
        source = Path(path)
        payload = json.loads(source.read_text(encoding="utf-8"))
        return [EvaluationCase.model_validate(item) for item in payload]

    def run_cases(self, cases: list[EvaluationCase]) -> EvaluationReport:
        results = []
        for case in cases:
            response = self.container.runner.run(case.ticket)
            results.append(score_case(case, response, self.container))

        passed_cases = sum(1 for result in results if result.passed)
        total_cases = len(results)
        score = sum(result.score for result in results) / total_cases if total_cases else 0.0
        return EvaluationReport(
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=total_cases - passed_cases,
            score=round(score, 4),
            passed=passed_cases == total_cases,
            results=results,
        )

    def run_path(self, path: str | Path = DEFAULT_CASES_PATH) -> EvaluationReport:
        return self.run_cases(self.load_cases(path))


def run_default_evaluations(project_root: str | Path | None = None) -> EvaluationReport:
    container = create_app_container(project_root)
    return EvaluationRunner(container).run_path()


def main() -> int:
    report = run_default_evaluations()
    print(report.model_dump_json(indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
