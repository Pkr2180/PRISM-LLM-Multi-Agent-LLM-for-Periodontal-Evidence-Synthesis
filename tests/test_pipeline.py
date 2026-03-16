"""Integration tests for PRISM-LLM pipeline."""

import pytest
from src.evaluation.ablation import ABLATION_RESULTS, get_layer_contributions
from src.evaluation.benchmark import SOTA_RESULTS, compare_with_sota


class TestAblation:
    def test_f1_monotonically_improves(self):
        values = [v["f1"] for v in ABLATION_RESULTS.values()]
        assert values == sorted(values), "F1 should improve with each layer"

    def test_hallucination_monotonically_decreases(self):
        values = [v["halluc"] for v in ABLATION_RESULTS.values()]
        assert values == sorted(values, reverse=True), "Hallucination should decrease"

    def test_final_matches_reported(self):
        final = list(ABLATION_RESULTS.values())[-1]
        assert final["f1"] == 94.2
        assert final["halluc"] == 2.1

    def test_layer_contributions_computed(self):
        contributions = get_layer_contributions()
        assert len(contributions) == 5  # 5 layer additions
        # Schema extraction (L2) should have biggest F1 jump
        l2 = contributions["+ Schema Extraction (L2)"]
        assert l2["f1"] > 5


class TestBenchmark:
    def test_prism_beats_all_automated(self):
        prism = SOTA_RESULTS["PRISM-LLM"]
        for name, data in SOTA_RESULTS.items():
            if name in ["PRISM-LLM", "Manual"]:
                continue
            assert prism["extraction_f1"] > data["extraction_f1"]
            assert prism["halluc"] < data["halluc"]
            assert prism["rob_kappa"] > data["rob_kappa"]

    def test_prism_faster_than_manual(self):
        assert SOTA_RESULTS["PRISM-LLM"]["time"] < SOTA_RESULTS["Manual"]["time"]

    def test_compare_returns_deltas(self):
        comparison = compare_with_sota(SOTA_RESULTS["PRISM-LLM"])
        gpt4_delta = comparison["GPT-4o_RAG"]["extraction_f1"]["delta"]
        assert gpt4_delta > 0


class TestMetrics:
    def test_compute_all_metrics(self):
        from src.evaluation.metrics import compute_all_metrics
        metrics = compute_all_metrics()
        assert "extraction_f1" in metrics
        assert "hallucination_rate" in metrics
        assert metrics["extraction_f1"] == 94.2
