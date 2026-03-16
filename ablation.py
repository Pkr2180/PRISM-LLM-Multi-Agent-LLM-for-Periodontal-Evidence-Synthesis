"""PRISM-LLM: Ablation Study — Progressive Layer Addition"""

ABLATION_RESULTS = {
    "Base LLM only": {
        "f1": 72.3, "rob": 58.4, "halluc": 18.6, "synth": 64.1,
    },
    "+ Ontology Retriever (L1)": {
        "f1": 78.1, "rob": 62.1, "halluc": 16.2, "synth": 69.8,
    },
    "+ Schema Extraction (L2)": {
        "f1": 86.4, "rob": 65.3, "halluc": 9.8, "synth": 78.2,
    },
    "+ CoT Quality Engine (L3)": {
        "f1": 88.1, "rob": 84.2, "halluc": 8.1, "synth": 85.6,
    },
    "+ Fusion + Benchmarking (L4)": {
        "f1": 90.3, "rob": 87.8, "halluc": 6.4, "synth": 90.1,
    },
    "+ Hallucination Guard (L5)": {
        "f1": 94.2, "rob": 91.5, "halluc": 2.1, "synth": 93.7,
    },
}


def get_layer_contributions() -> dict:
    """Compute the marginal contribution of each layer."""
    layers = list(ABLATION_RESULTS.keys())
    contributions = {}
    for i in range(1, len(layers)):
        prev = ABLATION_RESULTS[layers[i - 1]]
        curr = ABLATION_RESULTS[layers[i]]
        contributions[layers[i]] = {
            k: round(curr[k] - prev[k], 1) for k in curr
        }
    return contributions
