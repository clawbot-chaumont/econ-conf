#!/usr/bin/env python3
"""
Comprehensive scraper for GDRE, EEA, RES, CEBRA, SFS -> v2 data.json
Then runs master_pipeline.py for sheet + Drive update.
"""
import json, os, re, sys, asyncio
from datetime import datetime, timezone
from playwright.async_api import async_playwright

DATA_DIR = os.path.expanduser("~/economics-conferences")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

NOW_ISO = datetime.now(timezone.utc).isoformat()

def load_existing(folder):
    path = os.path.join(DATA_DIR, folder, "data.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def write_v2(folder, data):
    conf_dir = os.path.join(DATA_DIR, folder)
    os.makedirs(conf_dir, exist_ok=True)
    path = os.path.join(conf_dir, "data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Écrit: {path}")
    return path

# ─── GDRE ──────────────────────────────────────────────────────────
def build_gdre():
    """GDRE: high-level schedule only, no detailed sessions/papers available."""
    data = {
        "conference": {
            "name": "42nd International Symposium on Money, Banking and Finance (GDRE)",
            "short_name": "GDRE 2026",
            "year": 2026,
            "edition": "42nd International Symposium",
            "start_date": "2026-06-25",
            "end_date": "2026-06-26",
            "location": "Rennes, France",
            "venue": "University of Rennes, Faculty of Economics",
            "city": "Rennes",
            "country": "France",
            "website": "https://gdre-2026.sciencesconf.org",
            "program_url": "https://gdre-2026.sciencesconf.org/page/program?lang=en",
            "organizer": "European Research Group (GdRE) on Money, Banking and Finance",
            "description": "Annual meeting of the European Research Group on Money, Banking and Finance.",
            "extras": {
                "keynote_speaker": "Pierpaolo Benigno (University of Bern / Luiss Guido Carli University)",
                "important_dates": {
                    "submission_deadline": "2026-03-02",
                    "registration_deadline": "2026-05-27"
                },
                "theme": "Money, Banking and Finance",
                "submission_system": "SciencesConf"
            }
        },
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://gdre-2026.sciencesconf.org",
            "program_url": "https://gdre-2026.sciencesconf.org/page/program?lang=en",
            "script_name": "scrape_all_v2.py",
            "program_available": True,
            "program_type": "web",
            "notes": "High-level schedule only (5 parallel sessions). Detailed session/papers/participants data was not published online as of scraping date.",
            "errors": []
        },
        "sessions": [
            {
                "session_id": "S001",
                "session_title": "Parallel Session I",
                "session_type": "Contributed",
                "day": "Thursday",
                "date": "2026-06-25",
                "time": "11:00 - 12:30",
                "papers": []
            },
            {
                "session_id": "S002",
                "session_title": "Parallel Session II",
                "session_type": "Contributed",
                "day": "Thursday",
                "date": "2026-06-25",
                "time": "14:00 - 15:30",
                "papers": []
            },
            {
                "session_id": "S003",
                "session_title": "Panel Discussion",
                "session_type": "Panel",
                "day": "Thursday",
                "date": "2026-06-25",
                "time": "16:00 - 17:30",
                "papers": []
            },
            {
                "session_id": "S004",
                "session_title": "Parallel Session III",
                "session_type": "Contributed",
                "day": "Friday",
                "date": "2026-06-26",
                "time": "09:00 - 10:30",
                "papers": []
            },
            {
                "session_id": "S005",
                "session_title": "Parallel Session IV",
                "session_type": "Contributed",
                "day": "Friday",
                "date": "2026-06-26",
                "time": "11:00 - 12:30",
                "papers": []
            },
            {
                "session_id": "S006",
                "session_title": "Parallel Session V",
                "session_type": "Contributed",
                "day": "Friday",
                "date": "2026-06-26",
                "time": "14:00 - 15:30",
                "papers": []
            }
        ],
        "papers": [],
        "participants": [],
        "total_sessions": 6,
        "total_papers": 0,
        "total_participants": 0
    }
    return data

