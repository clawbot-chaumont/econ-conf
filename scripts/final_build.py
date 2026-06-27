#!/usr/bin/env python3
"""
Final: Rebuild ALL 5 conferences to v2, update Sheet + Drive.
Reads from archives and web sources, produces valid v2 data.json.
"""
import json, os, sys, re
from datetime import datetime, timezone

DATA_DIR = os.path.expanduser("~/economics-conferences")
NOW_ISO = datetime.now(timezone.utc).isoformat()

def write_v2(folder, data):
    d = os.path.join(DATA_DIR, folder)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "data.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ {folder}/data.json: {len(data.get('sessions',[]))} sessions, {len(data.get('participants',[]))} participants")
    return p

# ═══ GDRE ═══════════════════════════════════════════════════════
def build_gdre():
    return {
        "conference": {
            "name": "42nd International Symposium on Money, Banking and Finance (GDRE)",
            "short_name": "GDRE 2026",
            "year": 2026,
            "edition": "42nd International Symposium",
            "start_date": "2026-06-25",
            "end_date": "2026-06-26",
            "location": "Rennes, France",
            "venue": "University of Rennes, Faculty of Economics",
            "city": "Rennes", "country": "France",
            "website": "https://gdre-2026.sciencesconf.org",
            "program_url": "https://gdre-2026.sciencesconf.org/page/program?lang=en",
            "organizer": "European Research Group (GdRE) on Money, Banking and Finance",
            "description": "Annual meeting of the European Research Group on Money, Banking and Finance.",
            "extras": {
                "keynote_speaker": "Pierpaolo Benigno (University of Bern / Luiss Guido Carli University)",
                "important_dates": {"submission_deadline": "2026-03-02", "registration_deadline": "2026-05-27"},
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
            "notes": "High-level schedule only (5 parallel sessions). Detailed paper-level data not published online.",
            "errors": []
        },
        "sessions": [
            {"session_id":"S001","session_title":"Parallel Session I","session_type":"Contributed","day":"Thursday","date":"2026-06-25","time":"11:00 - 12:30","papers":[]},
            {"session_id":"S002","session_title":"Parallel Session II","session_type":"Contributed","day":"Thursday","date":"2026-06-25","time":"14:00 - 15:30","papers":[]},
            {"session_id":"S003","session_title":"Panel Discussion","session_type":"Panel","day":"Thursday","date":"2026-06-25","time":"16:00 - 17:30","papers":[]},
            {"session_id":"S004","session_title":"Parallel Session III","session_type":"Contributed","day":"Friday","date":"2026-06-26","time":"09:00 - 10:30","papers":[]},
            {"session_id":"S005","session_title":"Parallel Session IV","session_type":"Contributed","day":"Friday","date":"2026-06-26","time":"11:00 - 12:30","papers":[]},
            {"session_id":"S006","session_title":"Parallel Session V","session_type":"Contributed","day":"Friday","date":"2026-06-26","time":"14:00 - 15:30","papers":[]}
        ],
        "papers":[], "participants":[],
        "total_sessions":6,"total_papers":0,"total_participants":0
    }

# ═══ EEA ═══════════════════════════════════════════════════════
def build_eea():
    tsv_path = os.path.join(DATA_DIR, "eea2026", "all_sessions.tsv")
    with open(tsv_path) as f:
        lines = [l.strip() for l in f if l.strip()]
    
    sessions = []
    participants_dict = {}
    
    for i, line in enumerate(lines):
        parts = line.split("\t")
        if len(parts) < 8:
            continue
        title, presenters_raw, stype, field, date_str, time_str, length, room = parts[:8]
        
        # Convert date
        date_iso = ""
        day_name = ""
        if "/" in date_str:
            try:
                d, m = date_str.split("/")
                from datetime import date as dt
                dt_obj = dt(2026, int(m), int(d))
                date_iso = dt_obj.isoformat()
                day_name = dt_obj.strftime("%A")
            except:
                pass
        
        stype_clean = stype.replace(" Sessions","").replace(" Address","")
        
        sid = f"EEA-S{i+1:04d}"
        sessions.append({
            "session_id": sid,
            "session_title": title,
            "session_type": stype_clean,
            "track": field if field else "",
            "day": day_name,
            "date": date_iso,
            "time": time_str,
            "room": room,
            "papers": []
        })
        
        # Extract presenters (concatenated, no separator)
        pres = presenters_raw.strip()
        if pres and pres not in ("Presenter","Presenter(s)"):
            # Split on transitions from lowercase to uppercase
            names = re.split(r'(?<=[a-záéíóúàèìòùäëïöüñç])(?=[A-ZÁÉÍÓÚÀÈÌÒÙÄËÏÖÜÑÇ][a-záéíóúàèìòùäëïöüñç])', pres)
            for n in names:
                n = n.strip()
                if len(n) > 2 and not n.startswith("Add to"):
                    key = n.lower()
                    if key not in participants_dict:
                        participants_dict[key] = {
                            "name": n, "institution": "",
                            "is_presenter": True, "papers": []
                        }
                    if title not in participants_dict[key]["papers"]:
                        participants_dict[key]["papers"].append(title)
    
    conf = {
        "name": "41st Meeting of the European Economic Association and 77th European Meeting of the Econometric Society",
        "short_name": "EEA 2026",
        "year": 2026,
        "edition": "41st EEA Congress / 77th ESEM",
        "start_date": "2026-08-17",
        "end_date": "2026-08-21",
        "location": "Dublin, Ireland",
        "venue": "University College Dublin",
        "city": "Dublin", "country": "Ireland",
        "website": "https://www.eea-esem-congresses.org/",
        "program_url": "https://www.eea-esem-congresses.org/full-programme",
        "organizer": "European Economic Association",
        "description": "Annual congress of the European Economic Association.",
        "extras": {
            "keynote_speakers": [
                "Melissa S. Kearney (Notre Dame) - Marshall Lecture",
                "Nobu Kiyotaki (Princeton) - ES Presidential Address",
                "Imran Rasul (UCL & IFS) - EEA Presidential Address",
                "Raj Chetty (Harvard) - Fisher-Schultz Lecture",
                "Nava Ashraf (LSE) - Laffont Lecture",
                "Gianluca Violante (Princeton) - Schumpeter Lecture"
            ],
            "registration_fees": {"regular_member": "€495", "regular_non_member": "€990"}
        }
    }
    
    return {
        "conference": conf,
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://www.eea-esem-congresses.org/",
            "program_url": "https://www.eea-esem-congresses.org/full-programme",
            "script_name": "scrape_all_v2.py",
            "program_available": True,
            "program_type": "web",
            "notes": f"Extracted {len(sessions)} sessions from full programme view (5 paginated pages). Session-level only, no paper-level details.",
            "errors": []
        },
        "sessions": sessions,
        "papers": [],
        "participants": list(participants_dict.values()),
        "total_sessions": len(sessions),
        "total_papers": 0,
        "total_participants": len(participants_dict)
    }

