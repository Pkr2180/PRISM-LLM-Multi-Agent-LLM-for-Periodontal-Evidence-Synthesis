"""Tests for Layer 3: Extraction & Numerical Grounding"""

import pytest
from src.utils.numerical_grounding import verify_extraction, cross_validate_tables


class TestNumericalGrounding:
    def test_valid_extraction(self):
        ext = {"cal_gain_mm": 3.5, "pd_reduction_mm": 4.0, "bone_fill_pct": 65.0}
        verified, flags = verify_extraction(ext)
        assert verified is True
        assert len(flags) == 0

    def test_implausible_cal(self):
        ext = {"cal_gain_mm": 12.0}
        verified, flags = verify_extraction(ext)
        assert verified is False
        assert any("cal_gain_mm" in f for f in flags)

    def test_implausible_bone_fill(self):
        ext = {"bone_fill_pct": 110.0}
        verified, flags = verify_extraction(ext)
        assert verified is False
        assert any("bone_fill_pct" in f for f in flags)

    def test_implausible_pd(self):
        ext = {"pd_reduction_mm": 15.0}
        verified, flags = verify_extraction(ext)
        assert verified is False

    def test_null_values_pass(self):
        ext = {"cal_gain_mm": None, "pd_reduction_mm": None, "bone_fill_pct": None}
        verified, flags = verify_extraction(ext)
        assert verified is True

    def test_edge_values_pass(self):
        ext = {"cal_gain_mm": 0.0, "bone_fill_pct": 100.0, "follow_up_months": 1}
        verified, flags = verify_extraction(ext)
        assert verified is True

    def test_negative_cal_fails(self):
        ext = {"cal_gain_mm": -1.0}
        verified, flags = verify_extraction(ext)
        assert verified is False

    def test_cross_validation_match(self):
        ext = {"cal_gain_mm": 3.5}
        tbl = {"cal_gain_mm": 3.5}
        discrepancies = cross_validate_tables(ext, tbl)
        assert len(discrepancies) == 0

    def test_cross_validation_mismatch(self):
        ext = {"cal_gain_mm": 3.5}
        tbl = {"cal_gain_mm": 5.0}
        discrepancies = cross_validate_tables(ext, tbl)
        assert len(discrepancies) == 1
