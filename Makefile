.PHONY: all build normalize upload status scrape conference clean install

# Default: build JSON from latest data
all: build

# Build JSON dataset
build:
	python run.py

# Run institution normalization
normalize:
	python run.py --normalize
	python run.py

# Build + upload to Google Drive
upload: build
	python run.py --upload

# Show conference coverage status
status:
	python run.py --status

# Full pipeline: scrape → normalize → build → upload
full:
	python run.py --from-scrape --normalize --upload

# Run pipeline for one conference: make conference KEY=AEA
conference:
	python run.py --conference $(KEY)

# Install package in development mode
install:
	pip install -e .
	pip install rapidfuzz

# Clean generated files
clean:
	rm -f data/outputs/ALL_CONFERENCES_2026.json
	rm -rf econ_conf.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