# ─── EEA ───────────────────────────────────────────────────────────
async def scrape_eea_full_programme():
    """
    Try to get the full programme from EEA-ESEM 2026.
    The page is JS-rendered with pagination. We'll try the JSON API.
    """
    result = {"sessions": [], "participants": []}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Intercept XHR/fetch requests
        api_responses = []
        page.on("response", lambda resp: api_responses.append(resp) if resp.url.startswith("https://www.eea-esem-congresses.org") else None)
        
        try:
            await page.goto("https://www.eea-esem-congresses.org/full-programme", 
                          timeout=30000, wait_until="networkidle")
            
            # Try clicking pagination to load more
            for page_num in range(2, 9):
                try:
                    # Look for pagination button
                    btn = await page.query_selector(f"a[href*='page={page_num}']")
                    if btn:
                        await btn.click()
                        await page.wait_for_timeout(2000)
                    else:
                        break
                except:
                    break
            
            # Get all sessions from the table
            text = await page.inner_text("body")
            
            # Save full text
            with open(os.path.join(DATA_DIR, "eea2026", "full_programme_raw.txt"), "w") as f:
                f.write(text)
            
            # Parse sessions from the text
            sections = text.split("\n")
            
            session_pattern = re.compile(
                r"^(.+?)\t(.+?)\t(Contributed Sessions|Invited Sessions|Keynote Address|Lunch Sessions, Panel & Workshop|Social, Award & Meetings)\t(.*?)\t(\d{2}/\d{2})\t(\d{2}:\d{2})\t(.+?)\t(.+?)\t"
            )
            
            sessions = []
            current_date = None
            current_time = None
            
            for line in sections:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split("\t")
                if len(parts) >= 9:
                    title = parts[0].strip()
                    presenters = parts[1].strip() if len(parts) > 1 else ""
                    stype = parts[2].strip() if len(parts) > 2 else ""
                    field = parts[3].strip() if len(parts) > 3 else ""
                    date_str = parts[4].strip() if len(parts) > 4 else ""
                    time_str = parts[5].strip() if len(parts) > 5 else ""
                    length = parts[6].strip() if len(parts) > 6 else ""
                    room = parts[7].strip() if len(parts) > 7 else ""
                    
                    # Filter out non-session entries
                    if stype in ("Contributed Sessions", "Invited Sessions", "Keynote Address", 
                                "Lunch Sessions, Panel & Workshop", "Social, Award & Meetings"):
                        # Convert date DD/MM to YYYY-MM-DD
                        if date_str:
                            try:
                                day, month = date_str.split("/")
                                date_iso = f"2026-{int(month):02d}-{int(day):02d}"
                            except:
                                date_iso = ""
                        else:
                            date_iso = ""
                        
                        # Parse presenters
                        presenter_list = []
                        if presenters and presenters != "Presenter":
                            # Split by CamelCase boundaries and known separators
                            # Presenters are concatenated without separator in the raw text
                            pnames = re.findall(r'[A-Z][a-záéíóúàèìòùäëïöüñçÁÉÍÓÚÀÈÌÒÙÄËÏÖÜÑÇ]+(?:\s+[A-Z][a-záéíóúàèìòùäëïöüñçÁÉÍÓÚÀÈÌÒÙÄËÏÖÜÑÇ]+)*(?:\s+[A-Z]\.)?', presenters)
                            if not pnames:
                                pnames = [presenters]
                            presenter_list = [p.strip() for p in pnames if p.strip()]
                        
                        session_id = f"EEA-S{len(sessions)+1:04d}"
                        sessions.append({
                            "session_id": session_id,
                            "session_title": title,
                            "session_type": stype.replace(" Sessions", "").replace(" Address", ""),
                            "track": field if field else "",
                            "date": date_iso,
                            "time": time_str,
                            "room": room if room else "",
                            "papers": [],
                            "presenters": presenter_list
                        })
            
            # Build participants from presenters
            seen = set()
            participants = []
            for s in sessions:
                for pname in s.get("presenters", []):
                    key = pname.lower().strip()
                    if key and key not in seen:
                        seen.add(key)
                        participants.append({
                            "name": pname.strip(),
                            "institution": "",
                            "is_presenter": True,
                            "papers": [s["session_title"]]
                        })
                    elif key in seen:
                        # Add paper to existing participant
                        for p in participants:
                            if p["name"].lower() == key:
                                if s["session_title"] not in p["papers"]:
                                    p["papers"].append(s["session_title"])
                                break
            
            # Clean up - remove presenters from sessions (not part of v2 schema)
            for s in sessions:
                s.pop("presenters", None)
            
            result = {"sessions": sessions, "participants": participants}
            print(f"  EEA: {len(sessions)} sessions, {len(participants)} participants extracted")
            
        except Exception as e:
            print(f"  ⚠️ EEA scraping error: {e}")
        finally:
            await browser.close()
    
    return result

