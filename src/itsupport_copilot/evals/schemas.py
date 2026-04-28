"""Schemas for repeatable support-copilot evaluations."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from itsupport_copilot.schemas.commands import RiskLevel
from itsupport_copilot.schemas.tickets import Platform, Severity, TicketInput


class EvaluationCategory(str, Enum):
    HALLUCINATION = "hallucination"
    UNSAFE_COMMAND = "unsafe_command"
    BAD_RETRIEVAL = "bad_retrieval"
    PROMPT_INJECTION = "prompt_injection"
    CITATION_CORRECTNESS = "citation_correctness"
    CLASSIFICATION_ACCURACY = "classification_accuracy"
    ANSWER_QUALITY = "answer_quality"
    KB_GENERATION = "kb_generation"
    APPROVAL_WORKFLOW = "approval_workflow"


class ExpectedSignals(BaseModel):
    expected_category: str | None = None
    expected_platform: Platform | None = None
    expected_severity: Severity | None = None
    expected_sources: list[str] = Field(default_factory=list)
    min_citations: int = 0
    require_insufficient_retrieval: bool = False
    require_uncertainty: bool = False
    required_safety_finding_types: list[str] = Field(default_factory=list)
    required_command_risk_levels: list[RiskLevel] = Field(default_factory=list)
    min_approval_records: int = 0
    require_no_approval_for_blocked: bool = False
    require_kb_article: bool = False
    required_answer_terms: list[str] = Field(default_factory=list)
    forbidden_answer_terms: list[str] = Field(default_factory=list)


class EvaluationCase(BaseModel):
    id: str
    name: str
    categories: list[EvaluationCategory]
    ticket: TicketInput
    expected_behavior: str
    unacceptable_behavior: str
    scoring_rubric: list[str]
    pass_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    expected: ExpectedSignals = Field(default_factory=ExpectedSignals)


class EvaluationCheckResult(BaseModel):
    name: str
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    details: str


class EvaluationCaseResult(BaseModel):
    case_id: str
    name: str
    categories: list[EvaluationCategory]
    score: float = Field(ge=0.0, le=1.0)
    pass_threshold: float
    passed: bool
    checks: list[EvaluationCheckResult]


class EvaluationReport(BaseModel):
    total_cases: int
    passed_cases: int
    failed_cases: int
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    results: list[EvaluationCaseResult]
