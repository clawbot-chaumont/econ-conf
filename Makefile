.PHONY: all build normalize upload status scrape process full clean install

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
upload:
	python run.py --upload

# Show conference coverage status
status:
	python run.py --status

# Scrape one conference:  make scrape KEY=AEA
scrape:
	python run.py --scrape $(KEY)

# Scrape all conferences
scrape-all:
	python run.py --scrape-all

# Process one conference (sheet + Drive):  make process KEY=AEA
process:
	python run.py --process $(KEY)

# Process all conferences
process-all:
	python run.py --process-all

# Full pipeline for one conference:  make full KEY=AEA
full:
	python run.py --full $(KEY)

# Push to Supabase
push:
	python run.py --push

# Full pipeline + Supabase
full-sync: full-all push

# Install package in development mode
install:
	pip install -e .
	pip install rapidfuzz

# Clean generated files
clean:
	rm -f data/outputs/ALL_CONFERENCES_2026.json
	rm -rf econ_conf.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
