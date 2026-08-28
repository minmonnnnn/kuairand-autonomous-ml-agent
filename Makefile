.PHONY: help setup lint test test-all baseline sanity check-submission clean

DATA_DIR ?= ./KuaiRand-Pure/data

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

setup:  ## Install dependencies
	pip install -r requirements.txt

lint:  ## Lint everything except the organizer reference code
	ruff check src tests scripts

test:  ## Run tests that do not need the dataset
	pytest -q -m "not requires_data"

test-all:  ## Run every test (needs the dataset on disk)
	pytest -q

sanity:  ## Harness self-check: must print primary ~0.475
	cd starter_kit && python3 baseline.py --model random --data_dir ../$(DATA_DIR)

baseline:  ## Reproduce the official FM baseline (~40s)
	bash scripts/baseline/run_official_baseline.sh

check-submission:  ## Validate a submission file: make check-submission FILE=x.csv SPLIT=valid
	cd starter_kit && python3 submit.py --check --split $(or $(SPLIT),valid) --data_dir ../$(DATA_DIR) ../$(FILE)

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} + ; rm -rf .pytest_cache .ruff_cache
