"""
Fine-tune DeBERTa-v3-large on SciFact + dental claim-source pairs.

Usage:
    python scripts/finetune_nli_guard.py \
        --scifact_data data/training/scifact.json \
        --dental_data data/training/dental_claims.json \
        --output_dir models/nli_guard/

Requirements:
    - SciFact dataset (Wadden et al., 2020)
    - Curated dental claim-source verification pairs (~2K)
"""

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scifact_data", required=True)
    parser.add_argument("--dental_data", default=None)
    parser.add_argument("--output_dir", default="models/nli_guard/")
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    print(f"Fine-tuning NLI hallucination guard")

if __name__ == "__main__":
    main()