# ═══ RES ═══════════════════════════════════════════════════════
def build_res():
    archive = os.path.join(DATA_DIR, "_archive", "res2026_data.json")
    with open(archive) as f:
        old = json.load(f)
    
    # Restore old data to res2026/data.json for reference
    with open(os.path.join(DATA_DIR, "res2026", "data.json"), "w") as f:
        json.dump(old, f, indent=2, ensure_ascii=False)
    
    conf = {
        "name": "Royal Economic Society Annual Conference",
        "short_name": "RES 2026",
        "year": 2026,
        "edition": "RES Annual Conference",
        "start_date": "2026-07-06",
        "end_date": "2026-07-08",
        "location": "Newcastle, United Kingdom",
        "venue": "Newcastle University",
        "city": "Newcastle", "country": "United Kingdom",
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
    
    sessions = []
    participants_dict = {}
    
    # Keynotes
    for i, kn in enumerate(old.get("keynotes", [])):
        speaker = kn.get("speaker", kn.get("speakers", ""))
        if isinstance(speaker, list):
            speaker = "; ".join(speaker)
        
        date_raw = kn.get("day", "")
        date_iso = day_name = ""
        if "6 July" in date_raw: date_iso = "2026-07-06"; day_name = "Monday"
        elif "7 July" in date_raw: date_iso = "2026-07-07"; day_name = "Tuesday"
        elif "8 July" in date_raw: date_iso = "2026-07-08"; day_name = "Wednesday"
        
        s = {
            "session_id": f"RES-K{i+1:02d}",
            "session_title": kn.get("title",""),
            "session_type": "Keynote",
            "day": day_name,
            "date": date_iso,
            "time": kn.get("time",""),
            "room": kn.get("venue",""),
            "chair": kn.get("chair",""),
            "papers": []
        }
        sessions.append(s)
        
        if speaker:
            for sp in ([speaker] if isinstance(speaker, str) else speaker):
                sp = sp.strip()
                if sp and sp not in participants_dict:
                    participants_dict[sp] = {"name": sp, "institution": kn.get("affiliation",""), "is_presenter": True, "papers": [kn.get("title","")]}
    
    # Special sessions
    for i, ss in enumerate(old.get("special_sessions", [])):
        date_raw = ss.get("day","")
        date_iso = day_name = ""
        if "6 July" in date_raw: date_iso = "2026-07-06"; day_name = "Monday"
        elif "7 July" in date_raw: date_iso = "2026-07-07"; day_name = "Tuesday"
        elif "8 July" in date_raw: date_iso = "2026-07-08"; day_name = "Wednesday"
        
        chairs = ss.get("chairs", ss.get("chair", ""))
        if isinstance(chairs, list): chairs = "; ".join(chairs)
        
        sessions.append({
            "session_id": f"RES-SS{i+1:02d}",
            "session_title": ss.get("title",""),
            "session_type": "Special Session",
            "day": day_name,
            "date": date_iso,
            "time": ss.get("time",""),
            "chair": chairs,
            "papers": []
        })
    
    # General sessions (session blocks)
    for date_str, day_data in old.get("general_sessions", {}).items():
        date_iso = day_name = ""
        if "6 July" in date_str: date_iso = "2026-07-06"; day_name = "Monday"
        elif "7 July" in date_str: date_iso = "2026-07-07"; day_name = "Tuesday"
        elif "8 July" in date_str: date_iso = "2026-07-08"; day_name = "Wednesday"
        
        for block_key in ["session_1", "session_2"]:
            block = day_data.get(block_key, {})
            time = block.get("time","")
            for s in block.get("sessions", []):
                code = s.get("code","")
                title = s.get("title","")
                venue = s.get("venue","")
                chair = s.get("chair","")
                sid = f"RES-{code}" if code else f"RES-G{len(sessions)+1:04d}"
                sessions.append({
                    "session_id": sid,
                    "session_title": f"{code}: {title}" if code else title,
                    "session_type": "General",
                    "day": day_name,
                    "date": date_iso,
                    "time": time,
                    "room": venue,
                    "chair": chair.strip() if isinstance(chair, str) else "",
                    "papers": []
                })
    
    return {
        "conference": conf,
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://res.org.uk/event-listing/res-2026-annual-conference/",
            "program_url": "https://virtual.oxfordabstracts.com/event/76093/program",
            "script_name": "scrape_all_v2.py",
            "program_available": True,
            "program_type": "web",
            "notes": f"Converted from RES archive: {len(sessions)} sessions (keynotes + special sessions + general sessions). Paper titles within sessions require JS interaction on Oxford Abstracts.",
            "errors": []
        },
        "sessions": sessions,
        "papers": [],
        "participants": list(participants_dict.values()),
        "total_sessions": len(sessions),
        "total_papers": 0,
        "total_participants": len(participants_dict)
    }

