"""Tests for Pydantic schemas."""

import pytest
from src.schemas.pico_perio import PICOPerioExtraction
from src.schemas.rob_assessment import RoBAssessment, DomainAssessment
from src.schemas.evidence_gap import EvidenceGap


class TestPICOPerioSchema:
    def test_valid_extraction(self):
        ext = PICOPerioExtraction(
            study_id="test", title="Test", year=2024, journal="Test J",
            cal_gain_mm=3.5, pd_reduction_mm=4.0, bone_fill_pct=65.0,
        )
        assert ext.cal_gain_mm == 3.5

    def test_bounds_enforcement(self):
        with pytest.raises(Exception):
            PICOPerioExtraction(
                study_id="test", title="Test", year=2024, journal="Test J",
                cal_gain_mm=20.0,  # Exceeds max of 15
            )

    def test_default_values(self):
        ext = PICOPerioExtraction()
        assert ext.study_id == ""
        assert ext.hallucination_flags == []
        assert ext.numerical_grounding_verified is False


class TestRoBSchema:
    def test_default_assessment(self):
        rob = RoBAssessment(study_id="test")
        assert rob.tool == "RoB2"
        assert rob.overall.judgment == "Some concerns"

    def test_domain_assessment(self):
        domain = DomainAssessment(judgment="Low", justification="Well randomised")
        assert domain.judgment == "Low"


class TestEvidenceGap:
    def test_priority_computation(self):
        gap = EvidenceGap(
            intervention="stem_cell", defect_type="furcation_III",
            clinical_importance=5.0, evidence_scarcity=2.0,
        )
        gap.compute_priority()
        assert gap.priority_score == 10.0
        assert gap.priority_label == "Critical"

    def test_moderate_priority(self):
        gap = EvidenceGap(clinical_importance=1.0, evidence_scarcity=1.0)
        gap.compute_priority()
        assert gap.priority_label == "Moderate"