def build_eea(scraped):
    existing = load_existing("eea2026")
    
    # Merge existing info with scraped sessions
    conf = {
        "name": "41st Meeting of the European Economic Association and 77th European Meeting of the Econometric Society",
        "short_name": "EEA 2026",
        "year": 2026,
        "edition": "41st EEA Congress / 77th ESEM",
        "start_date": "2026-08-17",
        "end_date": "2026-08-21",
        "location": "Dublin, Ireland",
        "venue": "University College Dublin",
        "city": "Dublin",
        "country": "Ireland",
        "website": "https://www.eea-esem-congresses.org/",
        "program_url": "https://www.eea-esem-congresses.org/full-programme",
        "organizer": "European Economic Association",
        "description": "Annual congress of the European Economic Association and European Meeting of the Econometric Society.",
        "extras": {
            "keynote_speakers": {
                "EEA Marshall Lecture": "Melissa S. Kearney (University of Notre Dame)",
                "ES Presidential Address": "Nobu Kiyotaki (Princeton University)",
                "EEA Presidential Address": "Imran Rasul (UCL & IFS)",
                "ES Fisher-Schultz Lecture": "Raj Chetty (Harvard University)",
                "ES Laffont Lecture": "Nava Ashraf (London School of Economics)",
                "EEA Joseph Schumpeter Lecture": "Gianluca Violante (Princeton University)"
            },
            "registration_fees": {
                "regular_member": "€495",
                "regular_non_member": "€990",
                "phd_student_member": "€315",
                "phd_student_non_member": "€630"
            },
            "submission_system": "EEA-ESEM website"
        }
    }
    
    sessions = scraped.get("sessions", [])
    participants = scraped.get("participants", [])
    
    # If we got no sessions from the live scrape, fall back to the existing high-level overview
    if not sessions:
        print("  ⚠️ No detailed sessions from full-programme page, using existing overview data")
        # Reuse overview data from existing file
        if existing:
            # Just mark the program as partially available
            pass
    
    data = {
        "conference": conf,
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://www.eea-esem-congresses.org/",
            "program_url": "https://www.eea-esem-congresses.org/full-programme",
            "script_name": "scrape_all_v2.py",
            "program_available": len(sessions) > 0,
            "program_type": "web",
            "notes": f"Extracted {len(sessions)} sessions and {len(participants)} presenters from the EEA-ESEM full programme page."
                     if len(sessions) > 0 else 
                     "Detailed contributed session program was loading dynamically. Only overview available.",
            "errors": [] if len(sessions) > 0 else ["Full programme data was paginated via JS; only partial extraction possible"]
        },
        "sessions": sessions,
        "papers": [],
        "participants": participants,
        "total_sessions": len(sessions),
        "total_papers": sum(len(s.get("papers", [])) for s in sessions),
        "total_participants": len(participants)
    }
    return data

