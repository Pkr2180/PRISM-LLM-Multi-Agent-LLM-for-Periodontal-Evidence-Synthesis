"""Tests for deduplication utility."""

import pytest
from src.utils.deduplication import deduplicate_records


class TestDeduplication:
    def test_doi_dedup(self):
        records = [
            {"doi": "10.1234/a", "title": "Study A"},
            {"doi": "10.1234/a", "title": "Study A"},
            {"doi": "10.5678/b", "title": "Study B"},
        ]
        unique = deduplicate_records(records)
        assert len(unique) == 2

    def test_fuzzy_title_dedup(self):
        records = [
            {"doi": "", "title": "Periodontal regeneration via stem cells"},
            {"doi": "", "title": "Periodontal regeneration via stem cell"},
        ]
        unique = deduplicate_records(records, threshold=0.90)
        assert len(unique) == 1

    def test_different_titles_kept(self):
        records = [
            {"doi": "", "title": "Bone grafts in periodontal therapy"},
            {"doi": "", "title": "Enamel matrix derivatives for regeneration"},
        ]
        unique = deduplicate_records(records)
        assert len(unique) == 2

    def test_empty_records(self):
        assert deduplicate_records([]) == []
