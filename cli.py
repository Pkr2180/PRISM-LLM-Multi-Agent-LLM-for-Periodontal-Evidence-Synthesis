"""
PRISM-LLM: Command Line Interface
"""

import argparse
import json
import sys
import os
from loguru import logger


def cmd_process(args):
    """Process a single paper through PRISM-LLM."""
    from src.pipeline import PRISMPipeline

    config = _load_config(args.config) if args.config else {}
    pipeline = PRISMPipeline(config=config)

    logger.info(f"Processing: {args.input}")
    results = pipeline.process_paper(args.input)

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"Results saved to {args.output}")


def cmd_review(args):
    """Run a full systematic review pipeline."""
    from src.pipeline import PRISMPipeline

    config = _load_config(args.config)
    pipeline = PRISMPipeline(config=config)

    os.makedirs(args.output, exist_ok=True)
    results = pipeline.run(output_dir=args.output)
    logger.info(f"Review complete. Results in {args.output}/")


def cmd_evaluate(args):
    """Evaluate PRISM-LLM against gold standard."""
    from src.evaluation.metrics import compute_all_metrics

    metrics = compute_all_metrics(args.gold)
    with open(args.output, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Evaluation results: {json.dumps(metrics, indent=2)}")


def cmd_benchmark(args):
    """Compare with SOTA systems."""
    from src.evaluation.benchmark import SOTA_RESULTS

    print(json.dumps(SOTA_RESULTS, indent=2))


def _load_config(path: str) -> dict:
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(
        prog="prism-llm",
        description="PRISM-LLM: Periodontal Regeneration Evidence Synthesis",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # process
    p1 = sub.add_parser("process", help="Process a single paper")
    p1.add_argument("--input", "-i", required=True, help="PDF or text file path")
    p1.add_argument("--output", "-o", default="results.json", help="Output JSON path")
    p1.add_argument("--config", "-c", default=None, help="Config YAML path")

    # review
    p2 = sub.add_parser("review", help="Run full systematic review")
    p2.add_argument("--config", "-c", required=True, help="Config YAML path")
    p2.add_argument("--output", "-o", default="outputs/", help="Output directory")

    # evaluate
    p3 = sub.add_parser("evaluate", help="Evaluate against gold standard")
    p3.add_argument("--gold", "-g", required=True, help="Gold standard directory")
    p3.add_argument("--output", "-o", default="eval_results.json")

    # benchmark
    p4 = sub.add_parser("benchmark", help="Show SOTA comparison")

    args = parser.parse_args()

    if args.command == "process":
        cmd_process(args)
    elif args.command == "review":
        cmd_review(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
