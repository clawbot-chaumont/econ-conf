#!/usr/bin/env python3
"""Template for GFA 2026 - 32nd Annual Meeting of the German Finance Association (Sept 24-26, 2026)"""
import json, os
from datetime import datetime

data = {
    "conference": {
        "name": "Annual Meeting of the German Finance Association (DGF)",
        "short_name": "GFA 2026",
        "year": 2026,
        "edition": "32nd Annual Meeting",
        "start_date": "2026-09-24",
        "end_date": "2026-09-26",
        "location": "Düsseldorf, Germany",
        "venue": "Heinrich Heine University Düsseldorf and WHU – Otto Beisheim School of Management",
        "city": "Düsseldorf",
        "country": "Germany",
        "website": "https://www.whu.edu/de/news-insights/events/dgf2026/",
        "program_url": "",
        "organizer": "German Finance Association (DGF)",
        "description": "The conference brings together researchers and practitioners to discuss the latest theoretical and empirical research from all areas of finance, banking, and insurance.",
        "extras": {
            "doctoral_workshop": True,
            "women_in_finance": True,
            "registration_fees": {
                "standard_early": "€260",
                "standard_normal": "€280",
                "standard_late": "€320",
                "phd_student_early": "€190",
                "phd_student_normal": "€210",
                "phd_student_late": "€240"
            },
            "program_status": "Call for papers closed. Detailed program not yet published online."
        }
    },
    "scrape_metadata": {
        "scraped_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": "https://www.whu.edu/de/news-insights/events/dgf2026/",
        "program_url": "",
        "script_name": "scrape_gfa.py",
        "program_available": False,
        "program_type": "web",
        "notes": "General info available. Detailed program/schedule not yet published.",
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
print(f"✅ GFA data.json template written")
