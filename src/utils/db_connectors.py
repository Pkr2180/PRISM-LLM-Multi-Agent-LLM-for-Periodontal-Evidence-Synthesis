"""
PRISM-LLM: Database API Connectors
Unified interface for PubMed, Scopus, Web of Science, Embase, and CENTRAL.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional
from loguru import logger


class DatabaseConnector(ABC):
    """Abstract base class for database API connectors."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def translate_query(self, concept_blocks: dict[str, list[str]]) -> str:
        ...

    @abstractmethod
    def search(self, query: str, max_results: int = 1000) -> list[dict]:
        ...


class PubMedClient(DatabaseConnector):
    """PubMed/MEDLINE connector via NCBI E-utilities."""

    name = "PubMed"

    def __init__(self, api_key: Optional[str] = None, email: Optional[str] = None):
        self.api_key = api_key or os.getenv("PUBMED_API_KEY")
        self.email = email or os.getenv("PUBMED_EMAIL", "researcher@example.com")

    def translate_query(self, concept_blocks: dict[str, list[str]]) -> str:
        parts = []
        for block_name, terms in concept_blocks.items():
            field_terms = [f'"{t}"[Title/Abstract]' for t in terms]
            parts.append(f"({' OR '.join(field_terms)})")
        return " AND ".join(parts)

    def search(self, query: str, max_results: int = 1000) -> list[dict]:
        logger.info(f"PubMed search: {query[:80]}...")
        try:
            from Bio import Entrez

            Entrez.email = self.email
            if self.api_key:
                Entrez.api_key = self.api_key

            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            results = Entrez.read(handle)
            handle.close()

            pmids = results.get("IdList", [])
            logger.info(f"  PubMed returned {len(pmids)} records")

            # Fetch details for each PMID
            if pmids:
                handle = Entrez.efetch(
                    db="pubmed", id=",".join(pmids[:100]), rettype="xml"
                )
                records = Entrez.read(handle)
                handle.close()
                return self._parse_pubmed_records(records)
            return []

        except ImportError:
            logger.warning("biopython not installed. PubMed search unavailable.")
            return []
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return []

    def _parse_pubmed_records(self, records: dict) -> list[dict]:
        parsed = []
        for article in records.get("PubmedArticle", []):
            try:
                medline = article.get("MedlineCitation", {})
                art = medline.get("Article", {})
                parsed.append({
                    "pmid": str(medline.get("PMID", "")),
                    "title": str(art.get("ArticleTitle", "")),
                    "abstract": str(
                        art.get("Abstract", {}).get("AbstractText", [""])[0]
                    ),
                    "journal": str(
                        art.get("Journal", {}).get("Title", "")
                    ),
                    "year": str(
                        art.get("Journal", {})
                        .get("JournalIssue", {})
                        .get("PubDate", {})
                        .get("Year", "")
                    ),
                    "doi": "",
                    "source_db": "pubmed",
                })
            except Exception:
                continue
        return parsed


class ScopusClient(DatabaseConnector):
    """Scopus connector via Elsevier API."""

    name = "Scopus"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SCOPUS_API_KEY")

    def translate_query(self, concept_blocks: dict[str, list[str]]) -> str:
        parts = []
        for block_name, terms in concept_blocks.items():
            field_terms = [f'TITLE-ABS-KEY("{t}")' for t in terms]
            parts.append(f"({' OR '.join(field_terms)})")
        return " AND ".join(parts)

    def search(self, query: str, max_results: int = 1000) -> list[dict]:
        logger.info(f"Scopus search: {query[:80]}...")
        if not self.api_key:
            logger.warning("Scopus API key not set. Skipping.")
            return []
        try:
            import requests

            url = "https://api.elsevier.com/content/search/scopus"
            headers = {"X-ELS-APIKey": self.api_key, "Accept": "application/json"}
            params = {"query": query, "count": min(max_results, 25)}
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            entries = (
                data.get("search-results", {}).get("entry", [])
            )
            return [
                {
                    "title": e.get("dc:title", ""),
                    "doi": e.get("prism:doi", ""),
                    "year": e.get("prism:coverDate", "")[:4],
                    "journal": e.get("prism:publicationName", ""),
                    "source_db": "scopus",
                }
                for e in entries
            ]
        except Exception as e:
            logger.error(f"Scopus search failed: {e}")
            return []


class WoSClient(DatabaseConnector):
    """Web of Science connector."""

    name = "Web of Science"

    def translate_query(self, concept_blocks):
        parts = []
        for terms in concept_blocks.values():
            parts.append(
                "(" + " OR ".join(f'TS=("{t}")' for t in terms) + ")"
            )
        return " AND ".join(parts)

    def search(self, query, max_results=1000):
        logger.info(f"WoS search: {query[:80]}...")
        logger.warning("WoS API requires institutional access. Placeholder.")
        return []


class EmbaseClient(DatabaseConnector):
    """Embase connector."""

    name = "Embase"

    def translate_query(self, concept_blocks):
        parts = []
        for terms in concept_blocks.values():
            field_terms = [f"'{t}':ti,ab" for t in terms]
            parts.append(f"({' OR '.join(field_terms)})")
        return " AND ".join(parts)

    def search(self, query, max_results=1000):
        logger.info(f"Embase search: {query[:80]}...")
        logger.warning("Embase API requires institutional access. Placeholder.")
        return []


class CENTRALClient(DatabaseConnector):
    """Cochrane CENTRAL connector."""

    name = "Cochrane CENTRAL"

    def translate_query(self, concept_blocks):
        parts = []
        for terms in concept_blocks.values():
            field_terms = [
                f'"{t}" in Title Abstract Keyword' for t in terms
            ]
            parts.append(f"({' OR '.join(field_terms)})")
        return " AND ".join(parts)

    def search(self, query, max_results=1000):
        logger.info(f"CENTRAL search: {query[:80]}...")
        logger.warning("CENTRAL API access required. Placeholder.")
        return []


def get_all_connectors(config: Optional[dict] = None) -> dict[str, DatabaseConnector]:
    """Create all database connectors from config."""
    config = config or {}
    api_keys = config.get("api_keys", {})
    return {
        "pubmed": PubMedClient(api_key=api_keys.get("pubmed")),
        "scopus": ScopusClient(api_key=api_keys.get("scopus")),
        "wos": WoSClient(),
        "embase": EmbaseClient(),
        "central": CENTRALClient(),
    }
