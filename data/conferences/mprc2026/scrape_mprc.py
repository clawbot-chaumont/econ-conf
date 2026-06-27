#!/usr/bin/env python3
"""Template for MPRC 2026 - ECB Conference on Financial Stability and Macroprudential Policy (Dec 2-3, 2026)"""
import json, os
from datetime import datetime

data = {
    "conference": {
        "name": "ECB Conference on Financial Stability and Macroprudential Policy",
        "short_name": "MPRC 2026",
        "year": 2026,
        "edition": "1st (formerly ECB/IMF Macroprudential Policy and Research Conference series)",
        "start_date": "2026-12-02",
        "end_date": "2026-12-03",
        "location": "Frankfurt, Germany",
        "venue": "European Central Bank",
        "city": "Frankfurt",
        "country": "Germany",
        "website": "https://www.ecb.europa.eu/press/conferences/html/20261202_financial_stability.en.html",
        "program_url": "",
        "organizer": "European Central Bank (ECB)",
        "description": "Conference bringing together academics, central bankers, supervisors and market participants to present and discuss new research on financial stability and macroprudential policy. Focus topics: regulatory complexity, banking sector competitiveness, and AI in banking and financial sector.",
        "extras": {
            "keynote_speaker": "Anil Kashyap (Chicago Booth)",
            "panelists": ["Anat Admati (Stanford)", "Lorenzo Bini Smaghi (Société Générale)", "Claudio Borio (formerly BIS)", "Vicky Saporta (Bank of England)"],
            "panel_moderator": "Isabel Schnabel (ECB)",
            "submission_deadline": "2026-06-15",
            "program_status": "Call for papers open until June 15, 2026. Program not yet available."
        }
    },
    "scrape_metadata": {
        "scraped_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": "https://www.ecb.europa.eu/press/conferences/html/20261202_financial_stability.en.html",
        "program_url": "",
        "script_name": "scrape_mprc.py",
        "program_available": False,
        "program_type": "web",
        "notes": "Only call for papers available. Submission deadline June 15, 2026. Note: This is the renamed/restructured version of the former ECB/IMF Macroprudential Policy and Research Conference series.",
        "errors": ["Program not yet available - call for papers still open"]
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
print(f"✅ MPRC data.json template written")
