# Economics Conference Data Pipeline

Scrape, normalize, and build a structured dataset of 44+ economics and finance conferences worldwide.

## Dataset: `ALL_CONFERENCES_2026.json`

```json
{
  "ECB": {
    "conference_name": "European Central Bank Annual Research Conference",
    "year": 2026,
    "participants": [
      {
        "name": "Christine Lagarde",
        "institutions": ["European Central Bank"],
        "papers": ["Monetary Policy in a Changing World"],
        "sessions": ["Keynote Address"]
      }
    ]
  }
}
```

- **34 conferences** with participant data (44 tracked, 10 pending scrape)
- **~11,800 participant entries** grouped by conference
- **Multi-affiliation support**: `["Harvard University", "NBER"]`
- **Homonym-safe**: each `(name, conference)` is a separate entry
- **~2,600 normalized institution names**

## Project Structure

```
econ-conf/
├── econ_conf/             # Python package
│   ├── normalize/         # Institution name normalization
│   │   ├── institutions.py    # normalize_institution(), split_affiliations()
│   │   ├── canonical_map.py   # 150+ manual institution mappings
│   │   └── abbreviations.py   # ECB → European Central Bank, etc.
│   ├── build/             # Dataset builders
│   │   └── json_builder.py    # Build ALL_CONFERENCES_2026.json
│   ├── pipeline/          # Scraping orchestration
│   │   ├── master.py          # Master pipeline (single or --all)
│   │   └── newsletter.py      # ECB Central Bank Research Pulse
│   ├── scrapers/          # Platform-specific scrapers
│   │   ├── conftool.py, sciencesconf.py, drupal.py, ...
│   ├── utils/             # Google Drive/Sheets API, schema validation
│   └── config.py          # Conference registry (44 conferences)
├── data/
│   ├── conferences/       # Per-conference folders (data.json + scraper)
│   └── outputs/           # Built JSON files
├── scripts/               # Convenience scripts
├── Makefile
└── pyproject.toml
```

## Quick Start

```bash
# Install
pip install -e .

# Build the full JSON from the CSV
make build

# Or directly
python -m econ_conf.build.json_builder

# Normalize a single institution name
python -c "
from econ_conf.normalize.institutions import normalize_institution
print(normalize_institution('Federal Reserve Board, USA'))
# → Federal Reserve Bank
"
```

## Adding a New Conference

1. Add entry to `econ_conf/config.py` (`CONFERENCES_2026` dict)
2. Create `data/conferences/<folder>/` with scraper script + data.json
3. Run `python -m econ_conf.pipeline.master <SHORT_KEY>`
4. Rebuild: `make build`

## Normalization Pipeline

Institution names go through:
1. **Diacritic stripping**: é → e, ü → u
2. **Abbreviation expansion**: ECB → European Central Bank, MIT → MIT
3. **Pattern cleaning**: trailing punctuation, double spaces, country suffixes
4. **Canonical mapping**: 150+ hand-curated rules (Fed Board → Federal Reserve Bank; Università Bocconi → Bocconi University)
5. **Affiliation splitting**: "Harvard University and NBER" → ["Harvard University", "NBER"]; "MIT; NBER" → ["MIT", "NBER"]

## Coverage

| Status | Count |
|--------|-------|
| Complete (participants + sessions) | 30 |
| Participants only | 2 |
| Sessions only | 2 |
| Not yet scraped | 10 |
| **Total tracked** | **44** |

## Related

- [econ-conf-search](https://github.com/clawbot-chaumont/econ-conf-search) — React frontend for browsing the data
