#!/usr/bin/env python3
"""Template for PDFM 2026 - Paris December Finance Meeting (Dec 17, 2026)"""
import json, os
from datetime import datetime

data = {
    "conference": {
        "name": "EUROFIDAI-ESSEC Paris December Finance Meeting",
        "short_name": "PDFM 2026",
        "year": 2026,
        "edition": "24th",
        "start_date": "2026-12-17",
        "end_date": "2026-12-17",
        "location": "Paris, France",
        "venue": "Pullman Paris Montparnasse Hotel",
        "city": "Paris",
        "country": "France",
        "website": "https://www.paris-december.eu/",
        "program_url": "",
        "organizer": "EUROFIDAI (European Financial Data Institute) and ESSEC Business School",
        "description": "All researchers are invited to present in English their latest research in all areas of finance. Job market papers are welcomed and integrated in normal sessions.",
        "extras": {
            "sponsors": ["Amundi", "PLADIFES", "CERESSEC", "CDC Institute for Economic Research", "Clipway"],
            "program_status": "Call for papers open. Program not yet available (conference in December 2026)."
        }
    },
    "scrape_metadata": {
        "scraped_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": "https://www.paris-december.eu/",
        "program_url": "",
        "script_name": "scrape_pdfm.py",
        "program_available": False,
        "program_type": "web",
        "notes": "Only call for papers and general info available. Program will be published closer to December 2026.",
        "errors": ["Program not yet available"]
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
print(f"✅ PDFM data.json template written")
