PYTHON ?= python3

.PHONY: install install-dev run test lint typecheck format hooks

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

run:
	PYTHONPATH=src uvicorn election_system.main:app --reload --host 0.0.0.0 --port 8000

test:
	PYTHONPATH=src pytest -q

lint:
	PYTHONPATH=src ruff check src tests

typecheck:
	PYTHONPATH=src mypy src

format:
	PYTHONPATH=src ruff check src tests --fix

hooks:
	git config core.hooksPath .githooks
	chmod +x .githooks/pre-push
	@echo "Git hooks enabled from .githooks/"