# ─── RES ───────────────────────────────────────────────────────────
def convert_res_to_v2():
    """Convert existing RES data to v2 schema."""
    existing = load_existing("res2026")
    if not existing:
        return create_empty_res()
    
    # Build conference info
    conf = {
        "name": "Royal Economic Society Annual Conference",
        "short_name": "RES 2026",
        "year": 2026,
        "edition": "RES Annual Conference",
        "start_date": "2026-07-06",
        "end_date": "2026-07-08",
        "location": "Newcastle, United Kingdom",
        "venue": "Newcastle University",
        "city": "Newcastle",
        "country": "United Kingdom",
        "website": "https://res.org.uk/event-listing/res-2026-annual-conference/",
        "program_url": "https://virtual.oxfordabstracts.com/event/76093/program",
        "organizer": "Royal Economic Society",
        "description": "Annual conference of the Royal Economic Society.",
        "extras": {
            "keynote_speakers": [
                "Sir Chris Pissarides (LSE) - Presidential Address",
                "Patrick Kline (UC Berkeley) - Sargan Lecture",
                "Ekaterina Zhuravskaya (PSE) - Economic Journal Lecture",
                "Manasi Deshpande (University of Chicago) - Hahn Lecture",
                "John Van Reenen (LSE/MIT) - Headline Lecture"
            ]
        }
    }
    
    # Extract sessions from existing data
    sessions = []
    participants = []
    seen_participants = {}
    
    # Process keynotes as sessions
    keynotes = existing.get("keynotes", [])
    for i, kn in enumerate(keynotes):
        speaker = kn.get("speaker", kn.get("speakers", ""))
        if isinstance(speaker, list):
            speaker = "; ".join(speaker)
        
        date_raw = kn.get("day", "")
        date_iso = ""
        if "6 July" in date_raw:
            date_iso = "2026-07-06"
        elif "7 July" in date_raw:
            date_iso = "2026-07-07"
        elif "8 July" in date_raw:
            date_iso = "2026-07-08"
        
        day_name = "Monday" if "6 July" in date_raw else "Tuesday" if "7 July" in date_raw else "Wednesday"
        
        sess = {
            "session_id": f"RES-K{i+1:02d}",
            "session_title": kn.get("title", ""),
            "session_type": "Keynote",
            "date": date_iso,
            "day": day_name,
            "time": kn.get("time", ""),
            "room": kn.get("venue", ""),
            "chair": kn.get("chair", ""),
            "papers": []
        }
        
        # Add speaker as participant
        if speaker:
            name = speaker
            if name and name not in seen_participants:
                seen_participants[name] = {
                    "name": name,
                    "institution": kn.get("affiliation", ""),
                    "is_presenter": True,
                    "papers": [kn.get("title", "")]
                }
        
        sessions.append(sess)
    
    # Process general sessions
    general = existing.get("general_sessions", {})
    for date_str, day_data in general.items():
        date_iso = ""
        day_name = ""
        if "6 July" in date_str:
            date_iso = "2026-07-06"
            day_name = "Monday"
        elif "7 July" in date_str:
            date_iso = "2026-07-07"
            day_name = "Tuesday"
        elif "8 July" in date_str:
            date_iso = "2026-07-08"
            day_name = "Wednesday"
        
        # Session blocks
        for key in ["session_1", "session_2"]:
            block = day_data.get(key, {})
            time = block.get("time", "")
            subsessions = block.get("sessions", [])
            for s in subsessions:
                code = s.get("code", "")
                title = s.get("title", "")
                venue = s.get("venue", "")
                chair = s.get("chair", "")
                
                sid = f"RES-{code}" if code else f"RES-G{len(sessions)+1:04d}"
                sessions.append({
                    "session_id": sid,
                    "session_title": f"{code}: {title}" if code else title,
                    "session_type": "General",
                    "date": date_iso,
                    "day": day_name,
                    "time": time,
                    "room": venue,
                    "chair": chair.strip() if isinstance(chair, str) else "",
                    "papers": []
                })
    
    # Process special sessions
    special = existing.get("special_sessions", [])
    for i, ss in enumerate(special):
        date_raw = ss.get("day", "")
        date_iso = ""
        day_name = ""
        if "6 July" in date_raw:
            date_iso = "2026-07-06"
            day_name = "Monday"
        elif "7 July" in date_raw:
            date_iso = "2026-07-07"
            day_name = "Tuesday"
        elif "8 July" in date_raw:
            date_iso = "2026-07-08"
            day_name = "Wednesday"
        
        chairs = ss.get("chairs", ss.get("chair", ""))
        if isinstance(chairs, list):
            chairs = "; ".join(chairs)
        
        sessions.append({
            "session_id": f"RES-SS{i+1:02d}",
            "session_title": ss.get("title", ""),
            "session_type": "Special Session",
            "date": date_iso,
            "day": day_name,
            "time": ss.get("time", ""),
            "chair": chairs,
            "papers": []
        })
    
    data = {
        "conference": conf,
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://res.org.uk/event-listing/res-2026-annual-conference/",
            "program_url": "https://virtual.oxfordabstracts.com/event/76093/program",
            "script_name": "scrape_all_v2.py",
            "program_available": True,
            "program_type": "web",
            "notes": f"Converted from existing data: {len(sessions)} sessions. Detailed paper titles within sessions require JS interaction on Oxford Abstracts.",
            "errors": []
        },
        "sessions": sessions,
        "papers": [],
        "participants": list(seen_participants.values()),
        "total_sessions": len(sessions),
        "total_papers": 0,
        "total_participants": len(seen_participants)
    }
    return data

