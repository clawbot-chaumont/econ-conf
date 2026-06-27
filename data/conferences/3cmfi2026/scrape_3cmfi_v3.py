#!/usr/bin/env python3
"""
3CMFI v3 — parses papers correctly from the single <td> block structure.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.request import urlopen, Request

DATA_DIR = os.path.expanduser("~/economics-conferences/3cmfi2026")
HEADERS = {"User-Agent": "Mozilla/5.0"}
NOW_ISO = datetime.now(timezone.utc).isoformat()

url = "https://editorialexpress.com/conference/3CMFI/program/3CMFI.html"
req = Request(url, headers=HEADERS)
html = urlopen(req, timeout=30).read().decode("utf-8", errors="replace")

# Find "Detailed List of Sessions"
detail_idx = html.find("Detailed List of Sessions")
detail = html[detail_idx:] if detail_idx >= 0 else html

# Split into session blocks: each session header has bgcolor="lightgrey"
parts = re.split(r'(<tr[^>]*bgcolor="lightgrey"[^>]*>)', detail)

sessions = []
participants_dict = {}
current_session = None

for i, part in enumerate(parts):
    # Check if this is a session header
    if 'bgcolor="lightgrey"' in part:
        # Save previous session
        if current_session and current_session.get("papers"):
            sessions.append(current_session)
        
        # Extract session info
        text = re.sub(r'<[^>]+>', ' ', part).strip()
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Get next block which has the session details
        if i + 1 < len(parts):
            next_text = re.sub(r'<[^>]+>', ' ', parts[i+1])
            next_text = re.sub(r'\s+', ' ', next_text).strip()
            combined = f"{text} {next_text}"
        else:
            combined = text
        
        # Extract session number and title
        m = re.search(r'Session\s*(\d+)\s*:\s*(.+?)(?:March|\d{2}:\d{2})', combined)
        sess_num = m.group(1) if m else str(len(sessions) + 1)
        sess_title = m.group(2).strip() if m else combined[:80]
        # Clean up title
        sess_title = re.sub(r'\s+', ' ', sess_title).strip()
        
        current_session = {
            "session_id": f"3CMFI-S{sess_num.zfill(2)}",
            "session_title": sess_title,
            "session_type": "Contributed" if "KEYNOTE" not in sess_title.upper() and "WELCOME" not in sess_title.upper() and "REGISTRATION" not in sess_title.upper() and "LUNCH" not in sess_title.upper() and "COFFEE" not in sess_title.upper() else "Other",
            "papers": []
        }
    
    # Paper entries: look for "By " followed by authors and "Presented by"
    if current_session and not 'bgcolor="lightgrey"' in part:
        text = re.sub(r'<[^>]+>', '\n', part)
        lines = text.split('\n')
        
        # Find blocks containing paper info
        paper_blocks = re.split(r'(?=\w[\w\s]{10,}?Abstract)', part)
        
        # Alternative: look for title followed by "By" and "Presented by"
        paper_matches = re.findall(
            r'<td[^>]*>\s*([^<]{10,}?)\s*(?:<details>.*?</details>)?\s*&nbsp;\s*&nbsp;\s*&nbsp;By\s+([^<]+?)\s*<br>\s*&nbsp;\s*&nbsp;\s*&nbsp;Presented by:\s*([^<]+)',
            part, re.DOTALL
        )
        
        for pm in paper_matches:
            title = re.sub(r'\s+', ' ', pm[0]).strip()
            # Remove trailing "Abstract" if present
            title = re.sub(r'\s*Abstract\s*$', '', title).strip()
            authors_str = pm[1].strip()
            presenter_str = pm[2].strip()
            
            # Split authors
            authors = [a.strip() for a in re.split(r';', authors_str) if a.strip()]
            
            # Split presenter from institution
            pres_parts = re.split(r'\s*,\s*', presenter_str, maxsplit=1)
            presenter = pres_parts[0].strip()
            presenter_inst = pres_parts[1].strip() if len(pres_parts) > 1 else ""
            
            paper = {
                "title": title,
                "authors": authors,
                "presenter": presenter
            }
            current_session["papers"].append(paper)
            
            # Track participant
            if presenter:
                key = presenter.lower()
                if key not in participants_dict:
                    participants_dict[key] = {"name": presenter, "institution": presenter_inst, "papers": [], "is_presenter": True}
                participants_dict[key]["papers"].append(title)
            
            for a in authors:
                key = a.lower()
                if key not in participants_dict:
                    participants_dict[key] = {"name": a, "institution": "", "papers": [], "is_presenter": False}

# Don't forget last session
if current_session and current_session.get("papers"):
    sessions.append(current_session)

# Only keep sessions that have papers
sessions_with_papers = [s for s in sessions if s["papers"]]
empty_sessions = [s for s in sessions if not s["papers"]]

print(f"Total session blocks: {len(sessions)}")
print(f"Sessions with papers: {len(sessions_with_papers)}")
print(f"Empty sessions: {len(empty_sessions)}")
print(f"Total papers found: {sum(len(s['papers']) for s in sessions)}")
print(f"Unique participants: {len(participants_dict)}")

if empty_sessions:
    print(f"\nEmpty session titles:")
    for s in empty_sessions[:10]:
        print(f"  - {s['session_title'][:60]}")

# Build v2 data
data = {
    "conference": {
        "name": "Third International Conference on the Climate-Macro-Finance Interface",
        "short_name": "3CMFI 2026",
        "year": 2026,
        "edition": "3rd",
        "start_date": "2026-03-23",
        "end_date": "2026-03-24",
        "location": "Frankfurt, Germany",
        "venue": "SAFE, Goethe University Frankfurt",
        "website": "https://safe-frankfurt.de/news-media/events/event-view/3rd-international-conference-on-the-climate-macro-finance-interface-3cmfi.html",
        "organizer": "Leibniz SAFE, RCEA-Europe, Deutsche Bundesbank, ECB",
        "extras": {
            "keynote_speakers": [
                "Sabine Mauderer (Bundesbank) - Balancing Growth, Stability, and Sustainability",
                "Hilary Allen (American University) - The Political Economy of Silicon Valley",
                "Philip Lane (ECB) - AI and the European Economy",
                "Stefano Giglio (Yale) - Climate Transition Risks and the Energy Sector",
                "Robert Engle (NYU) - The Impact of Climate Risk On Financial Markets"
            ],
            "ecb_presence": "Philip R. Lane (keynote), Alexander Popov (discussant), Caroline Willeke (chair/organizer), Tina Emambakhsh, Marien Ferdinandusse, Miles Parker (ECB Special Session), Margherita Giuzio (organizer)"
        }
    },
    "scrape_metadata": {
        "scraped_at": NOW_ISO,
        "source_url": "https://editorialexpress.com/conference/3CMFI/program/3CMFI.html",
        "program_available": True,
        "program_type": "web",
        "notes": f"Full program: {len(sessions_with_papers)} sessions with papers, {sum(len(s['papers']) for s in sessions_with_papers)} papers, {len(participants_dict)} participants. {len(empty_sessions)} non-paper sessions (registration, coffee, lunch, keynotes)."
    },
    "sessions": sessions_with_papers,
    "papers": [],
    "participants": list(participants_dict.values()),
    "total_sessions": len(sessions_with_papers),
    "total_papers": sum(len(s['papers']) for s in sessions_with_papers),
    "total_participants": len(participants_dict)
}

# Save
os.makedirs(DATA_DIR, exist_ok=True)
path = os.path.join(DATA_DIR, "data.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"\n✅ Saved: {path} ({os.path.getsize(path)/1024:.1f} KB)")
