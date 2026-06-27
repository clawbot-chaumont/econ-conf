#!/usr/bin/env python3
"""Fix 3CMFI data.json to v2 schema."""
import json, os, re

DATA_DIR = os.path.expanduser("~/economics-conferences/3cmfi2026")
path = os.path.join(DATA_DIR, "data.json")

with open(path) as f:
    d = json.load(f)

# Fix conference field: rename 'title' to 'name'
if 'title' in d.get('conference', {}):
    d['conference']['name'] = d['conference'].pop('title')

# Fix sessions: rename 'title' to 'session_title'
seen_participants = {}
new_sessions = []
for s in d.get('sessions', []):
    new_s = {
        'session_title': s.get('title', s.get('session_title', s.get('session_number', ''))),
        'session_type': s.get('session_type', 'Contributed'),
        'date': s.get('date', ''),
        'time': s.get('date_time', s.get('time', '')),
        'room': s.get('location', s.get('room', '')),
        'papers': [],
    }
    for p in s.get('papers', []):
        # Fix authors: split "Author; Institution" format
        authors_raw = p.get('authors', [])
        fixed_authors = []
        for a in authors_raw:
            if isinstance(a, str) and ';' in a:
                parts = [x.strip() for x in a.split(';') if x.strip()]
                # First part is name, rest could be institutions
                if parts:
                    fixed_authors.append(parts[0])
                    # If there's more parts, they're likely institution — skip for authors
            else:
                fixed_authors.append(a)
        
        # Fix presenter: split "Name, Institution"
        presenter_str = p.get('presenter', '')
        presenter_name = presenter_str
        presenter_inst = ''
        if ',' in presenter_str:
            parts = [x.strip() for x in presenter_str.split(',', 1)]
            presenter_name = parts[0]
            presenter_inst = parts[1] if len(parts) > 1 else ''
        
        paper = {
            'title': p.get('title', ''),
            'authors': fixed_authors,
            'presenter': presenter_name,
        }
        new_s['papers'].append(paper)
        
        # Track participants
        # Add all authors
        for author in fixed_authors:
            key = author.lower().strip()
            if key not in seen_participants:
                seen_participants[key] = {
                    'name': author.strip(),
                    'institution': '',
                    'is_presenter': author.strip().lower() == presenter_name.lower(),
                    'papers': []
                }
            if paper['title'] not in seen_participants[key]['papers']:
                seen_participants[key]['papers'].append(paper['title'])
        
        # Mark presenter
        if presenter_name:
            pk = presenter_name.lower().strip()
            if pk in seen_participants:
                seen_participants[pk]['is_presenter'] = True
                if presenter_inst and not seen_participants[pk]['institution']:
                    seen_participants[pk]['institution'] = presenter_inst
    
    new_s['papers'] = [p for p in new_s['papers'] if p['title']]
    if new_s['papers']:
        new_sessions.append(new_s)

# Clean up extras
extras = {
    'keynote_speakers': [
        'Sabine Mauderer (Bundesbank) - Balancing Growth, Stability, and Sustainability',
        'Hilary Allen (American University) - The Political Economy of Silicon Valley',
        'Philip Lane (ECB) - AI and the European Economy',
        'Stefano Giglio (Yale) - Climate Transition Risks and the Energy Sector',
        'Robert Engle (NYU) - The Impact of Climate Risk On Financial Markets'
    ]
}

d['conference'] = {
    'name': 'Third International Conference on the Climate-Macro-Finance Interface',
    'short_name': '3CMFI 2026',
    'year': 2026,
    'start_date': '2026-03-23',
    'end_date': '2026-03-24',
    'location': 'Frankfurt, Germany',
    'extras': extras,
}
d['sessions'] = new_sessions
d['participants'] = list(seen_participants.values())
d.setdefault('scrape_metadata', {})
d['scrape_metadata']['program_available'] = True
d['scrape_metadata']['program_type'] = 'web'
d['scrape_metadata']['notes'] = f'{len(new_sessions)} paper sessions, {sum(len(s["papers"]) for s in new_sessions)} papers, {len(seen_participants)} participants'

with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"✅ Fixed: {len(new_sessions)} sessions, {sum(len(s['papers']) for s in new_sessions)} papers, {len(seen_participants)} participants")
