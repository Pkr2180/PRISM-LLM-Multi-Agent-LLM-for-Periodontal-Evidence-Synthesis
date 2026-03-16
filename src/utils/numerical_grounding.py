"""
PRISM-LLM: Numerical Grounding Module
Cross-validates extracted clinical measurements against plausibility bounds.
"""

from typing import Optional

PLAUSIBILITY_BOUNDS = {
    "cal_gain_mm": (0.0, 8.0),
    "pd_reduction_mm": (0.0, 9.0),
    "bone_fill_pct": (0.0, 100.0),
    "bone_fill_sd": (0.0, 50.0),
    "defect_depth_mm": (0.0, 15.0),
    "follow_up_months": (1, 240),
    "sample_size_patients": (1, 2000),
    "sample_size_defects": (1, 5000),
    "mean_age": (18, 95),
    "gingival_recession_change_mm": (-5.0, 5.0),
    "radiographic_bone_gain_mm": (0.0, 12.0),
}


def verify_extraction(extraction: dict) -> tuple[bool, list[str]]:
    """
    Verify extracted numerical values against clinical plausibility bounds.

    Args:
        extraction: Dictionary of extracted PICO-Perio fields.

    Returns:
        Tuple of (all_verified: bool, flags: list of violation descriptions).
    """
    flags = []
    for field, (lo, hi) in PLAUSIBILITY_BOUNDS.items():
        val = extraction.get(field)
        if val is None:
            continue
        try:
            v = float(val)
            if v < lo or v > hi:
                flags.append(
                    f"IMPLAUSIBLE: {field} = {v} (expected range: {lo} to {hi})"
                )
        except (ValueError, TypeError):
            flags.append(f"INVALID_TYPE: {field} = {val} (expected numeric)")
    return len(flags) == 0, flags


def cross_validate_tables(extraction: dict, table_values: dict) -> list[str]:
    """
    Cross-validate extracted values against OCR-parsed table data.

    Args:
        extraction: Main extraction dictionary.
        table_values: Values parsed from paper tables via OCR.

    Returns:
        List of discrepancies found.
    """
    discrepancies = []
    for field in ["cal_gain_mm", "pd_reduction_mm", "bone_fill_pct"]:
        ext_val = extraction.get(field)
        tbl_val = table_values.get(field)
        if ext_val is not None and tbl_val is not None:
            try:
                if abs(float(ext_val) - float(tbl_val)) > 0.5:
                    discrepancies.append(
                        f"MISMATCH: {field} text={ext_val} vs table={tbl_val}"
                    )
            except (ValueError, TypeError):
                pass
    return discrepancies
