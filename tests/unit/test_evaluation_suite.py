from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from itsupport_copilot.app_services.bootstrap import create_app_container
from itsupport_copilot.evals.runner import EvaluationRunner
from itsupport_copilot.evals.schemas import EvaluationCase, EvaluationCategory


REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_CASES = REPO_ROOT / "evals" / "cases" / "support_eval_cases.json"


class EvaluationSuiteTests(unittest.TestCase):
    def test_eval_cases_have_required_fields_and_categories(self) -> None:
        payload = json.loads(EVAL_CASES.read_text(encoding="utf-8"))
        cases = [EvaluationCase.model_validate(item) for item in payload]

        self.assertGreaterEqual(len(cases), 7)
        categories = {category for case in cases for category in case.categories}
        required = {
            EvaluationCategory.HALLUCINATION,
            EvaluationCategory.UNSAFE_COMMAND,
            EvaluationCategory.BAD_RETRIEVAL,
            EvaluationCategory.PROMPT_INJECTION,
            EvaluationCategory.CITATION_CORRECTNESS,
            EvaluationCategory.CLASSIFICATION_ACCURACY,
            EvaluationCategory.ANSWER_QUALITY,
            EvaluationCategory.KB_GENERATION,
            EvaluationCategory.APPROVAL_WORKFLOW,
        }
        self.assertTrue(required.issubset(categories))
        for case in cases:
            self.assertTrue(case.expected_behavior)
            self.assertTrue(case.unacceptable_behavior)
            self.assertTrue(case.scoring_rubric)
            self.assertGreaterEqual(case.pass_threshold, 0.85)

    def test_default_evaluation_suite_passes(self) -> None:
        container = create_app_container(REPO_ROOT)
        report = EvaluationRunner(container).run_path(EVAL_CASES)

        self.assertTrue(report.passed, report.model_dump_json(indent=2))
        self.assertEqual(report.failed_cases, 0)
        self.assertEqual(report.total_cases, 7)
        self.assertGreaterEqual(report.score, 0.95)

    def test_eval_runner_cli_returns_json_report(self) -> None:
        env = {**os.environ, "PYTHONPATH": "src"}
        completed = subprocess.run(
            [sys.executable, "-m", "itsupport_copilot.evals.runner"],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        report = json.loads(completed.stdout)
        self.assertTrue(report["passed"])
        self.assertEqual(report["failed_cases"], 0)


if __name__ == "__main__":
    unittest.main()
