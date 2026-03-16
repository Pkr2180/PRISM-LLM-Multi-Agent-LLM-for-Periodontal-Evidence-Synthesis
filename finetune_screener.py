"""
Fine-tune PubMedBERT screening classifier on dental SR decisions.

Usage:
    python scripts/finetune_screener.py \
        --train_data data/training/screening_decisions.json \
        --output_dir models/screener/

Requirements:
    - 10K labeled screening decisions from dental systematic reviews
    - Three-class labels: INCLUDE / EXCLUDE / UNCERTAIN
"""

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_data", required=True)
    parser.add_argument("--output_dir", default="models/screener/")
    parser.add_argument("--epochs", type=int, default=20)
    args = parser.parse_args()
    print(f"Fine-tuning screening classifier: {args.train_data}")

if __name__ == "__main__":
    main()
