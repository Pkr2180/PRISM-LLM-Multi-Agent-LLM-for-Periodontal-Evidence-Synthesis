"""
PRISM-LLM: PICO-Perio Extraction Schema
Pydantic-enforced JSON structure for periodontal regeneration studies.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class DefectType(str, Enum):
    INTRABONY_1WALL = "intrabony_1wall"
    INTRABONY_2WALL = "intrabony_2wall"
    INTRABONY_3WALL = "intrabony_3wall"
    INTRABONY_COMBINATION = "intrabony_combination"
    FURCATION_I = "furcation_class_I"
    FURCATION_II = "furcation_class_II"
    FURCATION_III = "furcation_class_III"
    SUPRA_ALVEOLAR = "supra_alveolar"
    COMBINED = "combined"


class InterventionCategory(str, Enum):
    GTR = "guided_tissue_regeneration"
    BONE_GRAFT = "bone_graft"
    EMD = "enamel_matrix_derivative"
    PRF = "platelet_rich_fibrin"
    PRP = "platelet_rich_plasma"
    GROWTH_FACTOR = "growth_factor"
    STEM_CELL = "stem_cell"
    SCAFFOLD = "scaffold_membrane"
    COMBINATION = "combined_protocol"


class StudyDesign(str, Enum):
    RCT = "randomised_controlled_trial"
    CCT = "controlled_clinical_trial"
    COHORT = "prospective_cohort"
    SPLIT_MOUTH = "split_mouth"
    CASE_SERIES = "case_series"
    REVIEW = "review"


class PICOPerioExtraction(BaseModel):
    """Schema-enforced PICO extraction for periodontal regeneration studies."""

    study_id: str = Field(default="", description="DOI or PMID")
    title: str = Field(default="", description="Study title")
    authors: list[str] = Field(default_factory=list)
    year: int = Field(default=0, ge=0, le=2030)
    journal: str = Field(default="")
    country: str = Field(default="")
    study_design: str = Field(default="")

    sample_size_patients: Optional[int] = Field(None, ge=0)
    sample_size_defects: Optional[int] = Field(None, ge=0)
    mean_age: Optional[float] = Field(None, ge=0, le=120)
    smokers_included: Optional[bool] = None
    diabetes_included: Optional[bool] = None
    follow_up_months: Optional[int] = Field(None, ge=0, le=240)

    intervention_category: str = Field(default="")
    intervention_detail: str = Field(default="")
    membrane_type: str = Field(default="")
    graft_material: str = Field(default="")
    biologic_agent: str = Field(default="")
    surgical_technique: str = Field(default="")

    comparator: str = Field(default="")
    comparator_detail: str = Field(default="")

    cal_gain_mm: Optional[float] = Field(None, ge=0, le=15)
    cal_gain_sd: Optional[float] = Field(None, ge=0)
    pd_reduction_mm: Optional[float] = Field(None, ge=0, le=15)
    pd_reduction_sd: Optional[float] = Field(None, ge=0)
    bone_fill_pct: Optional[float] = Field(None, ge=0, le=100)
    bone_fill_sd: Optional[float] = Field(None, ge=0)
    radiographic_bone_gain_mm: Optional[float] = Field(None, ge=0)

    gingival_recession_change_mm: Optional[float] = None
    tooth_survival: Optional[bool] = None
    adverse_events: Optional[str] = None
    patient_reported_outcomes: Optional[str] = None

    defect_types: list[str] = Field(default_factory=list)
    defect_depth_mm: Optional[float] = Field(None, ge=0, le=20)
    number_of_walls: Optional[str] = None

    extraction_confidence: float = Field(default=0.0, ge=0, le=1)
    numerical_grounding_verified: bool = False
    hallucination_flags: list[str] = Field(default_factory=list)
