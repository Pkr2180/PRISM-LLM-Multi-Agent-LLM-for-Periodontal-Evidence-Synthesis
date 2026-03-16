"""
PRISM-LLM: Cross-Database Deduplication
DOI exact matching + fuzzy title similarity (Levenshtein >= 0.92).
"""

import hashlib
from typing import Optional
from loguru import logger

try:
    from Levenshtein import ratio as levenshtein_ratio
except ImportError:
    from difflib import SequenceMatcher

    def levenshtein_ratio(s1: str, s2: str) -> float:
        return SequenceMatcher(None, s1, s2).ratio()


def deduplicate_records(
    records: list[dict],
    threshold: float = 0.92,
) -> list[dict]:
    """
    Deduplicate records using DOI exact match + fuzzy title similarity.

    Args:
        records: List of record dictionaries with 'doi' and 'title' keys.
        threshold: Levenshtein similarity threshold for title matching.

    Returns:
        Deduplicated list of records.
    """
    seen_dois: set[str] = set()
    seen_titles: dict[str, str] = {}
    unique: list[dict] = []

    for record in records:
        doi = record.get("doi", "").strip().lower()
        title = record.get("title", "").strip().lower()

        # Phase 1: DOI exact match
        if doi and doi in seen_dois:
            continue
        if doi:
            seen_dois.add(doi)

        # Phase 2: Fuzzy title match
        is_duplicate = False
        for existing_title in seen_titles.values():
            if levenshtein_ratio(title, existing_title) >= threshold:
                is_duplicate = True
                break

        if not is_duplicate and title:
            key = hashlib.md5(title.encode()).hexdigest()[:16]
            seen_titles[key] = title
            unique.append(record)

    n_removed = len(records) - len(unique)
    logger.info(f"Deduplication: {len(records)} -> {len(unique)} unique ({n_removed} removed)")
    return unique
