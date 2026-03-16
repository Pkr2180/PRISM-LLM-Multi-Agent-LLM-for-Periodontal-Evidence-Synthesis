"""
PRISM-LLM: Periodontal MeSH Ontology Graph
Maps dental concepts using MeSH tree numbers and ICD-DA codes.
"""

from typing import Optional


class PerioMeSHOntology:
    """Periodontal domain MeSH concept graph for query enrichment."""

    CONCEPT_GRAPH = {
        "periodontitis": {
            "mesh_id": "D010518",
            "tree": "C07.465.714.533",
            "children": ["chronic_periodontitis", "aggressive_periodontitis"],
            "related": ["periodontal_diseases", "alveolar_bone_loss"],
        },
        "periodontal_regeneration": {
            "mesh_id": "D014019",
            "tree": "E02.950",
            "children": ["guided_tissue_regeneration", "bone_regeneration"],
            "related": ["tissue_engineering", "wound_healing"],
        },
        "intrabony_defect": {
            "mesh_id": "D016301",
            "tree": "C05.116.198.050",
            "children": ["one_wall", "two_wall", "three_wall", "combination"],
            "related": ["alveolar_bone_loss", "periodontal_pocket"],
        },
        "furcation_defect": {
            "mesh_id": "D005484",
            "tree": "C07.465.714.258",
            "children": ["class_I", "class_II", "class_III"],
            "related": ["molar", "premolar", "tooth_root"],
        },
        "enamel_matrix_derivative": {
            "mesh_id": "D053668",
            "children": [],
            "related": ["emdogain", "amelogenin"],
        },
        "platelet_rich_fibrin": {
            "mesh_id": "C000610891",
            "children": ["L_PRF", "A_PRF", "i_PRF"],
            "related": ["platelet_rich_plasma", "growth_factors"],
        },
        "stem_cell": {
            "mesh_id": "D013234",
            "children": [
                "mesenchymal_stem_cells", "dental_pulp_stem_cells",
                "periodontal_ligament_stem_cells", "induced_pluripotent_stem_cells",
            ],
            "related": ["cell_therapy", "tissue_engineering"],
        },
    }

    ICD_DA_CODES = {
        "K05.2": "Acute periodontitis",
        "K05.3": "Chronic periodontitis",
        "K05.4": "Periodontosis",
        "K08.1": "Loss of teeth due to accident or extraction",
        "K08.2": "Atrophy of edentulous alveolar ridge",
    }

    @classmethod
    def expand_query(cls, terms: list[str]) -> list[str]:
        """Expand query terms using ontology graph relationships."""
        expanded = set(terms)
        for term in terms:
            normalised = term.lower().replace(" ", "_").replace("-", "_")
            if normalised in cls.CONCEPT_GRAPH:
                node = cls.CONCEPT_GRAPH[normalised]
                expanded.update(node.get("children", []))
                expanded.update(node.get("related", []))
        return sorted(expanded)

    @classmethod
    def get_mesh_id(cls, term: str) -> Optional[str]:
        """Look up MeSH ID for a periodontal term."""
        normalised = term.lower().replace(" ", "_").replace("-", "_")
        if normalised in cls.CONCEPT_GRAPH:
            return cls.CONCEPT_GRAPH[normalised].get("mesh_id")
        return None

    @classmethod
    def get_icd_codes(cls, terms: list[str]) -> list[str]:
        """Map terms to relevant ICD-DA codes."""
        codes = []
        for code, desc in cls.ICD_DA_CODES.items():
            if any(t.lower() in desc.lower() for t in terms):
                codes.append(f"{code} ({desc})")
        return codes


def expand_mesh_terms(terms: list[str]) -> list[str]:
    """Convenience function for MeSH expansion."""
    return PerioMeSHOntology.expand_query(terms)
