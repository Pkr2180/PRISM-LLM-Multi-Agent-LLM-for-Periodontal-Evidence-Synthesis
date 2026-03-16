"""PRISM-LLM: Evidence Gap Schema"""

from pydantic import BaseModel, Field


class EvidenceGap(BaseModel):
    intervention: str = ""
    defect_type: str = ""
    outcome_gap: str = ""
    existing_studies: int = 0
    clinical_importance: float = 0.0
    evidence_scarcity: float = 0.0
    priority_score: float = 0.0
    priority_label: str = "Moderate"

    def compute_priority(self) -> None:
        self.priority_score = self.clinical_importance * self.evidence_scarcity
        if self.priority_score > 5:
            self.priority_label = "Critical"
        elif self.priority_score > 2:
            self.priority_label = "High"
        else:
            self.priority_label = "Moderate"
