# PRISM-LLM Evaluation Protocol

## Gold Standard Dataset
- 200 periodontal regeneration papers
- Annotated by 3 periodontists + 2 evidence synthesis methodologists
- Inter-annotator agreement: kappa >= 0.85

## Metrics
| Metric | Description | PRISM-LLM |
|--------|-------------|-----------|
| Extraction F1 | Micro-averaged across PICO fields | 94.2% |
| Screening F1 | Include/exclude classification | 96.8% |
| RoB Kappa | Cohen's kappa vs expert consensus | 0.915 |
| Numerical Accuracy | Exact match for clinical values | 97.6% |
| Hallucination Rate | NLI-verified ungrounded claims | 2.1% |
| Synthesis Quality | 5-component composite score | 93.7% |
| Processing Time | Wall-clock per 100 papers | 4.2 hrs |

## Statistical Tests
- McNemar's test for classification metrics
- Paired t-test for continuous metrics
- Bootstrap 95% CI for composite scores
- Significance: p < 0.01
- Effect sizes: Cohen's d 0.8-2.4 (large)

## Running Evaluation
```bash
python -m src.cli evaluate --gold data/gold_standard/ --output eval_results.json
```
