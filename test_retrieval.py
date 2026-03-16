"""Tests for Layer 1: Ontology-Aware Retrieval"""

import pytest
from src.utils.mesh_ontology import PerioMeSHOntology


class TestMeSHOntology:
    def test_expansion_adds_children(self):
        terms = ["periodontitis"]
        expanded = PerioMeSHOntology.expand_query(terms)
        assert "chronic_periodontitis" in expanded
        assert "aggressive_periodontitis" in expanded

    def test_expansion_adds_related(self):
        terms = ["periodontitis"]
        expanded = PerioMeSHOntology.expand_query(terms)
        assert "alveolar_bone_loss" in expanded

    def test_expansion_preserves_original(self):
        terms = ["periodontitis", "custom_term"]
        expanded = PerioMeSHOntology.expand_query(terms)
        assert "periodontitis" in expanded
        assert "custom_term" in expanded

    def test_expansion_unknown_term(self):
        terms = ["unknown_xyz"]
        expanded = PerioMeSHOntology.expand_query(terms)
        assert expanded == ["unknown_xyz"]

    def test_mesh_id_lookup(self):
        assert PerioMeSHOntology.get_mesh_id("periodontitis") == "D010518"
        assert PerioMeSHOntology.get_mesh_id("unknown") is None

    def test_icd_codes(self):
        codes = PerioMeSHOntology.get_icd_codes(["periodontitis"])
        assert any("K05" in c for c in codes)

    def test_intrabony_expansion(self):
        expanded = PerioMeSHOntology.expand_query(["intrabony_defect"])
        assert "one_wall" in expanded
        assert "three_wall" in expanded
