#!/usr/bin/env python3
"""AFA 2026 program scraper - v2 - fixed for multiple sessions per time block."""
import json, os, re
from datetime import datetime
from bs4 import BeautifulSoup

DATA_DIR = "/root/economics-conferences"

with open(f"{DATA_DIR}/afa2026/full_program_2026.html") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
participants = []
seen_names = set()

def add_participant(name, institution, role="Author/Presenter", paper_title=""):
    if not name or not name.strip():
        return
    name = name.strip()
    key = name.lower()
    if key in seen_names:
        return
    seen_names.add(key)
    participants.append({
        "name": name,
        "institution": institution.strip() if institution else "",
        "role": role,
        "is_presenter": True,
        "papers": [paper_title] if paper_title else [],
        "paper_titles": [],
    })

# Find all time block headers
time_headers = soup.find_all('div', class_='col-12', style=re.compile(r'background:#6b2f1d'))
print(f"Found {len(time_headers)} time blocks")

month_map = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
             'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

sessions = []

for th in time_headers:
    h4 = th.find('h4')
    if not h4:
        continue
    time_text = h4.get_text(strip=True)
    
    m = re.search(r'(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday),\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+)\s*[|\xa0]+\s*([\d:]+\s*[ap]m\s*-\s*[\d:]+\s*[ap]m)', time_text, re.IGNORECASE)
    if not m:
        print(f"  Could not parse: {time_text}")
        continue
    
    block_day = m.group(1)
    block_month = m.group(2)
    block_day_num = m.group(3)
    block_time = m.group(4)
    iso_date = f"2026-{month_map.get(block_month, '01')}-{block_day_num.zfill(2)}"
    
    # Get the parent row
    parent_row = th.find_parent('div', class_='row')
    if not parent_row:
        continue
    
    # Now iterate through next sibling rows until the next time block
    current_row = parent_row.find_next_sibling('div', class_='row')
    
    while current_row:
        # Check if this row has a time header (next block)
        if current_row.find('div', class_='col-12', style=re.compile(r'background:#6b2f1d')):
            break
        
        # Check if this row has a session header (h5 with "Session:")
        h5 = current_row.find('h5')
        if h5 and 'Session:' in h5.get_text():
            title_text = h5.get_text(strip=True)
            title = re.sub(r'^Session:\s*', '', title_text).strip()
            
            # Get all col-lg-12 divs in this row
            cols = current_row.find_all('div', class_='col-lg-12')
            
            chair = ""
            papers = []
            
            for col in cols:
                # Check if this is the session header col
                col_h5 = col.find('h5')
                if col_h5:
                    # Get chair from h6
                    h6_chair = col.find('h6')
                    if h6_chair:
                        chair_text = h6_chair.get_text(strip=True)
                        if 'Session Chair:' in chair_text:
                            chair = chair_text.replace('Session Chair:', '').strip()
                    continue
                
                # Check if this is a paper (has h6 with link)
                h6 = col.find('h6')
                if h6 and h6.find('a'):
                    paper_link = h6.find('a')
                    paper_title = paper_link.get_text(strip=True)
                    
                    # Extract authors from <strong> tags in <p>
                    authors = []
                    discussant = ""
                    
                    p_tags = col.find_all('p')
                    for p in p_tags:
                        strongs = p.find_all('strong')
                        for s in strongs:
                            name = s.get_text(strip=True)
                            if not name:
                                continue
                            # Get affiliation from text after strong
                            p_full = p.get_text()
                            s_idx = p_full.find(name)
                            affiliation = ""
                            if s_idx >= 0:
                                after = p_full[s_idx + len(name):].strip()
                                after = after.lstrip(',;:\t ')
                                after = after.replace('\t', ' ').strip()
                                # Get text until br/newline
                                aff = after.split('\n')[0].strip(' ,;()\t')
                                if aff:
                                    affiliation = aff
                            
                            if name and name not in authors:
                                authors.append({"name": name, "affiliation": affiliation})
                                add_participant(name, affiliation, "Author/Presenter", paper_title)
                        
                        # Check discussant
                        p_text = p.get_text()
                        if 'Discussant:' in p_text:
                            d = p_text.split('Discussant:')[1].strip()
                            d_name = re.match(r'([^(]+)', d)
                            if d_name:
                                discussant = d_name.group(1).strip()
                    
                    paper = {
                        "title": paper_title,
                        "authors": [a["name"] for a in authors],
                        "presenter": authors[0]["name"] if authors else "",
                    }
                    if discussant:
                        paper["discussant"] = discussant
                    
                    papers.append(paper)
            
            if papers:
                session = {
                    "session_title": title,
                    "session_type": "Contributed",
                    "day": block_day,
                    "date": iso_date,
                    "time": block_time,
                    "chair": chair,
                    "papers": papers
                }
                sessions.append(session)
        
        current_row = current_row.find_next_sibling('div', class_='row')

print(f"Extracted {len(sessions)} sessions")
total_papers = sum(len(s.get("papers", [])) for s in sessions)
print(f"Total papers: {total_papers}")
print(f"Total participants: {len(participants)}")

# Build and save
data = {
    "conference": {
        "name": "American Finance Association Annual Meeting",
        "short_name": "AFA 2026",
        "year": 2026,
        "edition": "2026 Annual Meeting",
        "start_date": "2026-01-03",
        "end_date": "2026-01-05",
        "location": "Philadelphia, PA, USA",
        "venue": "Loews Philadelphia Hotel & Philadelphia Marriott Downtown",
        "city": "Philadelphia",
        "country": "USA",
        "website": "https://www.afajof.org/annual-meeting/",
        "program_url": "https://afajof.org/management/full-program2026.html",
        "organizer": "American Finance Association",
        "description": "The annual meeting of the American Finance Association.",
        "extras": {
            "program_chair": "Wei Jiang",
            "presidential_address": "Ulrike Malmendier",
        }
    },
    "scrape_metadata": {
        "scraped_at": datetime.now().isoformat(),
        "source_url": "https://afajof.org/management/full-program2026.html",
        "program_url": "https://afajof.org/management/full-program2026.html",
        "script_name": "scrape_afa_program.py",
        "program_available": True,
        "program_type": "web",
        "notes": "Scraped from AFA full program HTML page.",
        "errors": [],
    },
    "sessions": sessions,
    "participants": participants,
    "total_sessions": len(sessions),
    "total_papers": total_papers,
    "total_participants": len(participants),
}

output_path = f"{DATA_DIR}/afa2026/data.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"\nWritten: {output_path} ({os.path.getsize(output_path)} bytes)")

if sessions:
    totals_by_day = {}
    for s in sessions:
        d = s.get('date', '')
        totals_by_day[d] = totals_by_day.get(d, 0) + 1
    print(f"Sessions by date:")
    for d, c in sorted(totals_by_day.items()):
        print(f"  {d}: {c} sessions")
PYEOF
