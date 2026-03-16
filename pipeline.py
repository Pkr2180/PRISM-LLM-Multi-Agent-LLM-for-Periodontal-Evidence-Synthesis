"""
PRISM-LLM: Main Pipeline Orchestrator
Coordinates all 5 layers in a PRISMA 2020-compliant workflow.
"""

import json
import time
from typing import Optional
from loguru import logger

from src.layers.layer1_retrieval import OntologyAwareRetrievalEngine
from src.layers.layer2_screening import ScreeningPipeline
from src.layers.layer3_extraction import ExtractionModule
from src.layers.layer4_quality import QualityEngine
from src.layers.layer5_synthesis import SynthesisEngine
from src.utils.llm_client import LLMClient
from src.utils.export import export_json, export_prisma_flow


class PRISMPipeline:
    """
    PRISM-LLM: 5-Layer Hierarchical Multi-Agent Pipeline.

    Usage:
        pipeline = PRISMPipeline(config_path="configs/config.yaml")
        results = pipeline.run()
    """

    def __init__(
        self,
        config: Optional[dict] = None,
        config_path: Optional[str] = None,
    ):
        if config_path:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
        self.config = config or {}

        # Initialize LLM client
        self.llm = LLMClient(self.config.get("llm", {}))

        # Initialize layers
        self.layer1 = OntologyAwareRetrievalEngine(self.config.get("retrieval", {}))
        self.layer2 = ScreeningPipeline(self.config.get("screening", {}), self.llm)
        self.layer3 = ExtractionModule(self.config.get("extraction", {}), self.llm)
        self.layer4 = QualityEngine(self.config.get("quality_assessment", {}), self.llm)
        self.layer5 = SynthesisEngine(self.config.get("synthesis", {}))

    def run(
        self,
        search_blocks: Optional[dict] = None,
        output_dir: Optional[str] = None,
    ) -> dict:
        """Execute the complete PRISM-LLM pipeline."""
        start_time = time.time()

        logger.info("=" * 60)
        logger.info("  PRISM-LLM: Periodontal Regeneration Intelligence")
        logger.info("  for Systematic Meta-benchmarking — v1.0")
        logger.info("=" * 60)

        # Layer 1: Retrieval
        records = self.layer1.execute(search_blocks)

        # Layer 2: Screening
        included, excluded, uncertain = self.layer2.execute(records)

        # Layer 3: Extraction
        extractions = self.layer3.execute(included)

        # Layer 4: Quality Assessment
        rob_assessments, grade = self.layer4.execute(extractions, included)

        # Layer 5: Synthesis
        synthesis = self.layer5.execute(extractions, rob_assessments)

        elapsed = time.time() - start_time

        # Compile results
        results = {
            "pipeline_version": "1.0.0",
            "processing_time_seconds": round(elapsed, 1),
            "counts": {
                "total_retrieved": len(records),
                "after_screening": len(included),
                "excluded": len(excluded),
                "uncertain_reviewed": len(uncertain),
                "final_included": len(extractions),
            },
            "extractions": extractions,
            "rob_assessments": rob_assessments,
            "grade": grade,
            "synthesis": synthesis,
        }

        # Export if output_dir specified
        if output_dir:
            import os
            os.makedirs(output_dir, exist_ok=True)
            export_json(results, f"{output_dir}/results.json")
            export_prisma_flow(
                identified=len(records) + len(excluded),
                after_dedup=len(records),
                screened_out=len(excluded),
                full_text_assessed=len(included),
                excluded_full_text=0,
                included=len(extractions),
                path=f"{output_dir}/prisma_flow.svg",
            )

        logger.info("=" * 60)
        logger.info(f"  PIPELINE COMPLETE in {elapsed:.1f}s")
        logger.info(f"  Retrieved: {len(records)} | Included: {len(extractions)}")
        logger.info(f"  Hallucination rate: {synthesis['hallucination_check']['hallucination_rate_pct']}%")
        logger.info("=" * 60)

        return results

    def process_paper(self, pdf_path: str) -> dict:
        """Process a single paper through layers 3-5."""
        from src.utils.pdf_parser import extract_text_from_pdf

        sections = extract_text_from_pdf(pdf_path)
        paper = {**sections}

        extraction = self.layer3.execute([paper])[0]
        rob, grade = self.layer4.execute([extraction], [paper])
        synthesis = self.layer5.execute([extraction], rob)

        return {
            "extraction": extraction,
            "quality": rob[0] if rob else {},
            "grade": grade,
            "synthesis": synthesis,
        }
