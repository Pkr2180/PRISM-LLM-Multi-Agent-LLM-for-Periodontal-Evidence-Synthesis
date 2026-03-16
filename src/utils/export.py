"""
PRISM-LLM: Export Utilities
Generate output files: JSON, CSV, PRISMA flow diagrams, reports.
"""

import json
import csv
import os
from typing import Optional
from loguru import logger


def export_json(data: dict, path: str) -> None:
    """Export data as formatted JSON."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)
    logger.info(f"Exported JSON: {path}")


def export_csv(data: list[dict], path: str, fieldnames: Optional[list[str]] = None) -> None:
    """Export list of dicts as CSV."""
    if not data:
        logger.warning("No data to export as CSV")
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fieldnames = fieldnames or list(data[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)
    logger.info(f"Exported CSV: {path} ({len(data)} rows)")


def export_prisma_flow(
    identified: int,
    after_dedup: int,
    screened_out: int,
    full_text_assessed: int,
    excluded_full_text: int,
    included: int,
    path: str,
) -> None:
    """Generate a PRISMA 2020 flow diagram as SVG."""
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 500" width="600" height="500">
<style>text{{font-family:Arial,sans-serif;font-size:12px}}</style>
<rect width="600" height="500" fill="#fff"/>
<text x="300" y="25" text-anchor="middle" font-weight="bold" font-size="14">PRISMA 2020 Flow Diagram</text>

<rect x="180" y="40" width="240" height="35" rx="6" fill="#1565c0"/>
<text x="300" y="62" text-anchor="middle" fill="#fff">Records identified (n={identified})</text>

<line x1="300" y1="75" x2="300" y2="100" stroke="#333" stroke-width="1.5" marker-end="url(#a)"/>
<defs><marker id="a" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#333"/></marker></defs>

<rect x="180" y="100" width="240" height="35" rx="6" fill="#1565c0"/>
<text x="300" y="122" text-anchor="middle" fill="#fff">After deduplication (n={after_dedup})</text>

<line x1="300" y1="135" x2="300" y2="165" stroke="#333" stroke-width="1.5" marker-end="url(#a)"/>

<rect x="180" y="165" width="240" height="35" rx="6" fill="#5e35b1"/>
<text x="300" y="187" text-anchor="middle" fill="#fff">Title/abstract screened (n={after_dedup})</text>
<rect x="450" y="165" width="130" height="35" rx="6" fill="#e8eaf6" stroke="#5e35b1"/>
<text x="515" y="187" text-anchor="middle" fill="#311b92">Excluded (n={screened_out})</text>
<line x1="420" y1="182" x2="450" y2="182" stroke="#333" stroke-width="1.5" marker-end="url(#a)"/>

<line x1="300" y1="200" x2="300" y2="235" stroke="#333" stroke-width="1.5" marker-end="url(#a)"/>

<rect x="180" y="235" width="240" height="35" rx="6" fill="#e65100"/>
<text x="300" y="257" text-anchor="middle" fill="#fff">Full-text assessed (n={full_text_assessed})</text>
<rect x="450" y="235" width="130" height="35" rx="6" fill="#fff3e0" stroke="#e65100"/>
<text x="515" y="257" text-anchor="middle" fill="#bf360c">Excluded (n={excluded_full_text})</text>
<line x1="420" y1="252" x2="450" y2="252" stroke="#333" stroke-width="1.5" marker-end="url(#a)"/>

<line x1="300" y1="270" x2="300" y2="310" stroke="#333" stroke-width="1.5" marker-end="url(#a)"/>

<rect x="150" y="310" width="300" height="45" rx="6" fill="#c62828"/>
<text x="300" y="335" text-anchor="middle" fill="#fff" font-weight="bold" font-size="14">Included in review (n={included})</text>
</svg>"""

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(svg)
    logger.info(f"Exported PRISMA flow: {path}")
