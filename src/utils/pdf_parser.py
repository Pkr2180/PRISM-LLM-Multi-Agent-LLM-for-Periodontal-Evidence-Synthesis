"""
PRISM-LLM: PDF Text Extraction
Layout-aware parsing of academic papers with section detection.
"""

import re
from typing import Optional
from loguru import logger


def extract_text_from_pdf(pdf_path: str) -> dict[str, str]:
    """
    Extract structured text from a PDF academic paper.

    Args:
        pdf_path: Path to PDF file.

    Returns:
        Dictionary with keys: full_text, title, abstract, methods_text, results_text.
    """
    sections = {
        "full_text": "",
        "title": "",
        "abstract": "",
        "methods_text": "",
        "results_text": "",
    }

    try:
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        pages = [page.get_text("text") for page in doc]
        full_text = "\n".join(pages)
        doc.close()
        sections["full_text"] = full_text

        # Extract title (first significant text block)
        for line in full_text.split("\n"):
            line = line.strip()
            if len(line) > 20 and not line.startswith("http"):
                sections["title"] = line
                break

        # Extract abstract
        abstract_match = re.search(
            r"(?i)(abstract|summary)[:\s]*(.+?)(?=\n\s*(?:introduction|keywords|1\.))",
            full_text,
            re.DOTALL,
        )
        if abstract_match:
            sections["abstract"] = abstract_match.group(2).strip()[:3000]

        # Extract methods
        methods_match = re.search(
            r"(?i)(?:materials?\s+and\s+methods?|methods?)[:\s]*(.+?)(?=\n\s*(?:results?|3\.))",
            full_text,
            re.DOTALL,
        )
        if methods_match:
            sections["methods_text"] = methods_match.group(1).strip()[:5000]

        # Extract results
        results_match = re.search(
            r"(?i)results?[:\s]*(.+?)(?=\n\s*(?:discussion|4\.))",
            full_text,
            re.DOTALL,
        )
        if results_match:
            sections["results_text"] = results_match.group(1).strip()[:5000]

        logger.info(f"Extracted {len(full_text)} chars from {pdf_path}")

    except ImportError:
        logger.warning("PyMuPDF not installed. Using fallback text extraction.")
        try:
            with open(pdf_path, "r", encoding="utf-8", errors="ignore") as f:
                sections["full_text"] = f.read()
        except Exception as e:
            logger.error(f"Failed to read {pdf_path}: {e}")

    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")

    return sections
