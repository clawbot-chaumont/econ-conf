#!/usr/bin/env python3
"""
EEA-ESEM 2026 Full Scraper v3
3-level: Programme pages → Session pages → Speaker pages (institutions)
"""

import json, re, os, time, sys
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

BASE_URL = "https://eea-esem-congresses.org"
DATA_DIR = os.path.expanduser("~/economics-conferences/eea2026")
NOW_ISO = datetime.now(timezone.utc).isoformat()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

def fetch(url, retries=3):
    """Fetch a URL with retries."""
    for attempt in range(retries):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  ⚠ Failed after {retries} retries: {url} — {e}", file=sys.stderr)
                return ""

def parse_programme_page(html):
    """Extract sessions and speakers from a programme page HTML."""
    sessions = []
    
    # Extract each table row
    rows = re.findall(r'<tr class="EEA[^"]*">(.*?)</tr>', html, re.DOTALL)
    if not rows:
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
        # Filter out header row  
        rows = [r for r in rows if 'href="/sessions/' in r]
    
    for row in rows:
        # Session title and link
        title_m = re.search(r'<a href="(/sessions/[^"]+)"[^>]*>([^<]+)</a>', row)
        if not title_m:
            continue
        session_slug = title_m.group(1)
        title = title_m.group(2).strip()
        
        # Type
        type_m = re.search(r'<td headers="view-field-type-table-column"[^>]*>([^<]+)</td>', row)
        stype = type_m.group(1).strip() if type_m else ""
        
        # Field
        field_m = re.search(r'<td headers="view-field-specialist-a-table-column"[^>]*>([^<]*)</td>', row)
        field = field_m.group(1).strip() if field_m else ""
        
        # Date
        date_m = re.search(r'<td headers="view-field-start-date-table-column"[^>]*>([^<]+)</td>', row)
        date_str = date_m.group(1).strip() if date_m else ""
        
        # Time
        time_m = re.search(r'<td headers="view-field-start-date-1-table-column"[^>]*>([^<]+)</td>', row)
        time_str = time_m.group(1).strip() if time_m else ""
        
        # Duration
        dur_m = re.search(r'<td headers="view-field-duration-table-column"[^>]*>([^<]+)</td>', row)
        duration = dur_m.group(1).strip() if dur_m else ""
        
        # Room
        room_m = re.search(r'<td headers="view-field-physical-room-table-column"[^>]*>([^<]*)</td>', row)
        room = room_m.group(1).strip() if room_m else ""
        
        # Speakers
        speakers = []
        for sp_m in re.finditer(r'<a href="(/speakers/[^"]+)"[^>]*>([^<]+)</a>', row):
            speakers.append({
                "slug": sp_m.group(1),
                "name": sp_m.group(2).strip()
            })
        
        # Parse date to ISO
        date_iso = ""
        if date_str and "/" in date_str:
            try:
                d, m = date_str.split("/")
                date_iso = f"2026-{int(m):02d}-{int(d):02d}"
            except:
                pass
        
        sessions.append({
            "title": title,
            "session_slug": session_slug,
            "type": stype,
            "field": field,
            "date": date_iso,
            "date_raw": date_str,
            "time": time_str,
            "duration": duration,
            "room": room,
            "speakers": speakers
        })
    
    return sessions

def parse_speaker_page(html, name):
    """Extract institution from a speaker page."""
    # Look for <strong> inside <div class="speaker-content">
    m = re.search(r'<div class="speaker-content">\s*<h3>[^<]*</h3>\s*<strong>([^<]*)</strong>', html)
    if m:
        inst = m.group(1).strip()
        # Decode HTML entities
        inst = inst.replace('&#039;', "'").replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return inst if inst else ""  # empty <strong></strong> means no institution listed
    return ""

