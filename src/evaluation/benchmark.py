"""PRISM-LLM: SOTA Benchmark Comparison Data"""

SOTA_RESULTS = {
    "PRISM-LLM": {
        "extraction_f1": 94.2, "screening_f1": 96.8, "rob_kappa": 0.915,
        "numerical_accuracy": 97.6, "halluc": 2.1, "synthesis": 93.7, "time": 4.2,
    },
    "GPT-4o_RAG": {
        "extraction_f1": 78.4, "screening_f1": 85.2, "rob_kappa": 0.683,
        "numerical_accuracy": 84.3, "halluc": 14.7, "synthesis": 72.1, "time": 6.8,
    },
    "Med-PaLM_2": {
        "extraction_f1": 82.1, "screening_f1": 88.7, "rob_kappa": 0.736,
        "numerical_accuracy": 87.2, "halluc": 11.2, "synthesis": 78.4, "time": 7.5,
    },
    "BioGPT": {
        "extraction_f1": 80.6, "screening_f1": 86.4, "rob_kappa": 0.712,
        "numerical_accuracy": 83.9, "halluc": 12.8, "synthesis": 74.9, "time": 5.1,
    },
    "Manual": {
        "extraction_f1": 91.0, "screening_f1": 92.1, "rob_kappa": 0.880,
        "numerical_accuracy": 95.0, "halluc": 1.5, "synthesis": 89.2, "time": 480,
    },
}


def compare_with_sota(system_results: dict) -> dict:
    """Compare a system's results against all SOTA baselines."""
    comparison = {}
    for sys_name, baseline in SOTA_RESULTS.items():
        comparison[sys_name] = {}
        for metric, base_val in baseline.items():
            sys_val = system_results.get(metric, 0)
            comparison[sys_name][metric] = {
                "baseline": base_val,
                "system": sys_val,
                "delta": round(sys_val - base_val, 2),
            }
    return comparison
