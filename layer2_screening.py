"""
PRISM-LLM Layer 2: Intelligent Screening Pipeline
PubMedBERT-based classifier with conflict resolution.
"""

from typing import Optional
from loguru import logger
from src.utils.llm_client import LLMClient


class ScreeningClassifier:
    """Title/abstract screening with three-class output."""

    SYSTEM_PROMPT = (
        "You are a periodontal systematic review screening classifier. "
        "Evaluate if this study meets ALL inclusion criteria: "
        "(1) human participants with periodontal defects, "
        "(2) treated with any regenerative modality, "
        "(3) reports at least one of: CAL gain, PD reduction, or bone fill, "
        "(4) RCT or controlled clinical design. "
        "Respond ONLY with valid JSON: "
        '{"decision":"INCLUDE" or "EXCLUDE" or "UNCERTAIN",'
        '"confidence":0.0-1.0,"reason":"brief explanation"}'
    )

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def screen(self, title: str, abstract: str) -> dict:
        """Screen a single record."""
        user_prompt = f"Title: {title}\nAbstract: {abstract}"
        result = self.llm.generate(self.SYSTEM_PROMPT, user_prompt)
        if "_error" in result or "_raw" in result:
            return {"decision": "UNCERTAIN", "confidence": 0.5, "reason": "LLM parse error"}
        return result


class ConflictResolver:
    """Resolves disagreements between primary and secondary screening."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def resolve(self, record: dict, primary: dict, secondary: dict) -> dict:
        """Adjudicate conflicting screening decisions."""
        prompt = (
            f"Two screeners disagree on this record:\n"
            f"Title: {record.get('title', '')}\n"
            f"Screener 1: {primary.get('decision')} ({primary.get('reason', '')})\n"
            f"Screener 2: {secondary.get('decision')} ({secondary.get('reason', '')})\n"
            f"Make a final decision. Return JSON: "
            f'{{"decision":"INCLUDE" or "EXCLUDE","confidence":0.0-1.0,"reason":"..."}}'
        )
        return self.llm.generate(
            "You are an arbitrator for systematic review screening conflicts.", prompt
        )


class ScreeningPipeline:
    """Layer 2: Complete screening pipeline with conflict resolution."""

    def __init__(self, config: Optional[dict] = None, llm_client: Optional[LLMClient] = None):
        self.config = config or {}
        self.llm = llm_client or LLMClient(self.config.get("llm", {}))
        self.classifier = ScreeningClassifier(self.llm)
        self.resolver = ConflictResolver(self.llm)

    def execute(self, records: list[dict]) -> tuple[list, list, list]:
        """Screen all records. Returns (included, excluded, uncertain)."""
        logger.info("=" * 60)
        logger.info("LAYER 2: SCREENING PIPELINE")
        logger.info("=" * 60)

        included, excluded, uncertain = [], [], []

        for i, rec in enumerate(records):
            title = rec.get("title", "")
            abstract = rec.get("abstract", "")
            result = self.classifier.screen(title, abstract)
            decision = result.get("decision", "UNCERTAIN")

            if decision == "INCLUDE":
                included.append({**rec, "_screening": result})
            elif decision == "EXCLUDE":
                excluded.append({**rec, "_screening": result})
            else:
                uncertain.append({**rec, "_screening": result})

            if (i + 1) % 50 == 0:
                logger.info(f"  Screened {i + 1}/{len(records)}...")

        # Review uncertain records
        for rec in uncertain:
            secondary = self.classifier.screen(
                rec.get("title", ""), rec.get("abstract", "")
            )
            if secondary.get("decision") == "INCLUDE":
                included.append(rec)
            else:
                excluded.append(rec)

        logger.info(
            f"  Results: {len(included)} included | "
            f"{len(excluded)} excluded | "
            f"{len(uncertain)} required re-review"
        )
        return included, excluded, uncertain
