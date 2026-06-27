#!/usr/bin/env python3
"""Parse EEA TSV and produce v2 data.json for EEA 2026."""
import json, os, re
from datetime import datetime, timezone

DATA_DIR = os.path.expanduser("~/economics-conferences")
NOW_ISO = datetime.now(timezone.utc).isoformat()

def parse_tsv_line(line):
    """Parse a TSV line from the EEA full programme view."""
    parts = line.split("\t")
    if len(parts) < 10:
        return None
    
    title = parts[0].strip()
    presenters_raw = parts[1].strip() if len(parts) > 1 else ""
    stype = parts[2].strip() if len(parts) > 2 else ""
    field = parts[3].strip() if len(parts) > 3 else ""
    date_str = parts[4].strip() if len(parts) > 4 else ""
    time_str = parts[5].strip() if len(parts) > 5 else ""
    length = parts[6].strip() if len(parts) > 6 else ""
    room = parts[7].strip() if len(parts) > 7 else ""
    
    if not title or not stype:
        return None
    
    # Convert DD/MM to YYYY-MM-DD
    date_iso = ""
    day_name = ""
    if date_str and "/" in date_str:
        try:
            day, month = date_str.split("/")
            date_iso = f"2026-{int(month):02d}-{int(day):02d}"
            # Map to day name
            from datetime import date as dt_date
            d = dt_date(2026, int(month), int(day))
            day_name = d.strftime("%A")
        except:
            pass
    
    # Clean session type
    stype_clean = stype.replace(" Sessions", "").replace(" Address", "")
    
    return {
        "title": title,
        "presenters_raw": presenters_raw,
        "type": stype_clean,
        "field": field if field else "",
        "date": date_iso,
        "day": day_name,
        "time": time_str,
        "room": room
    }

def split_presenters(text):
    """Split concatenated presenter names (e.g. 'John SmithJane Doe')."""
    if not text or text == "Presenter" or text == "Presenter(s)":
        return []
    
    # Try splitting by common patterns
    # Names are concatenated: first and last name, then next person's first+last
    # Pattern: CapitalizedWord CapitalizedWord AnotherCapitalized...
    # This is tricky. Better approach: split by looking for transitions from 
    # lowercase to uppercase after a space
    names = []
    
    # First try splitting by semicolon or comma patterns
    if ";" in text:
        names = [n.strip() for n in text.split(";") if n.strip()]
        return names
    
    # Try to find name boundaries: after a lowercase letter followed by uppercase
    # e.g., "John SmithJane Doe" -> split after "Smith" (lowercase 'h') before "Jane" (uppercase 'J')
    parts = re.split(r'(?<=[a-záéíóúàèìòùäëïöüñç])(?=[A-ZÁÉÍÓÚÀÈÌÒÙÄËÏÖÜÑÇ][a-záéíóúàèìòùäëïöüñç])', text)
    
    for p in parts:
        p = p.strip()
        if p and len(p) > 2:
            names.append(p)
    
    # If too many names or none, try alternative split
    if len(names) <= 1:
        # Try splitting on known name patterns
        name_pattern = r'((?:[A-Z][a-záéíóúàèìòùäëïöüñç]+\s+){1,3}[A-Z][a-záéíóúàèìòùäëïöüñç]+(?:-\s*[A-Z][a-z]+)?)'
        found = re.findall(name_pattern, text)
        if found:
            return [f.strip() for f in found if f.strip()]
        return [text]
    
    return names

def build_eea_v2():
    # Read TSV
    tsv_path = os.path.join(DATA_DIR, "eea2026", "all_sessions.tsv")
    with open(tsv_path) as f:
        lines = f.readlines()
    
    sessions = []
    participants_dict = {}
    session_counter = 0
    
    for line in lines:
        parsed = parse_tsv_line(line.strip())
        if not parsed:
            continue
        
        session_counter += 1
        
        # Split presenters
        presenter_names = split_presenters(parsed["presenters_raw"])
        
        session_id = f"EEA-S{session_counter:04d}"
        
        sessions.append({
            "session_id": session_id,
            "session_title": parsed["title"],
            "session_type": parsed["type"],
            "track": parsed["field"],
            "day": parsed["day"],
            "date": parsed["date"],
            "time": parsed["time"],
            "room": parsed["room"],
            "papers": []
        })
        
        # Track participants
        for name in presenter_names:
            if name.lower() not in participants_dict:
                participants_dict[name.lower()] = {
                    "name": name,
                    "institution": "",
                    "is_presenter": True,
                    "papers": []
                }
            title = parsed["title"]
            if title not in participants_dict[name.lower()]["papers"]:
                participants_dict[name.lower()]["papers"].append(title)
    
    # Conference metadata
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
    
    data = {
        "conference": conf,
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://www.eea-esem-congresses.org/",
            "program_url": "https://www.eea-esem-congresses.org/full-programme",
            "script_name": "eea_tsv_parser.py",
            "program_available": True,
            "program_type": "web",
            "notes": f"Extracted {len(sessions)} sessions from the EEA-ESEM full programme view (5 paginated pages). Paper-level details not available (session-level only).",
            "errors": []
        },
        "sessions": sessions,
        "papers": [],
        "participants": list(participants_dict.values()),
        "total_sessions": len(sessions),
        "total_papers": 0,
        "total_participants": len(participants_dict)
    }
    
    return data

if __name__ == "__main__":
    data = build_eea_v2()
    path = os.path.join(DATA_DIR, "eea2026", "data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ EEA: {data['total_sessions']} sessions, {data['total_participants']} participants")
    print(f"   Written to {path}")
