.PHONY: install test lint clean run evaluate

install:
	pip install -e ".[dev]"
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	ruff check src/ tests/
	black --check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

clean:
	rm -rf __pycache__ .pytest_cache htmlcov .coverage *.egg-info dist build
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

run:
	python -m src.cli process --input $(INPUT) --output results.json

evaluate:
	python -m src.cli evaluate --gold data/gold_standard/ --output eval_results.json

demo:
	python -m src.demo
