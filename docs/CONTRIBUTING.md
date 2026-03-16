# Contributing to PRISM-LLM

## Setup
```bash
git clone https://github.com/[username]/prism-llm.git
cd prism-llm
pip install -e .
pip install -r requirements.txt
```

## Running Tests
```bash
make test
# or
pytest tests/ -v --cov=src
```

## Code Style
- Python 3.9+ with type hints
- Black formatting (line length 100)
- Ruff linting
- Docstrings for all public functions

## Pull Request Process
1. Fork and create a feature branch
2. Add tests for new functionality
3. Ensure all tests pass
4. Update docs if needed
5. Submit PR with description
