#!/usr/bin/env python3
"""
Scrape the WFA 2026 conference program from the Western Finance Portal.
Generates a v2 schema data.json file.
"""

import urllib.request
import urllib.error
import re
import json
import time
from datetime import datetime, timezone

BASE_URL = "https://westernfinance-portal.org"
CONFERENCE_URL = f"{BASE_URL}/conference"
SESSION_URL = f"{BASE_URL}/conferencesession?Session={{}}"

# Non-academic session IDs to skip
SKIP_SESSIONS = {"event", "welcome", "awards", "sponsors", "pdf", "map", "help", "homepage"}

def fetch_url(url, retries=3):
    """Fetch a URL with retries."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; HermesScraper/1.0)"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

def get_session_ids(html):
    """Extract all academic session IDs from the main conference page."""
    session_ids = set()
    for m in re.finditer(r'conferencesession\?Session=([a-zA-Z0-9]+)', html):
        sid = m.group(1)
        # Skip non-academic sessions
        skip = False
        for prefix in SKIP_SESSIONS:
            if sid.startswith(prefix):
                skip = True
                break
        if not skip:
            session_ids.add(sid)
    return sorted(session_ids)

def scrape_sessions(session_ids):
    """Scrape all session pages and extract structured data."""
    sessions = []
    all_participants = {}  # name -> {institution, paper_titles, roles}
    all_papers = {}  # paper_id -> paper info

    for i, sid in enumerate(session_ids):
        print(f"  [{i+1}/{len(session_ids)}] Fetching session {sid}...")
        url = SESSION_URL.format(sid)
        try:
            html = fetch_url(url)
        except Exception as e:
            print(f"    ERROR fetching {sid}: {e}")
            continue

        session_data, session_papers = parse_session_page(html, sid)
        if session_data:
            sessions.append(session_data)
            # Collect all papers from this session
            for pid, p in session_papers.items():
                if pid not in all_papers:
                    all_papers[pid] = p
            # Collect participants from this session
            collect_participants(session_data, all_participants, all_papers)

        time.sleep(0.5)  # Rate limiting

    return sessions, all_participants, all_papers

def parse_session_page(html, sid):
    """Parse a single session page."""
    session = {}

    # --- Session ID ---
    session["session_id"] = sid

    # --- Title ---
    m = re.search(r'<a href="conferencesession\?Session=' + re.escape(sid) + r'"[^>]*>\s*([^<]+?)\s*</a>', html)
    if m:
        session["session_title"] = m.group(1).strip()
    else:
        m = re.search(r'style="color:#fdc657">\s*([^<]+?)\s*</a>', html)
        if m:
            session["session_title"] = m.group(1).strip()
        else:
            print(f"    WARNING: Could not find title for session {sid}")
            return None

    # --- Date ---
    m = re.search(r'<i class="fa fa-calendar"></i>\s*([^<]+)', html)
    if m:
        date_str = m.group(1).strip()
        # Convert "Monday, June 22, 2026" to "2026-06-22"
        month_map = {
            "January": "01", "February": "02", "March": "03", "April": "04",
            "May": "05", "June": "06", "July": "07", "August": "08",
            "September": "09", "October": "10", "November": "11", "December": "12"
        }
        m2 = re.match(r'\w+,\s*(\w+)\s+(\d+),\s*(\d{4})', date_str)
        if m2:
            month_name = m2.group(1)
            day = m2.group(2).zfill(2)
            year = m2.group(3)
            month = month_map.get(month_name, "06")
            session["date"] = f"{year}-{month}-{day}"
        else:
            session["date"] = "2026-06-22"
    else:
        session["date"] = "2026-06-22"

    # --- Time ---
    m = re.search(r'<i class="fa fa-clock-o"></i>\s*([^<]+)', html)
    if m:
        session["time"] = m.group(1).strip()
    else:
        session["time"] = ""

    # --- Location ---
    m = re.search(r'<i class="fa fa-map-pin[^>]*></i>\s*([^<]+)', html)
    if m:
        session["location"] = m.group(1).strip()
    else:
        session["location"] = ""

    # --- Chair ---
    m = re.search(r'Chair:\s*<strong>([^,]+),\s*<em>([^<]+)</em></strong>', html)
    if m:
        session["chair"] = {
            "name": clean_name(m.group(1).strip()),
            "institution": clean_institution(m.group(2).strip())
        }
    else:
        session["chair"] = {"name": "", "institution": ""}

    # --- Papers ---
    # Split the HTML into paper blocks
    # Each paper block starts with <h5><a href="viewpaper?n=..."> and ends before the next <br><hr><h5> or end
    paper_blocks = re.split(r'<br><hr><h5>', html)

    papers = []
    for block in paper_blocks:
        # Skip non-paper blocks (before first paper)
        if '<a href="https://westernfinance-portal.org/viewpaper?n=' not in block and '<a href="viewpaper?n=' not in block:
            continue

        # Extract paper ID and title
        m = re.search(r'<a href="https://westernfinance-portal.org/viewpaper\?n=(\d+)"[^>]*>([^<]+?)<i class="fa fa-angle-right">', block)
        if not m:
            m = re.search(r'<a href="viewpaper\?n=(\d+)"[^>]*>([^<]+?)<i class="fa fa-angle-right">', block)
        if not m:
            m = re.search(r'<a href="[^"]*viewpaper\?n=(\d+)"[^>]*>([^<]+?)<i class="fa fa-angle-right">', block)
        
        if not m:
            continue

        paper_id = m.group(1)
        paper_title = m.group(2).strip()

        # Extract authors
        authors = []
        author_matches = re.findall(r'<h6><strong>([^,]+),\s*<em>([^<]+)</em></strong></h6>', block)
        for name, inst in author_matches:
            if not name.startswith("Discussant"):
                authors.append({
                    "name": clean_name(name.strip()),
                    "institution": clean_institution(inst.strip())
                })

        # Extract discussants
        discussants = []
        disc_matches = re.findall(r'Discussant:\s*<strong>([^,]+),\s*<em>([^<]+)</em></strong>', block)
        for name, inst in disc_matches:
            discussants.append({
                "name": clean_name(name.strip()),
                "institution": clean_institution(inst.strip())
            })

        paper_entry = {
            "title": paper_title,
            "authors": [a["name"] for a in authors],
            "author_details": authors,
            "discussants": discussants,
            "paper_id": paper_id
        }
        papers.append(paper_entry)

    session["papers"] = papers
    
    # Build papers dict for this session
    session_papers = {}
    for p in papers:
        session_papers[p.get("paper_id", "")] = p
    
    return session, session_papers

def clean_name(name):
    """Clean participant names - remove trailing affiliation numbers."""
    # Remove trailing digits, commas, spaces (affiliation markers like ", 1", " 1,2", etc.)
    name = re.sub(r'[\d,\s]+$', '', name).strip()
    # Also remove leading/trailing special chars
    name = name.strip()
    return name

def clean_institution(inst):
    """Clean institution names."""
    inst = inst.strip()
    # Remove common suffixes
    inst = re.sub(r',?\s*(and|&)\s+(CEPR|NBER|CEPR|IZA|BIS|ECB|FEDS)\s*$', '', inst).strip()
    # Remove trailing " and X" patterns
    inst = re.sub(r',?\s+and\s+\w+\s*$', '', inst).strip()
    # Fix known abbreviations
    abbrev_map = {
        "UCLA": "University of California-Los Angeles",
        "UC Los Angeles": "University of California-Los Angeles",
        "UC Berkeley": "University of California-Berkeley",
        "UC San Diego": "University of California-San Diego",
        "UC Davis": "University of California-Davis",
        "UC Irvine": "University of California-Irvine",
        "UC Santa Barbara": "University of California-Santa Barbara",
        "MIT": "Massachusetts Institute of Technology",
        "CEMFI": "CEMFI",
        "NYU": "New York University",
        "LSE": "London School of Economics",
        "U Chicago": "University of Chicago",
        "U Penn": "University of Pennsylvania",
        "USC": "University of Southern California",
        "UBC": "University of British Columbia",
    }
    return inst

def collect_participants(session_data, all_participants, all_papers):
    """Collect unique participants from a session."""
    # Chair
    chair = session_data.get("chair", {})
    if chair.get("name"):
        name = chair["name"]
        if name not in all_participants:
            all_participants[name] = {
                "institution": chair.get("institution", ""),
                "paper_titles": [],
                "roles": []
            }
        all_participants[name]["roles"].append("chair")

    # Authors and discussants from papers
    for paper in session_data.get("papers", []):
        paper_title = paper.get("title", "")
        for author in paper.get("author_details", []):
            name = author.get("name", "")
            if name:
                if name not in all_participants:
                    all_participants[name] = {
                        "institution": author.get("institution", ""),
                        "paper_titles": [],
                        "roles": []
                    }
                if paper_title not in all_participants[name]["paper_titles"]:
                    all_participants[name]["paper_titles"].append(paper_title)
                if "author" not in all_participants[name]["roles"]:
                    all_participants[name]["roles"].append("author")

        for discussant in paper.get("discussants", []):
            name = discussant.get("name", "")
            if name:
                if name not in all_participants:
                    all_participants[name] = {
                        "institution": discussant.get("institution", ""),
                        "paper_titles": [],
                        "roles": []
                    }
                if paper_title not in all_participants[name]["paper_titles"]:
                    all_participants[name]["paper_titles"].append(paper_title)
                if "discussant" not in all_participants[name]["roles"]:
                    all_participants[name]["roles"].append("discussant")


def build_data_json(sessions, participants_dict, papers_dict):
    """Build the v2 schema data.json structure."""
    # Sort sessions by date then time then title
    def session_sort_key(s):
        return (s.get("date", ""), s.get("time", ""), s.get("session_title", ""))

    sessions_sorted = sorted(sessions, key=session_sort_key)

    # Build participants array
    participants_list = []
    for name, info in sorted(participants_dict.items()):
        participants_list.append({
            "name": name,
            "institution": info.get("institution", ""),
            "paper_titles": info.get("paper_titles", []),
            "roles": info.get("roles", [])
        })

    # Build top-level papers array (unique)
    unique_papers = []
    seen_titles = set()
    for pid in sorted(papers_dict.keys()):
        p = papers_dict[pid]
        title = p.get("title", "")
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_papers.append({
                "title": title,
                "paper_id": p.get("paper_id", ""),
                "authors": p.get("authors", []),
                "author_details": p.get("author_details", []),
                "discussants": p.get("discussants", [])
            })

    # Build sessions (final clean form)
    clean_sessions = []
    for s in sessions_sorted:
        clean_papers = []
        for p in s.get("papers", []):
            clean_papers.append({
                "title": p["title"],
                "authors": p["authors"],
                "discussants": [
                    {"name": d["name"], "institution": d["institution"]}
                    for d in p.get("discussants", [])
                ]
            })
        clean_sessions.append({
            "session_title": s["session_title"],
            "session_id": s.get("session_id", ""),
            "date": s.get("date", ""),
            "time": s.get("time", ""),
            "location": s.get("location", ""),
            "chair": s.get("chair", {"name": "", "institution": ""}),
            "papers": clean_papers
        })

    data = {
        "conference": {
            "name": "Western Finance Association Annual Meeting",
            "short_name": "WFA 2026",
            "year": 2026,
            "start_date": "2026-06-22",
            "end_date": "2026-06-24",
            "location": "Denver, CO, Hyatt Regency Denver",
            "website": "https://westernfinance.org/conference-2026/"
        },
        "scrape_metadata": {
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source_url": "https://westernfinance-portal.org/conference",
            "program_available": True,
            "num_sessions": len(clean_sessions),
            "num_papers": len(unique_papers),
            "num_participants": len(participants_list)
        },
        "sessions": clean_sessions,
        "papers": unique_papers,
        "participants": participants_list
    }

    return data


def main():
    print("=" * 60)
    print("WFA 2026 Conference Program Scraper")
    print("=" * 60)

    # Step 1: Fetch main page to get session IDs
    print("\n[Step 1] Fetching main conference page...")
    try:
        html = fetch_url(CONFERENCE_URL)
    except Exception as e:
        print(f"  ERROR fetching main page: {e}")
        return

    session_ids = get_session_ids(html)
    print(f"  Found {len(session_ids)} academic sessions:")
    for sid in session_ids:
        print(f"    - {sid}")

    # Step 2: Scrape each session
    print(f"\n[Step 2] Scraping {len(session_ids)} sessions...")
    sessions, all_participants, all_papers = scrape_sessions(session_ids)
    print(f"  Successfully scraped {len(sessions)} sessions")
    print(f"  Found {len(all_participants)} unique participants")
    print(f"  Found {len(all_papers)} unique papers")

    # Step 3: Build data.json
    print("\n[Step 3] Building data.json...")
    data = build_data_json(sessions, all_participants, all_papers)

    output_path = "/root/economics-conferences/wfa2026/data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Written to {output_path}")
    print(f"  File size: {len(json.dumps(data, indent=2))} bytes")
    print(f"  Sessions: {len(data['sessions'])}")
    print(f"  Papers: {len(data['papers'])}")
    print(f"  Participants: {len(data['participants'])}")

    print("\nDone!")


if __name__ == "__main__":
    main()