def create_empty_res():
    return {
        "conference": {
            "name": "Royal Economic Society Annual Conference",
            "short_name": "RES 2026",
            "year": 2026,
            "start_date": "2026-07-06",
            "end_date": "2026-07-08",
            "location": "Newcastle, United Kingdom",
        },
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://res.org.uk/event-listing/res-2026-annual-conference/",
            "program_available": False,
            "errors": ["Program not found"]
        },
        "sessions": [], "papers": [], "participants": [],
        "total_sessions": 0, "total_papers": 0, "total_participants": 0
    }

# ─── CEBRA ─────────────────────────────────────────────────────────
def convert_cebra_to_v2():
    existing = load_existing("cebra2026")
    if not existing:
        return create_empty_cebra()
    
    conf = {
        "name": "Central Bank Research Association Annual Meeting",
        "short_name": "CEBRA 2026",
        "year": 2026,
        "edition": "2026 Annual Meeting",
        "start_date": "2026-06-22",
        "end_date": "2026-06-24",
        "location": "Copenhagen, Denmark",
        "venue": "Bella Sky Conference & Event / University of Copenhagen",
        "city": "Copenhagen",
        "country": "Denmark",
        "website": "https://cebra.org/meeting/",
        "program_url": "https://cebra-events.org/annual-meeting-2026",
        "organizer": "Central Bank Research Association (CEBRA)",
        "description": "Annual meeting of the Central Bank Research Association.",
        "extras": {
            "co_organizers": ["Danmarks Nationalbank", "University of Copenhagen"],
            "tracks": existing.get("tracks", {}),
            "poster_session": existing.get("poster_session", {})
        }
    }
    
    # Build sessions from tracks
    sessions = []
    seen_participants = {}
    session_id = 0
    
    tracks = existing.get("tracks", {})
    for track_key, track_data in tracks.items():
        track_name = track_data.get("name", "")
        for s in track_data.get("sessions", []):
            session_id += 1
            day_raw = s.get("day", "")
            date_iso = ""
            day_name = ""
            if "June 22" in day_raw:
                date_iso = "2026-06-22"; day_name = "Monday"
            elif "June 23" in day_raw:
                date_iso = "2026-06-23"; day_name = "Tuesday"
            elif "June 24" in day_raw:
                date_iso = "2026-06-24"; day_name = "Wednesday"
            
            chairs = s.get("chair", s.get("chairs", ""))
            if isinstance(chairs, list):
                chairs = "; ".join(chairs)
            
            sessions.append({
                "session_id": f"CEBRA-S{session_id:03d}",
                "session_title": s.get("title", ""),
                "session_type": "Parallel Session",
                "track": track_name,
                "day": day_name,
                "date": date_iso,
                "time": s.get("time", ""),
                "chair": chairs,
                "papers": []
            })
    
    # Add panel sessions from summary_program
    summary = existing.get("summary_program", {})
    for day_key, day_data in summary.items():
        for event in day_data.get("sessions", []):
            if "Panel" in event.get("event", ""):
                session_id += 1
                speakers = event.get("panelists", [])
                panelists_str = "; ".join(speakers) if speakers else ""
                
                # Determine date
                date_iso = ""
                day_name = ""
                if "june_22" in day_key.lower():
                    date_iso = "2026-06-22"; day_name = "Monday"
                elif "june_23" in day_key.lower():
                    date_iso = "2026-06-23"; day_name = "Tuesday"
                elif "june_24" in day_key.lower():
                    date_iso = "2026-06-24"; day_name = "Wednesday"
                
                sessions.append({
                    "session_id": f"CEBRA-S{session_id:03d}",
                    "session_title": event.get("event", ""),
                    "session_type": "Panel",
                    "day": day_name,
                    "date": date_iso,
                    "time": event.get("time", ""),
                    "chair": event.get("moderator", ""),
                    "papers": [],
                    "panelists": panelists_str
                })
                
                # Add panelists as participants
                for sp in speakers:
                    if sp.strip() and sp not in seen_participants:
                        seen_participants[sp] = {
                            "name": sp,
                            "institution": "",
                            "is_presenter": True,
                            "papers": [event.get("event", "")]
                        }
    
    # Add poster session authors
    poster = existing.get("poster_session", {})
    poster_authors = poster.get("presenting_authors", [])
    for author in poster_authors:
        if author not in seen_participants:
            seen_participants[author] = {
                "name": author,
                "institution": "",
                "is_presenter": True,
                "papers": ["Poster Session for Early-Career Economists"]
            }
    
    data = {
        "conference": conf,
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://cebra.org/meeting/",
            "program_url": "https://cebra-events.org/annual-meeting-2026",
            "script_name": "scrape_all_v2.py",
            "program_available": True,
            "program_type": "web",
            "notes": f"Converted from existing scrape: {len(sessions)} sessions from 7 tracks. Paper-level details require login.",
            "errors": []
        },
        "sessions": sessions,
        "papers": [],
        "participants": list(seen_participants.values()),
        "total_sessions": len(sessions),
        "total_papers": 0,
        "total_participants": len(seen_participants)
    }
    return data