# ═══ CEBRA ═════════════════════════════════════════════════════
def build_cebra():
    conf = {
        "name": "Central Bank Research Association Annual Meeting",
        "short_name": "CEBRA 2026",
        "year": 2026,
        "edition": "2026 Annual Meeting",
        "start_date": "2026-06-22",
        "end_date": "2026-06-24",
        "location": "Copenhagen, Denmark",
        "venue": "Bella Sky Conference & Event / University of Copenhagen",
        "city": "Copenhagen", "country": "Denmark",
        "website": "https://cebra.org/meeting/",
        "program_url": "https://cebra-events.org/program-summary26",
        "organizer": "Central Bank Research Association (CEBRA)",
        "description": "Annual meeting of the Central Bank Research Association, co-organized with Danmarks Nationalbank and University of Copenhagen.",
        "extras": {
            "co_organizers": ["Danmarks Nationalbank", "University of Copenhagen"],
            "panels": [
                "Panel 1: The Global Financial System and the Role of the US Dollar",
                "Panel 2: Geoeconomic Fragmentation: Drivers, Dynamics, and Global Consequences",
                "Panel 3: Revisiting Trade Policy: Tariffs, Protectionism, and Global Integration"
            ]
        }
    }
    
    sessions = [
        {"session_id":"CEBRA-S001","session_title":"Welcome and Opening Remarks","session_type":"Plenary","day":"Monday","date":"2026-06-22","time":"11:45 - 12:00","papers":[]},
        {"session_id":"CEBRA-S002","session_title":"ChaMP Network Results Presentation","session_type":"Presentation","day":"Monday","date":"2026-06-22","time":"12:00 - 13:00","papers":[]},
        {"session_id":"CEBRA-S003","session_title":"Panel 1: The Global Financial System and the Role of the US Dollar","session_type":"Panel","day":"Monday","date":"2026-06-22","time":"14:00 - 15:30","papers":[]},
        {"session_id":"CEBRA-S004","session_title":"Panel 2: Geoeconomic Fragmentation: Drivers, Dynamics, and Global Consequences","session_type":"Panel","day":"Monday","date":"2026-06-22","time":"16:00 - 17:30","papers":[]},
        {"session_id":"CEBRA-S005","session_title":"Parallel Session 1 (Tracks A-G)","session_type":"Parallel Session","day":"Tuesday","date":"2026-06-23","time":"09:00 - 11:00","papers":[]},
        {"session_id":"CEBRA-S006","session_title":"Panel 3: Revisiting Trade Policy","session_type":"Panel","day":"Tuesday","date":"2026-06-23","time":"11:30 - 13:00","papers":[]},
        {"session_id":"CEBRA-S007","session_title":"Poster Session for Early-Career Economists","session_type":"Poster","day":"Tuesday","date":"2026-06-23","time":"13:00 - 14:15","papers":[]},
        {"session_id":"CEBRA-S008","session_title":"Parallel Session 2 (Tracks A-G)","session_type":"Parallel Session","day":"Tuesday","date":"2026-06-23","time":"14:15 - 16:15","papers":[]},
        {"session_id":"CEBRA-S009","session_title":"Parallel Session 3 (Tracks A-G)","session_type":"Parallel Session","day":"Tuesday","date":"2026-06-23","time":"16:30 - 18:30","papers":[]},
        {"session_id":"CEBRA-S010","session_title":"Parallel Session 4 (Tracks A-G)","session_type":"Parallel Session","day":"Wednesday","date":"2026-06-24","time":"08:45 - 10:45","papers":[]},
        {"session_id":"CEBRA-S011","session_title":"Parallel Session 5 (Tracks A-G)","session_type":"Parallel Session","day":"Wednesday","date":"2026-06-24","time":"11:15 - 13:15","papers":[]},
        {"session_id":"CEBRA-S012","session_title":"CEBRA Annual General Assembly","session_type":"Meeting","day":"Wednesday","date":"2026-06-24","time":"13:45 - 14:30","papers":[]},
        {"session_id":"CEBRA-S013","session_title":"Parallel Session 6 (Tracks A-G)","session_type":"Parallel Session","day":"Wednesday","date":"2026-06-24","time":"14:30 - 16:30","papers":[]}
    ]
    
    return {
        "conference": conf,
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://cebra.org/meeting/",
            "program_url": "https://cebra-events.org/program-summary26",
            "script_name": "scrape_all_v2.py",
            "program_available": True,
            "program_type": "web",
            "notes": "Program summary extracted from cebra-events.org. Track-level session data requires login. 13 sessions identified from the public schedule.",
            "errors": []
        },
        "sessions": sessions,
        "papers": [],
        "participants": [],
        "total_sessions": len(sessions),
        "total_papers": 0,
        "total_participants": 0
    }

