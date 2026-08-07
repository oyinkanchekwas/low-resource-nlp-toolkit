.PHONY: test quality check benchmark docs build

test:
	PYTHONPATH=src python3 -m unittest discover -s tests

quality:
	python3 scripts/quality_gate.py

check: quality test

benchmark:
	PYTHONPATH=src python3 benchmarks/afrisenti/run_benchmark.py --download

docs:
	mkdocs build --strict

build:
	python3 -m build
