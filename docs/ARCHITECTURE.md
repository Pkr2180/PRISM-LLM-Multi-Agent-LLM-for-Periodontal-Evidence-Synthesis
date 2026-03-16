# PRISM-LLM Architecture

## Overview
PRISM-LLM is a 5-layer hierarchical multi-agent architecture designed for automated systematic benchmarking of periodontal regeneration evidence.

## Layer 1: Ontology-Aware Retrieval Engine
- **Base encoder:** PubMedBERT with MeSH periodontal graph adapter injection
- **Retrieval:** Hybrid BM25 + dense retrieval fusion (alpha=0.6)
- **Databases:** PubMed, Scopus, WoS, Embase, CENTRAL
- **Deduplication:** DOI exact match + fuzzy title (Levenshtein >= 0.92)
- **Query enrichment:** MeSH concept graph + ICD-DA code mapping

## Layer 2: Structured Clinical Extraction
- **Schema:** PICO-Perio JSON-mode (Pydantic-enforced)
- **Numerical Grounding:** Cross-validates extracted values against table OCR + in-text
- **Defect Taxonomy:** Multi-label classifier (4,200 training samples)
- **Re-extraction:** Automatic retry on plausibility failures

## Layer 3: Evidence Quality Reasoning
- **RCTs:** RoB 2 chain-of-thought (5 domains)
- **Non-RCTs:** ROBINS-I (7 domains)
- **GRADE:** 5-domain certainty estimation
- **Reporting:** CONSORT-Outcomes completeness scan

## Layer 4: Cross-Evidence Fusion & Benchmarking
- **Aggregation:** Quality-weighted: w = f(n, 1/RoB, follow_up, defect_std)
- **Benchmarking:** Intervention x Defect x Outcome matrix
- **Gap detection:** Automated with clinical importance x evidence scarcity scoring

## Layer 5: Agentic Orchestrator + Self-Verification
- **Controller:** LangGraph PRISMA-Agent finite-state machine
- **Guard 1:** NLI claim grounding (DeBERTa-v3-large + SciFact)
- **Guard 2:** Statistical plausibility (CAL<8mm, bone fill<100%, etc.)
- **Conflict resolution:** Structured deliberation for extraction disagreements
