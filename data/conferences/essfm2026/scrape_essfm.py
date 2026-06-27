#!/usr/bin/env python3
"""Template for ESSFM 2026 - European Summer Symposium in Financial Markets (July 12-24, 2026)"""
import json, os
from datetime import datetime

data = {
    "conference": {
        "name": "European Summer Symposium in Financial Markets",
        "short_name": "ESSFM 2026",
        "year": 2026,
        "edition": "2026",
        "start_date": "2026-07-12",
        "end_date": "2026-07-24",
        "location": "Switzerland",
        "venue": "Study Center Gerzensee",
        "city": "Gerzensee",
        "country": "Switzerland",
        "website": "https://cepr.org/essfm-2026",
        "program_url": "",
        "organizer": "Centre for Economic Policy Research (CEPR)",
        "description": "The European Summer Symposium in Financial Markets (ESSFM) brings together academics, policymakers and practitioners to present and discuss frontier research in financial markets.",
        "extras": {
            "program_status": "CEPR website behind Cloudflare protection. Program could not be scraped directly."
        }
    },
    "scrape_metadata": {
        "scraped_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": "https://cepr.org/essfm-2026",
        "program_url": "",
        "script_name": "scrape_essfm.py",
        "program_available": False,
        "program_type": "web",
        "notes": "CEPR website protected by Cloudflare. Could not access program content directly.",
        "errors": ["Cloudflare protection blocked scraping. Page returns 403/security verification."]
    },
    "sessions": [],
    "participants": [],
    "total_sessions": 0,
    "total_papers": 0,
    "total_participants": 0
}

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"✅ ESSFM data.json template written")