def create_empty_cebra():
    return {
        "conference": {"name": "Central Bank Research Association Annual Meeting", "short_name": "CEBRA 2026", "year": 2026, "start_date": "2026-08-27", "end_date": "2026-08-28", "location": "USA"},
        "scrape_metadata": {"scraped_at": NOW_ISO, "source_url": "https://cebra.org/meeting/", "program_available": False, "errors": ["Program not found"]},
        "sessions": [], "papers": [], "participants": [],
        "total_sessions": 0, "total_papers": 0, "total_participants": 0
    }

# ─── SFS ───────────────────────────────────────────────────────────
def convert_sfs_to_v2():
    existing = load_existing("sfs2026")
    if not existing:
        return create_empty_sfs()
    
    conf = {
        "name": "Society for Financial Studies Cavalcade North America",
        "short_name": "SFS 2026",
        "year": 2026,
        "edition": "SFS Cavalcade North America 2026",
        "start_date": "2026-05-18",
        "end_date": "2026-05-21",
        "location": "Charlottesville, USA",
        "venue": "Darden Graduate School of Business, University of Virginia",
        "city": "Charlottesville",
        "state": "Virginia",
        "country": "USA",
        "website": "https://sfs.org/cavalcade/",
        "program_url": "https://www.conftool.com/sfs-cavalcade-2026/sessions.php",
        "organizer": "Society for Financial Studies",
        "description": "Premier academic finance conference covering all areas of finance.",
        "extras": {
            "first_north_american_edition": True,
            "submission_system": "ConfTool"
        }
    }
    
    # Build sessions from program
    sessions = []
    participants_dict = {}
    paper_count = 0
    session_id_counter = 0
    
    program = existing.get("program", {})
    for date_iso, day_sessions in program.items():
        for s in day_sessions:
            if s.get("type") != "track":
                continue  # Skip special events
            
            session_id_counter += 1
            papers_data = s.get("papers", [])
            chair_raw = s.get("chair", "")
            discussant_raw = s.get("discussant", "")
            
            papers = []
            for p in papers_data:
                paper_count += 1
                title = p.get("title", "")
                authors_raw = p.get("authors", "")
                affiliations = p.get("affiliations", "")
                
                # Parse authors
                authors = [a.strip() for a in authors_raw.split(",") if a.strip()] if authors_raw else []
                
                # Identify presenter (first author)
                presenter = authors[0] if authors else ""
                
                paper_data = {
                    "paper_id": f"SFS-P{paper_count:04d}",
                    "title": title,
                    "authors": authors,
                    "presenter": presenter,
                    "abstract": ""
                }
                papers.append(paper_data)
                
                # Add participants
                for author in authors:
                    if author not in participants_dict:
                        participants_dict[author] = {
                            "name": author,
                            "institution": "",
                            "is_presenter": author == presenter,
                            "papers": []
                        }
                    if title not in participants_dict[author]["papers"]:
                        participants_dict[author]["papers"].append(title)
            
            # Determine date
            day_name = ""
            date_iso_clean = date_iso
            if "2026-05-18" in str(date_iso):
                day_name = "Monday"
            elif "2026-05-19" in str(date_iso):
                day_name = "Tuesday"
            elif "2026-05-20" in str(date_iso):
                day_name = "Wednesday"
            elif "2026-05-21" in str(date_iso):
                day_name = "Thursday"
            
            sessions.append({
                "session_id": f"SFS-T{session_id_counter:04d}",
                "session_title": s.get("title", ""),
                "session_type": "Track Session",
                "track": s.get("track", ""),
                "day": day_name,
                "date": str(date_iso_clean),
                "time": s.get("time", ""),
                "room": s.get("location", s.get("room", "")),
                "chair": chair_raw,
                "papers": papers
            })
    
    # Get affiliations for participants
    for s in sessions:
        for p in s.get("papers", []):
            for author in p.get("authors", []):
                if author in participants_dict:
                    # Try to get affiliation from paper data
                    pass  # Affiliations are embedded per-paper, hard to map
    
    data = {
        "conference": conf,
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://sfs.org/cavalcade/",
            "program_url": "https://www.conftool.com/sfs-cavalcade-2026/sessions.php",
            "script_name": "scrape_all_v2.py",
            "program_available": True,
            "program_type": "web",
            "notes": f"Converted from existing scrape: {len(sessions)} track sessions, {paper_count} papers, {len(participants_dict)} participants.",
            "errors": []
        },
        "sessions": sessions,
        "papers": [],
        "participants": list(participants_dict.values()),
        "total_sessions": len(sessions),
        "total_papers": paper_count,
        "total_participants": len(participants_dict)
    }
    return data

