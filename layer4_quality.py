"""
PRISM-LLM Layer 4: Evidence Quality Reasoning Engine
Chain-of-thought RoB 2 / ROBINS-I + GRADE certainty estimation.
"""

from typing import Optional
from loguru import logger
from src.utils.llm_client import LLMClient


class RoBCoTAssessor:
    """Chain-of-thought risk-of-bias assessment."""

    ROB2_DOMAINS = [
        "randomisation_process",
        "deviations_from_intervention",
        "missing_outcome_data",
        "measurement_of_outcome",
        "selection_of_reported_result",
    ]

    ROBINS_I_DOMAINS = [
        "confounding",
        "selection_of_participants",
        "classification_of_interventions",
        "deviations_from_intended",
        "missing_data",
        "measurement_of_outcomes",
        "selection_of_reported_result",
    ]

    COT_SYSTEM = (
        "You are a Cochrane-trained risk-of-bias assessor. "
        "Assess this periodontal regeneration study using a chain-of-thought approach. "
        "For the specified domain:\n"
        "STEP 1: Extract relevant methodology text\n"
        "STEP 2: Identify signalling questions for this domain\n"
        "STEP 3: Reason through each question with evidence\n"
        "STEP 4: Assign judgment: Low / Some concerns / High\n"
        "STEP 5: Provide justification citing source text\n"
        "Return ONLY valid JSON: "
        '{"judgment":"Low" or "Some concerns" or "High","justification":"brief"}'
    )

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def assess(self, extraction: dict, methods_text: str) -> dict:
        """Perform domain-by-domain RoB assessment."""
        design = extraction.get("study_design", "").lower()
        is_rct = any(k in design for k in ["rct", "randomis", "randomiz"])
        tool = "RoB2" if is_rct else "ROBINS-I"
        domains = self.ROB2_DOMAINS if is_rct else self.ROBINS_I_DOMAINS

        assessment = {"tool": tool, "domains": {}}
        for domain in domains:
            prompt = f"Domain: {domain.replace('_', ' ')}\n\nMethods text:\n{methods_text[:3000]}"
            result = self.llm.generate(self.COT_SYSTEM, prompt)
            assessment["domains"][domain] = {
                "judgment": result.get("judgment", "Some concerns"),
                "justification": result.get("justification", ""),
            }

        # Compute overall
        judgments = [d["judgment"] for d in assessment["domains"].values()]
        if any(j == "High" for j in judgments):
            overall = "High"
        elif any(j == "Some concerns" for j in judgments):
            overall = "Some concerns"
        else:
            overall = "Low"
        assessment["overall"] = {"judgment": overall}

        return assessment


class GRADECertaintyEstimator:
    """GRADE evidence certainty assessment."""

    DOMAINS = [
        "risk_of_bias", "inconsistency", "indirectness",
        "imprecision", "publication_bias",
    ]

    SYSTEM = (
        "You are a GRADE certainty assessor. Evaluate the certainty of evidence "
        "across 5 GRADE domains. Return ONLY valid JSON: "
        '{"certainty":"High" or "Moderate" or "Low" or "Very low",'
        '"domains":{"risk_of_bias":"no concern" or "serious" or "very serious",'
        '"inconsistency":"...","indirectness":"...","imprecision":"...","publication_bias":"..."}}'
    )

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def estimate(self, extractions: list, rob_assessments: list) -> dict:
        summary = f"Based on {len(extractions)} studies, "
        n_low = sum(
            1 for r in rob_assessments
            if r.get("overall", {}).get("judgment") == "Low"
        )
        summary += f"{n_low} at low RoB, "
        summary += f"designs: {set(e.get('study_design','') for e in extractions)}"

        result = self.llm.generate(self.SYSTEM, summary)
        if "_error" in result or "_raw" in result:
            return {"certainty": "Moderate", "domains": {}}
        return result


class QualityEngine:
    """Layer 4: Complete quality assessment pipeline."""

    def __init__(self, config: Optional[dict] = None, llm_client: Optional[LLMClient] = None):
        self.config = config or {}
        self.llm = llm_client or LLMClient(self.config.get("llm", {}))
        self.rob_assessor = RoBCoTAssessor(self.llm)
        self.grade_estimator = GRADECertaintyEstimator(self.llm)

    def execute(
        self, extractions: list[dict], papers: list[dict]
    ) -> tuple[list[dict], dict]:
        """Assess quality for all included studies."""
        logger.info("=" * 60)
        logger.info("LAYER 4: EVIDENCE QUALITY REASONING ENGINE")
        logger.info("=" * 60)

        rob_assessments = []
        for i, (ext, paper) in enumerate(zip(extractions, papers)):
            methods = paper.get("methods_text", paper.get("full_text", ""))
            assessment = self.rob_assessor.assess(ext, methods)
            rob_assessments.append(assessment)

            if (i + 1) % 20 == 0:
                logger.info(f"  Assessed {i + 1}/{len(extractions)}...")

        grade = self.grade_estimator.estimate(extractions, rob_assessments)

        n_low = sum(
            1 for a in rob_assessments
            if a.get("overall", {}).get("judgment") == "Low"
        )
        logger.info(
            f"  RoB: {len(rob_assessments)} assessed | "
            f"Low: {n_low} | GRADE: {grade.get('certainty', 'N/A')}"
        )
        return rob_assessments, grade
