#!/usr/bin/env python3
"""
Convert existing conference data to v2 schema for AFA, CEPRPS, ECBARC, CMRC, MYE.
"""
import json, os, re
from datetime import datetime

DATA_DIR = "/root/economics-conferences"

def load_old(folder, file="data.json"):
    path = os.path.join(DATA_DIR, folder, file)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def save_v2(folder, data):
    path = os.path.join(DATA_DIR, folder, "data.json")
    os.makedirs(os.path.join(DATA_DIR, folder), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Written: {path}")

# ── 1. AFA 2026 ───────────────────────────────────────────────
def afa_v2():
    old = load_old("afa2026")
    # Already has full program data but in old format (conference is string)
    sessions = []
    participants = []
    seen_participants = set()
    
    # Extract sessions from special_events and the rest
    special_events = old.get("special_events", [])
    
    # Parse the main program data - look for paper sessions and poster sessions
    for se in special_events:
        session = {
            "session_title": se.get("name", ""),
            "session_type": se.get("type", "special_event"),
            "day": se.get("day", ""),
            "date": se.get("date", ""),
            "time": se.get("time", ""),
            "room": se.get("location", ""),
            "chair": se.get("chair", se.get("chairs", "")),
        }
        # Trim empty fields
        session = {k: v for k, v in session.items() if v}
        
        papers = []
        # Panelists become a special paper
        panelists = se.get("panelists", [])
        if panelists:
            papers.append({
                "title": f"Panel: {se.get('name', '')}",
                "authors": [p.split("(")[0].strip() for p in panelists],
                "presenter": panelists[0].split("(")[0].strip() if panelists else "",
            })
        
        # Description might contain paper info
        desc = se.get("description", "")
        if desc:
            # Check for panel topics
            lines = desc.split("\n")
            for line in lines:
                if line.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
                    parts = line.split(",", 1)
                    if len(parts) > 1 and "(" in parts[1]:
                        papers.append({
                            "title": parts[0].strip(),
                            "authors": [parts[1].strip()],
                            "presenter": parts[1].strip(),
                        })
        
        if papers:
            session["papers"] = papers
        sessions.append(session)
    
    # Look for paper_sessions, sessions etc.
    for key in ["paper_sessions", "sessions", "poster_session"]:
        items = old.get(key, [])
        if isinstance(items, list):
            for item in items:
                s = {
                    "session_title": item.get("title", item.get("name", item.get("session", ""))),
                    "session_type": item.get("type", key.replace("_", " ").title()),
                    "day": item.get("day", ""),
                    "date": item.get("date", ""),
                    "time": item.get("time", item.get("timeslot", "")),
                    "room": item.get("room", item.get("location", "")),
                    "chair": item.get("chair", item.get("chairperson", "")),
                }
                s = {k: v for k, v in s.items() if v}
                
                raw_papers = item.get("papers", [])
                papers = []
                for p in raw_papers:
                    if isinstance(p, str):
                        papers.append({"title": p, "authors": [], "presenter": ""})
                    elif isinstance(p, dict):
                        authors = p.get("authors", p.get("author", ""))
                        if isinstance(authors, str):
                            authors = [a.strip() for a in authors.split(";") if a.strip()]
                            if not authors:
                                authors = [p.get("author", "")]
                        papers.append({
                            "title": p.get("title", ""),
                            "authors": authors if isinstance(authors, list) else [authors],
                            "presenter": p.get("presenter", p.get("presenter_clean", "")),
                            "discussant": p.get("discussant", ""),
                            "abstract": p.get("abstract", ""),
                        })
                if papers:
                    s["papers"] = papers
                sessions.append(s)
    
    # Build conference dict
    conf = {
        "name": "American Finance Association Annual Meeting",
        "short_name": "AFA 2026",
        "year": 2026,
        "edition": "2026 Annual Meeting",
        "start_date": "2026-01-03",
        "end_date": "2026-01-05",
        "location": "Philadelphia, PA, USA",
        "venue": "Loews Philadelphia Hotel & Philadelphia Marriott Downtown",
        "website": "https://www.afajof.org/annual-meeting/",
        "program_url": "https://afajof.org/management/full-program2026.html",
        "organizer": "American Finance Association",
        "extras": {
            "program_chair": "Wei Jiang",
            "acceptance_rate": None,
        }
    }
    
    data = {
        "conference": conf,
        "scrape_metadata": {
            "scraped_at": datetime.now().isoformat(),
            "source_url": "https://afajof.org/management/full-program2026.html",
            "program_url": "https://afajof.org/management/full-program2026.html",
            "script_name": "create_v2_data.py",
            "program_available": True,
            "program_type": "web",
            "notes": "Full program with special events, panel sessions, and poster sessions. Scraped from AFA management site.",
            "errors": [],
        },
        "sessions": sessions,
        "participants": participants,
        "total_sessions": len(sessions),
        "total_papers": sum(len(s.get("papers", [])) for s in sessions),
        "total_participants": len(participants),
    }
    save_v2("afa2026", data)
    print(f"  Sessions: {len(sessions)}, Papers: {data['total_papers']}")

# ── 2. CEPRPS 2026 ────────────────────────────────────────────
def ceprps_v2():
    data = {
        "conference": {
            "name": "CEPR Paris Symposium",
            "short_name": "CEPRPS 2026",
            "year": 2026,
            "edition": "5th Edition",
            "start_date": "2026-12-08",
            "end_date": "2026-12-10",
            "location": "Paris, France",
            "venue": "",
            "city": "Paris",
            "country": "France",
            "website": "https://cepr.org/events/event-series/cepr-paris-symposium",
            "organizer": "Centre for Economic Policy Research (CEPR)",
            "description": "The 5th edition of CEPR's annual flagship symposium. No dedicated event page or program has been published yet as of June 2026.",
            "extras": {
                "event_series_url": "https://cepr.org/events/event-series/cepr-paris-symposium",
                "past_program_url_2025": "https://cepr.org/system/files/2025-10/2025_Paris_Sym_Prelim.pdf",
                "likely_venues": ["Banque de France", "Collège de France", "Sciences Po"],
            }
        },
        "scrape_metadata": {
            "scraped_at": datetime.now().isoformat(),
            "source_url": "https://cepr.org/events/event-series/cepr-paris-symposium",
            "program_url": None,
            "script_name": "create_v2_data.py",
            "program_available": False,
            "program_type": "web",
            "notes": "CEPR Paris Symposium 2026 not yet published. Dedicated page returned 404. Event expected December 2026.",
            "errors": ["CEPR event page returned 404", "No program URL available yet"],
        },
        "sessions": [],
        "participants": [],
        "total_sessions": 0,
        "total_papers": 0,
        "total_participants": 0,
    }
    save_v2("ceprps2026", data)

# ── 3. ECBARC 2026 ────────────────────────────────────────────
def ecbarc_v2():
    data = {
        "conference": {
            "name": "ECB Annual Research Conference",
            "short_name": "ECBARC 2026",
            "year": 2026,
            "edition": "11th Edition",
            "start_date": "2026-09-21",
            "end_date": "2026-09-22",
            "location": "Frankfurt, Germany",
            "venue": "",
            "city": "Frankfurt",
            "country": "Germany",
            "website": "https://www.ecb.europa.eu/press/conferences/html/index.en.html",
            "organizer": "European Central Bank",
            "description": "The 11th ECB Annual Research Conference. The conference is listed on the ECB conferences index page but no dedicated page or programme has been published yet.",
            "extras": {
                "theme": "Geoeconomics and the international trading system (tentative from ECB page)",
                "conference_type": "Flagship Annual Research Conference",
                "contact_email": "ARConference@ecb.europa.eu",
                "reference_2025_theme": "The Next Financial Crisis?",
                "reference_2025_joint_with": "Stanford's Hoover Institution",
            }
        },
        "scrape_metadata": {
            "scraped_at": datetime.now().isoformat(),
            "source_url": "https://www.ecb.europa.eu/press/conferences/html/index.en.html",
            "program_url": None,
            "script_name": "create_v2_data.py",
            "program_available": False,
            "program_type": "web",
            "notes": "ECB ARC 2026 listed on ECB conferences page but no dedicated page or program published yet. The conferences index entry has NO hyperlink, unlike other upcoming conferences, suggesting page not created yet.",
            "errors": [
                "https://www.ecb.europa.eu/press/conferences/html/20260916_11th_ecb_annual_research_conference.en.html -> 404",
                "https://www.ecb.europa.eu/press/conferences/html/20260916_ecb_annual_research_conference.en.html -> 404",
            ],
        },
        "sessions": [],
        "participants": [],
        "total_sessions": 0,
        "total_papers": 0,
        "total_participants": 0,
    }
    save_v2("ecbarc2026", data)

# ── 4. CMRC 2026 ──────────────────────────────────────────────
def cmrc_v2():
    old = load_old("cmrc2026")
    
    # Build conference from existing data
    participants = []
    
    # Extract keynotes
    keynotes = old.get("keynotes", [])
    for k in keynotes:
        speaker = k.get("speaker", {})
        participants.append({
            "name": speaker.get("name", ""),
            "institution": speaker.get("organization", ""),
            "role": "Keynote Speaker",
            "is_presenter": True,
            "papers": [],
            "paper_titles": [f"Keynote: {k.get('type', 'Keynote')}"],
        })
    
    # Emerging scholars
    for es in old.get("emerging_scholars", []):
        participants.append({
            "name": es.get("name", ""),
            "institution": es.get("university", ""),
            "role": "Emerging Scholar",
            "is_presenter": True,
            "papers": [],
            "paper_titles": [],
        })
    
    data = {
        "conference": {
            "name": "Community Banking Research Conference",
            "short_name": "CMRC 2026",
            "year": 2026,
            "edition": "14th Annual",
            "start_date": "2026-10-06",
            "end_date": "2026-10-07",
            "location": "St. Louis, MO, USA",
            "venue": "Gateway Auditorium, Federal Reserve Bank of St. Louis",
            "city": "St. Louis",
            "country": "USA",
            "website": "https://www.communitybanking.org/conferences/2026",
            "organizer": "Federal Reserve System, CSBS, FDIC",
            "description": old.get("conference", {}).get("description", "The fourteenth annual Community Banking Research Conference brings together community bankers, academics, policymakers and bank regulators."),
            "extras": {
                "organizers": old.get("conference", {}).get("organizers", []),
                "keynotes": [
                    {
                        "speaker": k.get("speaker", {}).get("name", ""),
                        "type": k.get("type", ""),
                        "organization": k.get("speaker", {}).get("organization", ""),
                    } for k in keynotes
                ],
                "emerging_scholars": [es.get("name", "") for es in old.get("emerging_scholars", [])],
                "case_study_competition": "CSBS Community Bank Case Study Competition with 35 student teams",
                "cfp_deadline": "2026-05-01",
                "author_notification": "2026-06-22",
            }
        },
        "scrape_metadata": {
            "scraped_at": datetime.now().isoformat(),
            "source_url": "https://www.communitybanking.org/conferences/2026",
            "program_url": "https://www.communitybanking.org/conferences/2026",
            "script_name": "create_v2_data.py",
            "program_available": False,
            "program_type": "web",
            "notes": "Conference website is an AngularJS SPA. Detailed program (sessions, paper presentations) not yet published as of June 2026. Call for papers closed May 1, 2026; author notifications by June 22, 2026.",
            "errors": ["Detailed program/sessions not published yet"],
        },
        "sessions": [],
        "participants": participants,
        "total_sessions": 0,
        "total_papers": 0,
        "total_participants": len(participants),
    }
    save_v2("cmrc2026", data)
    print(f"  Participants: {len(participants)}")

# ── 5. MYE 2026 ───────────────────────────────────────────────
def mye_v2():
    data = {
        "conference": {
            "name": "EAYE Annual Meeting (formerly Spring Meeting of Young Economists)",
            "short_name": "MYE 2026",
            "year": 2026,
            "edition": "2026 Edition (30th Anniversary)",
            "start_date": "2026-05-18",
            "end_date": "2026-05-20",
            "location": "Bilbao, Spain",
            "venue": "Bizkaia Aretoa",
            "city": "Bilbao",
            "country": "Spain",
            "website": "https://www.eaye.info/",
            "program_url": "https://www.eaye.info/eayeam/2026-edition/program-2026",
            "organizer": "European Association of Young Economists (EAYE)",
            "description": "The European Association of Young Economists (EAYE) Annual Meeting, formerly called the Spring Meeting of Young Economists (SMYE). The 2026 edition is hosted by the University of the Basque Country in Bilbao, Spain.",
            "extras": {
                "former_name": "Spring Meeting of Young Economists (SMYE)",
                "host": "University of the Basque Country",
                "keynote_speakers": [
                    {"name": "Manuel Arellano", "institution": "CEMFI"},
                    {"name": "Giacomo Ponzetto", "institution": "CREI and Universitat Pompeu Fabra"},
                ],
                "submission_system": "CMT (Microsoft)",
                "submission_deadline": "2025-12-28",
                "conference_dinner_venue": "San Joseren Jauregia, Getxo",
                "cocktail_reception": "Menchu Gal terrace at Bizkaia Aretoa",
                "original_domain": "smye.org (expired, redirected to GoDaddy)",
                "new_domain": "eaye.info",
            }
        },
        "scrape_metadata": {
            "scraped_at": datetime.now().isoformat(),
            "source_url": "https://www.eaye.info/",
            "program_url": "https://www.eaye.info/eayeam/2026-edition/program-2026",
            "script_name": "create_v2_data.py",
            "program_available": True,
            "program_type": "web",
            "notes": "SMYE domain (smye.org, smye2026.org) has expired. The conference has moved to eaye.info under EAYE branding. Conference already took place May 18-20, 2026 in Bilbao. Program page exists but detailed schedule not yet published online. Keynote speakers confirmed: Manuel Arellano (CEMFI) and Giacomo Ponzetto (CREI, UPF).",
            "errors": [
                "smye.org -> domain expired, redirected to GoDaddy parking",
                "smye2026.org -> DNS resolution failure",
                "Program page has no detailed schedule content published",
            ],
        },
        "sessions": [],
        "participants": [
            {
                "name": "Manuel Arellano",
                "institution": "CEMFI",
                "role": "Keynote Speaker",
                "is_presenter": True,
                "papers": [],
                "paper_titles": [],
            },
            {
                "name": "Giacomo Ponzetto",
                "institution": "CREI and Universitat Pompeu Fabra",
                "role": "Keynote Speaker",
                "is_presenter": True,
                "papers": [],
                "paper_titles": [],
            },
        ],
        "papers": [],
        "total_sessions": 0,
        "total_papers": 0,
        "total_participants": 2,
    }
    save_v2("mye2026", data)
    print(f"  Participants: 2 (keynote speakers)")

# ── Run all ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== AFA 2026 ===")
    afa_v2()
    print()
    print("=== CEPRPS 2026 ===")
    ceprps_v2()
    print()
    print("=== ECBARC 2026 ===")
    ecbarc_v2()
    print()
    print("=== CMRC 2026 ===")
    cmrc_v2()
    print()
    print("=== MYE 2026 ===")
    mye_v2()
    print()
    print("✅ All v2 data.json files created!")
