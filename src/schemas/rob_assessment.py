"""PRISM-LLM: Risk-of-Bias Assessment Schema"""

from pydantic import BaseModel, Field
from enum import Enum


class RoBJudgment(str, Enum):
    LOW = "Low"
    SOME_CONCERNS = "Some concerns"
    HIGH = "High"


class DomainAssessment(BaseModel):
    judgment: str = "Some concerns"
    justification: str = ""
    supporting_quotes: list[str] = Field(default_factory=list)


class RoBAssessment(BaseModel):
    study_id: str = ""
    tool: str = "RoB2"
    domains: dict[str, DomainAssessment] = Field(default_factory=dict)
    overall: DomainAssessment = Field(
        default_factory=lambda: DomainAssessment(judgment="Some concerns")
    )
    grade_certainty: str = "Moderate"
    confidence: float = 0.0
