#!/usr/bin/env python3
"""Template for AC-MFR 2026 - 3rd Annual Conference on Macro-Finance Research (Oct 9, 2026)"""
import json, os
from datetime import datetime

data = {
    "conference": {
        "name": "Annual Conference on Macro-Finance Research",
        "short_name": "AC-MFR 2026",
        "year": 2026,
        "edition": "3rd",
        "start_date": "2026-10-09",
        "end_date": "2026-10-09",
        "location": "San Francisco, USA",
        "venue": "Federal Reserve Bank of San Francisco",
        "city": "San Francisco",
        "country": "USA",
        "website": "https://www.frbsf.org/news-and-media/events/conferences/2026/10/conference-on-macro-finance-research-2026/",
        "program_url": "",
        "organizer": "Federal Reserve Bank of San Francisco, Center for Monetary Research",
        "description": "Conference discussing the latest macro-finance research, broadly defined as work on the links between financial markets, monetary policy, and the macroeconomy.",
        "extras": {
            "academic_keynote": "Jeremy Stein (Harvard University)",
            "janet_yellen_award": True,
            "organizers": ["Michael Bauer", "Thomas Mertens", "Pascal Paul"],
            "submission_deadline": "2026-06-15",
            "program_status": "Call for papers open until June 15, 2026. Program not yet available."
        }
    },
    "scrape_metadata": {
        "scraped_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": "https://www.frbsf.org/news-and-media/events/conferences/2026/10/conference-on-macro-finance-research-2026/",
        "program_url": "",
        "script_name": "scrape_acmfr.py",
        "program_available": False,
        "program_type": "web",
        "notes": "Only call for papers available. Submission deadline June 15, 2026. Program will be available after that date.",
        "errors": ["Program not yet published - submission deadline is June 15, 2026"]
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
print(f"✅ AC-MFR data.json template written")
