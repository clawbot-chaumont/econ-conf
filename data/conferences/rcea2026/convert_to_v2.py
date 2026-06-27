#!/usr/bin/env python3
"""Convert RCEA data.json to v2 schema."""
import json, os
from datetime import datetime

path = os.path.expanduser("~/economics-conferences/rcea2026/data.json")
with open(path) as f:
    d = json.load(f)

# 1. Fix conference
if 'title' in d['conference']:
    d['conference']['name'] = d['conference'].pop('title')
d['conference'].setdefault('short_name', 'RCEA 2026')
d['conference'].setdefault('year', 2026)

# Build extras from leftover fields
extra_fields = [k for k in d['conference'] if k not in ('name','short_name','year','start_date','end_date','location')]
extras = {}
for k in extra_fields:
    extras[k] = d['conference'].pop(k)
if extras:
    d['conference']['extras'] = extras

# 2. Fix sessions
new_sessions = []
session_titles_seen = set()
for s in d.get('sessions', []):
    title = s.get('title', s.get('session_title', '')).strip()
    
    # Skip non-paper sessions
    skip_keywords = ['REGISTRATION', 'COFFEE', 'LUNCH', 'KEYNOTE', 'BREAK', 'WELCOME']
    if any(kw in title.upper() for kw in skip_keywords):
        continue
    
    # Skip sessions with no papers
    papers = s.get('papers', [])
    if not papers:
        continue
    
    new_s = {
        'session_title': title,
        'session_type': 'Contributed',
        'date': s.get('date', '2026-05-25'),
        'time': f"{s.get('time_start','')} - {s.get('time_end','')}",
        'room': s.get('location', s.get('room', '')),
        'papers': [],
    }
    
    for p in papers:
        # Extract title
        p_title = p.get('title', '')
        if not p_title:
            continue
        
        # Extract presenters/authors
        presenters = p.get('presenters', [])
        authors = []
        for pr in presenters:
            name = pr.get('name', '').strip()
            if name:
                authors.append(name)
                if name not in [a for a in authors]:
                    pass
        
        new_p = {
            'title': p_title,
            'authors': authors,
            'presenter': authors[0] if authors else '',
        }
        new_s['papers'].append(new_p)
    
    if new_s['papers']:
        new_sessions.append(new_s)

# 3. Fix participants
new_participants = []
seen = set()
for p in d.get('participants', []):
    name = p.get('name', '').strip()
    if not name or name.lower() in seen:
        continue
    seen.add(name.lower())
    
    # Find papers for this participant
    participant_papers = []
    for s in new_sessions:
        for paper in s['papers']:
            if name.lower() in [a.lower() for a in paper['authors']]:
                participant_papers.append(paper['title'])
    
    new_participants.append({
        'name': name,
        'institution': p.get('institution', ''),
        'is_presenter': True,
        'papers': participant_papers,
    })

# 4. Add scrape_metadata
d['scrape_metadata'] = {
    'scraped_at': '2026-06-13T11:48:20Z',
    'source_url': 'http://editorialexpress.com/conference/202_RCEA_ICEEF/program/202_RCEA_ICEEF.html',
    'program_available': len(new_sessions) > 0,
    'program_type': 'web',
    'notes': f'{len(new_sessions)} paper sessions, {sum(len(s["papers"]) for s in new_sessions)} papers, {len(new_participants)} participants',
}
d['sessions'] = new_sessions
d['participants'] = new_participants

with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"✅ RCEA converted: {len(new_sessions)} sessions, {sum(len(s['papers']) for s in new_sessions)} papers, {len(new_participants)} participants")
