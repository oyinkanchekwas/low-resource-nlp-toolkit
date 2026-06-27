.PHONY: test quality check build

test:
	PYTHONPATH=src python3 -m unittest discover -s tests

quality:
	python3 scripts/quality_gate.py

check: quality test

build:
	python3 -m build
