#!/usr/bin/env python3
"""
Enhanced 3CMFI scraper — parses the detailed program correctly.
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

blocks = re.split(r'<tr', html)

# Find where "Detailed List of Sessions" starts
detail_start = None
for i, b in enumerate(blocks):
    if 'Detailed List of Sessions' in b:
        detail_start = i
        break

if not detail_start:
    print("Could not find detailed list")
    sys.exit(1)

print(f"Detailed list starts at block {detail_start}")

# Parse sessions and their papers
sessions = []
current_session = None
participants_dict = {}

for i in range(detail_start, len(blocks)):
    b = blocks[i]
    text = re.sub(r'<[^>]+>', ' ', b)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Session header (bgcolor="lightgrey")
    if 'bgcolor="lightgrey"' in b:
        if current_session:
            sessions.append(current_session)
        
        # Extract session info
        # Pattern: "Session N: TITLE Date time Location"
        m = re.search(r'Session\s+(\d+)\s*:\s*(.+?)(?:March\s+\d+)', text)
        if m:
            sess_num = m.group(1)
            sess_title = m.group(2).strip()
        else:
            sess_num = str(len(sessions) + 1)
            sess_title = text[:100]
        
        current_session = {
            "session_id": f"3CMFI-S{sess_num}",
            "session_title": sess_title,
            "session_type": "Contributed",
            "papers": []
        }
        continue
    
    # Paper entry: title line with "Abstract"
    if current_session and 'Abstract' in text and len(text) > 30 and text[0].isupper():
        # This block contains the paper title
        # Extract title (before "Abstract")
        title_m = re.search(r'^([^A]*(?:Abstract)?)', text)
        title = title_m.group(1).strip() if title_m else text[:100]
        # Clean up title
        title = re.sub(r'\s+Abstract.*$', '', title).strip()
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Look ahead for author info in next blocks
        authors = []
        presenter = ""
        
        # Check next block for "By" line
        if i + 1 < len(blocks):
            next_text = re.sub(r'<[^>]+>', ' ', blocks[i+1])
            next_text = re.sub(r'\s+', ' ', next_text).strip()
            by_m = re.search(r'By\s+(.+)', next_text)
            if by_m:
                authors_str = by_m.group(1).strip()
                # Split by semicolon
                authors = [a.strip() for a in re.split(r';|,', authors_str) if a.strip() and len(a.strip()) > 3]
        
        # Check block after that for "Presented by" line  
        if i + 2 < len(blocks):
            pres_text = re.sub(r'<[^>]+>', ' ', blocks[i+2])
            pres_text = re.sub(r'\s+', ' ', pres_text).strip()
            pres_m = re.search(r'Presented by:\s*([^,]+)', pres_text)
            if pres_m:
                presenter = pres_m.group(1).strip()
                inst_m = re.search(r'Presented by:\s*[^,]+,\s*(.+?)$', pres_text)
                if inst_m:
                    presenter_inst = inst_m.group(1).strip()
        
        # Build paper entry
        paper = {
            "title": title,
            "authors": authors,
            "presenter": presenter,
        }
        current_session["papers"].append(paper)
        
        # Track participant
        if presenter:
            key = presenter.lower()
            if key not in participants_dict:
                participants_dict[key] = {"name": presenter, "institution": presenter_inst if 'presenter_inst' in dir() else "", "papers": [], "is_presenter": True}
            if title not in participants_dict[key]["papers"]:
                participants_dict[key]["papers"].append(title)
        
        for a in authors:
            key = a.lower()
            if key not in participants_dict:
                participants_dict[key] = {"name": a, "institution": "", "papers": [], "is_presenter": False}

if current_session:
    sessions.append(current_session)

print(f"\nParsed: {len(sessions)} sessions, {sum(len(s['papers']) for s in sessions)} papers, {len(participants_dict)} participants")

# Show first 3 sessions
for s in sessions[:3]:
    print(f"\n  Session: {s['session_title']}")
    for p in s['papers'][:2]:
        print(f"    - {p['title'][:60]}")
        print(f"      By: {', '.join(p['authors'])}")
        print(f"      Presenter: {p['presenter']}")

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
            "keynote_speakers": ["Sabine Mauderer (Bundesbank)", "Hilary Allen (American University)", "Philip Lane (ECB)", "Stefano Giglio (Yale)", "Robert Engle (NYU)"],
            "ecb_presence": "Philip R. Lane (keynote), Alexander Popov (discussant), Caroline Willeke (chair/organizer), Margherita Giuzio (co-organizer), Tina Emambakhsh, Marien Ferdinandusse, Miles Parker (ECB Special Session)",
            "theme": "Emerging Macroeconomic, Financial, and Environmental Policy Challenges"
        }
    },
    "scrape_metadata": {
        "scraped_at": NOW_ISO,
        "source_url": "https://editorialexpress.com/conference/3CMFI/program/3CMFI.html",
        "program_available": True,
        "program_type": "web",
        "notes": f"Full detailed program scraped: {len(sessions)} sessions, {sum(len(s['papers']) for s in sessions)} papers, {len(participants_dict)} participants."
    },
    "sessions": sessions,
    "papers": [],
    "participants": list(participants_dict.values()),
    "total_sessions": len(sessions),
    "total_papers": sum(len(s['papers']) for s in sessions),
    "total_participants": len(participants_dict)
}

# Save
os.makedirs(DATA_DIR, exist_ok=True)
path = os.path.join(DATA_DIR, "data.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"\n✅ Saved: {path} ({os.path.getsize(path)/1024:.1f} KB)")

# Upload to Drive
try:
    from google.oauth2.credentials import Credentials as OAuthCreds
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    
    token_path = os.path.expanduser("~/.hermes/google_token.json")
    with open(token_path) as f:
        td = json.load(f)
    oauth_creds = OAuthCreds.from_authorized_user_info(td)
    drive = build('drive', 'v3', credentials=oauth_creds)
    
    FOLDER_ID = "1IQY4Ip1X2ZzsxLn14okVcvMuV0CQGQOQ"
    drive_name = "3CMFI_2026_3rd_International_Conference_on_Climate_Macro_Finance_Interface.json"
    
    results = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and name='{drive_name}' and trashed=false",
        fields="files(id, name)"
    ).execute()
    for f in results.get('files', []):
        drive.files().delete(fileId=f['id']).execute()
    
    media = MediaFileUpload(path, mimetype='application/json', resumable=True)
    f = drive.files().create(
        body={'name': drive_name, 'parents': [FOLDER_ID]},
        media_body=media,
        fields='id, name, size'
    ).execute()
    print(f"☁️ Uploaded: {drive_name} ({int(f['size'])//1024} KB)")
except Exception as e:
    print(f"⚠ Upload failed: {e}")