def build_data():
    """Full pipeline: scrape programme, then speaker pages."""
    
    # Step 1: Scrape all programme pages
    print("=" * 60)
    print("📋 Step 1: Scraping programme pages (pages 0-4)")
    print("=" * 60)
    
    all_sessions = []
    speaker_map = {}  # slug -> {name, institution, papers[]}
    
    for page_num in range(5):
        url = f"{BASE_URL}/full-programme?page={page_num}"
        print(f"  Page {page_num}/4...", end=" ")
        html = fetch(url)
        if not html:
            print("❌ FAILED")
            continue
        
        sessions = parse_programme_page(html)
        print(f"✅ {len(sessions)} sessions found")
        
        for s in sessions:
            # Add speakers to map
            for sp in s["speakers"]:
                slug = sp["slug"]
                if slug not in speaker_map:
                    speaker_map[slug] = {
                        "name": sp["name"],
                        "institution": "",
                        "papers": []
                    }
                # Add this session title as a paper
                if s["title"] not in speaker_map[slug]["papers"]:
                    speaker_map[slug]["papers"].append(s["title"])
            
            all_sessions.append(s)
    
    print(f"\n📊 Total: {len(all_sessions)} sessions, {len(speaker_map)} unique speakers")
    
    # Step 2: Scrape each speaker page for institution
    print("\n" + "=" * 60)
    print("🏛️ Step 2: Scraping speaker pages for institutions")
    print("=" * 60)
    
    speaker_slugs = list(speaker_map.keys())
    total = len(speaker_slugs)
    
    # Use ThreadPoolExecutor for speed (10 concurrent)
    def fetch_speaker(slug):
        url = f"{BASE_URL}{slug}"
        html = fetch(url)
        if not html:
            return slug, ""
        inst = parse_speaker_page(html, speaker_map[slug]["name"])
        return slug, inst
    
    completed = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_speaker, slug): slug for slug in speaker_slugs}
        for future in as_completed(futures):
            slug, inst = future.result()
            speaker_map[slug]["institution"] = inst
            completed += 1
            if completed % 50 == 0 or completed == total:
                print(f"  {completed}/{total} speakers scraped ({completed/total*100:.0f}%)")
    
    # Stats
    with_inst = sum(1 for s in speaker_map.values() if s["institution"])
    print(f"\n✅ {with_inst}/{total} speakers have institution data")
    
    # Step 3: Build v2 data structure
    print("\n" + "=" * 60)
    print("📦 Step 3: Building v2 data.json")
    print("=" * 60)
    
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
    
    # Build sessions array (v2 format) with papers instead of speakers
    sessions_v2 = []
    for i, s in enumerate(all_sessions):
        session_title = s["title"] if s["title"] and s["title"].strip() else f"Session {i+1}"
        # Build papers array from speakers linked to participant data
        papers = []
        for sp in s["speakers"]:
            papers.append({
                "title": sp["name"],
                "authors": [sp["name"]],
                "presenter": sp["name"]
            })
        session = {
            "session_id": f"EEA-S{len(sessions_v2)+1:04d}",
            "session_title": session_title,
            "session_slug": s["session_slug"],
            "session_type": s["type"],
            "track": s["field"],
            "date": s["date"],
            "time": s["time"],
            "duration": s["duration"],
            "room": s["room"],
            "papers": papers
        }
        sessions_v2.append(session)
    
    # Build participants array
    participants = []
    for slug, data in speaker_map.items():
        participants.append({
            "name": data["name"],
            "speaker_slug": slug,
            "institution": data["institution"],
            "papers": data["papers"]
        })
    
    # Sort participants by name
    participants.sort(key=lambda p: p["name"].lower())
    
    data = {
        "conference": conf,
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://www.eea-esem-congresses.org/",
            "program_url": "https://www.eea-esem-congresses.org/full-programme",
            "script_name": "eea_scraper_v3.py",
            "program_available": True,
            "program_type": "web",
            "notes": f"Full 3-level scrape: {len(sessions_v2)} sessions, {len(participants)} participants with institutions from speaker pages.",
            "errors": []
        },
        "sessions": sessions_v2,
        "papers": [],  # Papers are at participant level
        "participants": participants,
        "total_sessions": len(sessions_v2),
        "total_papers": 0,
        "total_participants": len(participants)
    }
    
    return data

def save_data(data):
    """Save data.json and return the path."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "data.json")
    
    # Validate v2 schema
    assert "conference" in data, "Missing conference"
    assert "sessions" in data, "Missing sessions"
    assert "participants" in data, "Missing participants"
    assert "scrape_metadata" in data, "Missing scrape_metadata"
    
    for p in data["participants"]:
        assert "name" in p, f"Participant missing name: {p}"
        assert "institution" in p, f"Participant missing institution: {p['name']}"
        assert "papers" in p, f"Participant missing papers: {p['name']}"
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to {path}")
    print(f"   Sessions: {data['total_sessions']}")
    print(f"   Participants: {data['total_participants']}")
    print(f"   Size: {os.path.getsize(path)/1024:.1f} KB")
    return path

if __name__ == "__main__":
    start = time.time()
    data = build_data()
    path = save_data(data)
    
    # Print ECB people
    print("\n" + "=" * 60)
    print("🏛️ ECB-affiliated participants")
    print("=" * 60)
    ecb_keywords = ["ECB", "European Central Bank", "BCE", "european central bank"]
    ecb_people = []
    for p in data["participants"]:
        inst = p["institution"]
        if inst and any(kw.lower() in inst.lower() for kw in ecb_keywords):
            ecb_people.append(p)
            print(f"  ✅ {p['name']:30s} — {inst}")
    
    if not ecb_people:
        print("  (none found via speaker pages)")
    
    elapsed = time.time() - start
    print(f"\n⏱️  Total time: {elapsed:.0f}s ({elapsed/60:.1f} min)")
