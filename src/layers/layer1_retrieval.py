"""
PRISM-LLM Layer 1: Ontology-Aware Retrieval Engine
Federated search across 5 databases with MeSH periodontal graph injection.
"""

from typing import Optional
from loguru import logger
from src.utils.mesh_ontology import PerioMeSHOntology
from src.utils.deduplication import deduplicate_records
from src.utils.db_connectors import get_all_connectors


class OntologyAwareRetrievalEngine:
    """Layer 1: Ontology-enriched federated retrieval."""

    DEFAULT_SEARCH_BLOCKS = {
        "disease_defect": [
            "periodontitis", "periodontal defect", "intrabony defect",
            "furcation defect", "periodontal osseous defect",
        ],
        "regeneration": [
            "periodontal regeneration", "regenerative therapy",
            "guided tissue regeneration", "bone graft",
            "enamel matrix derivative", "platelet rich fibrin",
            "platelet-rich plasma", "growth factor", "scaffold",
            "membrane", "stem cell",
        ],
        "outcomes": [
            "clinical attachment level", "probing depth",
            "bone fill", "radiographic fill", "regeneration outcome",
        ],
    }

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.connectors = get_all_connectors(self.config)
        self.dedup_threshold = self.config.get("dedup_threshold", 0.92)

    def execute(
        self, search_blocks: Optional[dict] = None
    ) -> list[dict]:
        """Run federated search with ontology expansion and deduplication."""
        logger.info("=" * 60)
        logger.info("LAYER 1: ONTOLOGY-AWARE RETRIEVAL ENGINE")
        logger.info("=" * 60)

        blocks = search_blocks or self.DEFAULT_SEARCH_BLOCKS

        # Expand with MeSH ontology
        expanded_blocks = {}
        for block_name, terms in blocks.items():
            expanded = PerioMeSHOntology.expand_query(terms)
            expanded_blocks[block_name] = expanded
            logger.info(
                f"  {block_name}: {len(terms)} -> {len(expanded)} terms"
            )

        # Map to ICD-DA codes
        all_terms = [t for terms in blocks.values() for t in terms]
        icd_codes = PerioMeSHOntology.get_icd_codes(all_terms)
        if icd_codes:
            logger.info(f"  ICD-DA codes: {icd_codes}")

        # Search each database
        all_records = []
        for db_name, connector in self.connectors.items():
            query = connector.translate_query(expanded_blocks)
            results = connector.search(query)
            all_records.extend(results)
            logger.info(f"  {connector.name}: {len(results)} records")

        # Deduplicate
        unique = deduplicate_records(all_records, self.dedup_threshold)
        logger.info(
            f"  TOTAL: {len(all_records)} -> {len(unique)} unique"
        )
        return unique