def create_empty_sfs():
    return {
        "conference": {"name": "Society for Financial Studies Cavalcade", "short_name": "SFS 2026", "year": 2026, "start_date": "2026-05-13", "end_date": "2026-05-15", "location": "USA"},
        "scrape_metadata": {"scraped_at": NOW_ISO, "source_url": "https://sfs.org/cavalcade/", "program_available": False, "errors": ["Program not found"]},
        "sessions": [], "papers": [], "participants": [],
        "total_sessions": 0, "total_papers": 0, "total_participants": 0
    }


# ─── MAIN ──────────────────────────────────────────────────────────
async def main():
    print("=" * 60)
    print("SCRAPING ALL CONFERENCES 2026 — v2 Schema")
    print("=" * 60)
    
    # 1. GDRE
    print("\n📌 GDRE 2026")
    gdre_data = build_gdre()
    write_v2("gdre2026", gdre_data)
    
    # 2. EEA
    print("\n📌 EEA 2026")
    try:
        eea_scraped = await scrape_eea_full_programme()
    except Exception as e:
        print(f"  ⚠️ EEA scraping failed: {e}")
        eea_scraped = {"sessions": [], "participants": []}
    eea_data = build_eea(eea_scraped)
    write_v2("eea2026", eea_data)
    
    # 3. RES
    print("\n📌 RES 2026")
    res_data = convert_res_to_v2()
    write_v2("res2026", res_data)
    
    # 4. CEBRA
    print("\n📌 CEBRA 2026")
    cebra_data = convert_cebra_to_v2()
    write_v2("cebra2026", cebra_data)
    
    # 5. SFS
    print("\n📌 SFS 2026")
    sfs_data = convert_sfs_to_v2()
    write_v2("sfs2026", sfs_data)
    
    print("\n" + "=" * 60)
    print("✅ ALL DATA FILES WRITTEN")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
