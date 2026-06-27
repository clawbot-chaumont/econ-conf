#!/usr/bin/env python3
"""Template for SEA 2026 - 96th Annual Meeting of the Southern Economic Association (Nov 21-23, 2026)"""
import json, os
from datetime import datetime

data = {
    "conference": {
        "name": "Southern Economic Association Annual Meeting",
        "short_name": "SEA 2026",
        "year": 2026,
        "edition": "96th Annual Meeting",
        "start_date": "2026-11-21",
        "end_date": "2026-11-23",
        "location": "Houston, USA",
        "venue": "Marriott Marquis Houston",
        "city": "Houston",
        "country": "USA",
        "website": "https://www.southerneconomic.org/",
        "program_url": "",
        "organizer": "Southern Economic Association",
        "description": "The 96th Annual Meeting of the Southern Economic Association.",
        "extras": {
            "program_status": "General info available (dates, location). Detailed program not yet published (conference in November 2026)."
        }
    },
    "scrape_metadata": {
        "scraped_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": "https://www.southerneconomic.org/",
        "program_url": "",
        "script_name": "scrape_sea.py",
        "program_available": False,
        "program_type": "web",
        "notes": "Website shows dates and location for 96th Annual Meeting (Nov 21-23, 2026, Houston). Program not yet available.",
        "errors": ["Detailed program not yet available"]
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
print(f"✅ SEA data.json template written")
