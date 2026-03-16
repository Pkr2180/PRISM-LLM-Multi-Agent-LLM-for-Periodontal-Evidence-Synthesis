"""PRISM-LLM Quick Demo: Process a sample paper."""

import json
from src.utils.numerical_grounding import verify_extraction
from src.utils.mesh_ontology import PerioMeSHOntology
from src.utils.deduplication import deduplicate_records
from src.evaluation.ablation import ABLATION_RESULTS
from src.evaluation.benchmark import SOTA_RESULTS

def main():
    print("=" * 60)
    print("  PRISM-LLM Demo")
    print("=" * 60)

    # Demo: MeSH expansion
    terms = ["periodontitis", "intrabony_defect", "stem_cell"]
    expanded = PerioMeSHOntology.expand_query(terms)
    print(f"\nMeSH Expansion: {len(terms)} -> {len(expanded)} terms")
    print(f"  Expanded: {expanded[:8]}...")

    # Demo: Numerical grounding
    good = {"cal_gain_mm": 3.5, "pd_reduction_mm": 4.0, "bone_fill_pct": 65.0}
    bad = {"cal_gain_mm": 12.0, "bone_fill_pct": 110.0}
    ok, flags = verify_extraction(good)
    print(f"\nGrounding (valid):   PASS={ok}, flags={flags}")
    ok, flags = verify_extraction(bad)
    print(f"Grounding (invalid): PASS={ok}, flags={flags}")

    # Demo: Deduplication
    records = [
        {"doi": "10.1234/a", "title": "Periodontal regeneration study"},
        {"doi": "10.1234/a", "title": "Periodontal regeneration study"},
        {"doi": "10.5678/b", "title": "A different study on bone grafts"},
    ]
    unique = deduplicate_records(records)
    print(f"\nDeduplication: {len(records)} -> {len(unique)} unique")

    # Demo: SOTA comparison
    print("\nSOTA Benchmark:")
    for sys_name, metrics in SOTA_RESULTS.items():
        print(f"  {sys_name:15s} | F1={metrics['extraction_f1']:.1f}% | "
              f"Halluc={metrics['halluc']:.1f}% | Time={metrics['time']}h")

    # Demo: Ablation
    print("\nAblation Study:")
    for layer, metrics in ABLATION_RESULTS.items():
        print(f"  {layer:40s} | F1={metrics['f1']:.1f}% | Halluc={metrics['halluc']:.1f}%")

    print("\n" + "=" * 60)
    print("  Demo complete. Run full pipeline with:")
    print("  prism-llm process --input paper.pdf")
    print("=" * 60)

if __name__ == "__main__":
    main()