# ═══ SFS ═══════════════════════════════════════════════════════
def build_sfs():
    archive = os.path.join(DATA_DIR, "_archive", "sfs2026_data.json")
    with open(archive) as f:
        old = json.load(f)
    
    conf = {
        "name": "Society for Financial Studies Cavalcade North America",
        "short_name": "SFS 2026",
        "year": 2026,
        "edition": "SFS Cavalcade North America 2026",
        "start_date": "2026-05-18",
        "end_date": "2026-05-21",
        "location": "Charlottesville, USA",
        "venue": "Darden Graduate School of Business, University of Virginia",
        "city": "Charlottesville", "country": "USA",
        "website": "https://sfs.org/cavalcade/",
        "program_url": "https://www.conftool.com/sfs-cavalcade-2026/sessions.php",
        "organizer": "Society for Financial Studies",
        "description": "Premier academic finance conference covering all areas of finance. First North American edition.",
        "extras": {
            "first_north_american_edition": True,
            "submission_system": "ConfTool"
        }
    }
    
    sessions = []
    participants_dict = {}
    paper_count = 0
    
    program = old.get("program", {})
    for date_iso, day_sessions in program.items():
        for s in day_sessions:
            if s.get("type") != "track":
                continue
            
            papers_data = s.get("papers", [])
            papers = []
            for p in papers_data:
                paper_count += 1
                title = p.get("title", "")
                authors_raw = p.get("authors", "")
                affiliations = p.get("affiliations", "")
                
                authors = [a.strip() for a in authors_raw.split(",") if a.strip()] if authors_raw else []
                presenter = authors[0] if authors else ""
                
                papers.append({
                    "paper_id": f"SFS-P{paper_count:04d}",
                    "title": title,
                    "authors": authors,
                    "presenter": presenter,
                    "abstract": ""
                })
                
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
            
            day_name = {"2026-05-18":"Monday","2026-05-19":"Tuesday","2026-05-20":"Wednesday","2026-05-21":"Thursday"}.get(str(date_iso), "")
            
            sid = f"SFS-T{len(sessions)+1:04d}"
            sessions.append({
                "session_id": sid,
                "session_title": s.get("title",""),
                "session_type": "Track Session",
                "track": s.get("track",""),
                "day": day_name,
                "date": str(date_iso),
                "time": s.get("time",""),
                "room": s.get("location", s.get("room","")),
                "chair": s.get("chair",""),
                "papers": papers
            })
    
    return {
        "conference": conf,
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://sfs.org/cavalcade/",
            "program_url": "https://www.conftool.com/sfs-cavalcade-2026/sessions.php",
            "script_name": "scrape_all_v2.py",
            "program_available": True,
            "program_type": "web",
            "notes": f"Converted from SFS archive: {len(sessions)} track sessions, {paper_count} papers, {len(participants_dict)} participants.",
            "errors": []
        },
        "sessions": sessions,
        "papers": [],
        "participants": list(participants_dict.values()),
        "total_sessions": len(sessions),
        "total_papers": paper_count,
        "total_participants": len(participants_dict)
    }

# ═══ MAIN ══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("FINAL BUILD — All 5 Conferences to v2 Schema")
    print("=" * 60)
    
    print("\n📌 GDRE 2026")
    g = build_gdre()
    write_v2("gdre2026", g)
    
    print("\n📌 EEA 2026")
    e = build_eea()
    write_v2("eea2026", e)
    
    print("\n📌 RES 2026")
    r = build_res()
    write_v2("res2026", r)
    
    print("\n📌 CEBRA 2026")
    c = build_cebra()
    write_v2("cebra2026", c)
    
    print("\n📌 SFS 2026")
    s = build_sfs()
    write_v2("sfs2026", s)
    
    print("\n" + "=" * 60)
    print("✅ BUILD COMPLETE")
    print("=" * 60)
