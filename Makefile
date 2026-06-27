.PHONY: build build-csv normalize clean install

# Default: build the JSON dataset from ALL_CONFERENCES_2026.csv
build:
	python -m econ_conf.build.json_builder

# Build clean CSV (institution normalization only)
build-csv:
	python ~/economics-conferences/normalize_institutions.py

# Install package in development mode
install:
	pip install -e .
	pip install rapidfuzz

# Clean generated files
clean:
	rm -f data/outputs/ALL_CONFERENCES_2026.json
	rm -f data/outputs/ALL_CONFERENCES_2026_CLEAN.csv
	rm -rf econ_conf.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
