"""
PRISM-LLM Layer 3: Structured Clinical Extraction Module
Schema-enforced PICO-Perio parsing with numerical grounding.
"""

from typing import Optional
from loguru import logger
from src.utils.llm_client import LLMClient
from src.utils.numerical_grounding import verify_extraction


class PICOPerioParser:
    """JSON-mode constrained extraction using PICO-Perio schema."""

    SYSTEM_PROMPT = (
        "You are a periodontal data extractor for the PRISM-LLM system. "
        "Extract structured data from this study into STRICT JSON matching the PICO-Perio schema. "
        "Return ONLY valid JSON with no markdown formatting. "
        "If a value is not reported in the text, use null. "
        "REQUIRED FIELDS: study_id, title, authors, year, journal, country, study_design, "
        "sample_size_patients, sample_size_defects, follow_up_months, "
        "intervention_category, intervention_detail, comparator, "
        "defect_types (list), defect_depth_mm, "
        "cal_gain_mm, cal_gain_sd, pd_reduction_mm, pd_reduction_sd, "
        "bone_fill_pct, bone_fill_sd, adverse_events"
    )

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def extract(self, text: str) -> dict:
        result = self.llm.generate(self.SYSTEM_PROMPT, text[:8000])
        if "_error" in result:
            logger.error(f"Extraction failed: {result['_error']}")
            return {}
        return result


class DefectTaxonomyClassifier:
    """Multi-label classifier for defect type and morphology."""

    SYSTEM_PROMPT = (
        "Classify the periodontal defect from this text. "
        "Return a JSON list of applicable types from: "
        "intrabony_1wall, intrabony_2wall, intrabony_3wall, intrabony_combination, "
        "furcation_class_I, furcation_class_II, furcation_class_III, "
        "supra_alveolar, combined. "
        "Return ONLY a JSON array."
    )

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def classify(self, text: str) -> list[str]:
        result = self.llm.generate(self.SYSTEM_PROMPT, text[:2000])
        if isinstance(result, list):
            return result
        return result.get("_raw", "").strip("[]").split(",") if "_raw" in result else []


class ExtractionModule:
    """Layer 3: Complete extraction pipeline with verification."""

    def __init__(self, config: Optional[dict] = None, llm_client: Optional[LLMClient] = None):
        self.config = config or {}
        self.llm = llm_client or LLMClient(self.config.get("llm", {}))
        self.parser = PICOPerioParser(self.llm)
        self.classifier = DefectTaxonomyClassifier(self.llm)
        self.max_retries = self.config.get("max_retries", 2)

    def execute(self, papers: list[dict]) -> list[dict]:
        """Extract structured data from all papers with verification."""
        logger.info("=" * 60)
        logger.info("LAYER 3: STRUCTURED CLINICAL EXTRACTION")
        logger.info("=" * 60)

        extractions = []
        for i, paper in enumerate(papers):
            text = paper.get("full_text", paper.get("abstract", ""))

            # Extract
            extraction = self.parser.extract(text)

            # Numerical grounding
            verified, flags = verify_extraction(extraction)
            if not verified and self.max_retries > 0:
                logger.warning(f"  Paper {i}: {len(flags)} flags -> re-extracting")
                extraction = self.parser.extract(text)
                verified, flags = verify_extraction(extraction)

            extraction["numerical_grounding_verified"] = verified
            extraction["hallucination_flags"] = flags

            # Defect classification
            defect_text = extraction.get("intervention_detail", "")
            if defect_text:
                extraction["defect_types"] = self.classifier.classify(defect_text)

            extractions.append(extraction)

            if (i + 1) % 20 == 0:
                logger.info(f"  Extracted {i + 1}/{len(papers)}...")

        n_verified = sum(1 for e in extractions if e.get("numerical_grounding_verified"))
        logger.info(f"  Extracted: {len(extractions)} | Verified: {n_verified}/{len(extractions)}")
        return extractions
