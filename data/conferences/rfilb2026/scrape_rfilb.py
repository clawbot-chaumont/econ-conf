#!/usr/bin/env python3
"""RFILB scraper - complete."""
import json, re
from collections import OrderedDict

with open("/tmp/rfilb_all_content.json") as f:
    tabs = json.load(f)

poster_text = tabs["Poster session"]
march30 = tabs["MARCH 30, 2026"]
march31 = tabs["MARCH 31, 2026"]

def clean(t):
    t = t.replace('\xa0', ' ').replace('\u2013', '-').replace('\u2014', '-')
    t = t.replace('\u201c', '"').replace('\u201d', '"')
    t = t.replace('\u2018', "'").replace('\u2019', "'")
    return t

def get_blocks(text):
    text = clean(text)
    positions = [(m.start(), m.group()) for m in re.finditer(r'\nParallel [Ss]ession (\d+)', text)]
    blocks = []
    for i, (pos, name) in enumerate(positions):
        end = positions[i+1][0] if i+1 < len(positions) else len(text)
        blocks.append((name.strip(), text[pos:end].strip()))
    return blocks

def parse_block(name, block):
    lines = block.split('\n')
    first = lines[0].strip()
    m = re.match(r'Parallel [Ss]ession (\d+)\s*[-:]\s*(.*)', first)
    if not m:
        return None
    num = m.group(1)
    rest = m.group(2).strip()
    parts = re.split(r'\s+[-]\s+', rest)
    title = " - ".join(parts[:-1]).strip() if len(parts) >= 2 and len(parts[-1]) < 40 else rest
    
    cm = re.search(r'Chair(?:man|woman)?\s*:\s*([^,\n]+?)(?:,|\s*[-]\s*)\s*([^\n]+?)(?:\.\s|\n)', block)
    chair = f"{cm.group(1).strip()}, {cm.group(2).strip()}" if cm else ""
    
    papers = []
    for m in re.finditer(r'[-]\s*"([^"]+)"[ \t]*\n\s*([^\n]+?)(?=\n\s*[-]\s*"|\n\s*(?:Discussant|$))', block):
        title = m.group(1).strip()
        auth = re.split(r'\s*Discussant\s*:\s*', m.group(2), flags=re.I)[0].strip()
        
        authors = []
        for seg in re.split(r',\s+and\s+', auth):
            parts = re.split(r',\s+', seg.strip().rstrip('.'), maxsplit=1)
            name = parts[0].strip().strip(',').strip()
            if name:
                authors.append(name)
        
        if title and authors:
            papers.append({"title": title, "authors": authors, "presenter": authors[0]})
    
    return {"session_title": f"Session {num}: {title}", "chair": chair, "papers": papers} if papers else None

def parse_posters(text):
    text = clean(text)
    papers = []
    for m in re.finditer(r'"([^"]+)"\s*\n\s*([^\n]+?)(?=\n\s*[-]\s*"|\n\s*(?:Tuesday|Monday|\n\n))', text):
        title = m.group(1).strip()
        auth = m.group(2).strip().strip(',').strip().rstrip('.').strip()
        authors = []
        for seg in re.split(r',\s+and\s+', auth):
            name = seg.split(',')[0].strip()
            if name:
                authors.append(name)
        if title:
            papers.append({"title": title, "authors": authors, "presenter": authors[0] if authors else ""})
    return papers

all_sessions = []
for text, date, label in [(march30, "2026-03-30", "March 30"), (march31, "2026-03-31", "March 31")]:
    for name, block in get_blocks(text):
        s = parse_block(name, block)
        if s:
            s["date"] = date
            all_sessions.append(s)

posters = parse_posters(poster_text)

participants = OrderedDict()
for s in all_sessions:
    for p in s["papers"]:
        for n in p["authors"]:
            n = n.strip()
            if n and n not in participants:
                participants[n] = {"name": n, "institution": "", "is_presenter": n == p["presenter"], "papers": [p["title"]]}
            elif n in participants and p["title"] not in participants[n]["papers"]:
                participants[n]["papers"].append(p["title"])

for p in posters:
    for n in p["authors"]:
        n = n.strip()
        if n and n not in participants:
            participants[n] = {"name": n, "institution": "", "is_presenter": n == p.get("presenter",""), "papers": [p["title"]]}
        elif n in participants and p["title"] not in participants[n]["papers"]:
            participants[n]["papers"].append(p["title"])

sessions_out = []
for s in all_sessions:
    vs = {"session_title": s["session_title"]}
    if s.get("chair"): vs["chair"] = s["chair"]
    if s.get("date"): vs["date"] = s["date"]
    vs["papers"] = [{"title": p["title"], "authors": p["authors"], "presenter": p.get("presenter", p["authors"][0] if p["authors"] else "")} for p in s["papers"]]
    sessions_out.append(vs)

# Add plenaries
sessions_out.insert(0, {"session_title": "Welcome Address", "chair": "Marie BRIERE, Institut Louis Bachelier", "date": "2026-03-30", "papers": []})
sessions_out.insert(0, {"session_title": "Plenary Session I - Measuring Geopolitical Risk using AI", "chair": "Dorothée ROUZET, French Treasury", "date": "2026-03-30", "papers": [{"title": "Measuring Geopolitical Risk using Artificial Intelligence", "authors": ["Matteo IACOVIELLO"], "presenter": "Matteo IACOVIELLO"}]})
for name, inst in [("Matteo IACOVIELLO", "Federal Reserve Board"), ("Monica BILLIO", "Ca' Foscari University of Venice"), ("Markus LEIPPOLD", "University of Zurich")]:
    if name not in participants:
        participants[name] = {"name": name, "institution": inst, "is_presenter": True, "papers": []}
sessions_out.append({"session_title": "Plenary Session II - Climate Risk and US Systemic Stability", "chair": "Laurent CLERC, Banque de France", "date": "2026-03-31", "papers": [{"title": "How Climate Risk Shapes US Systemic Stability Through Syndicated Lendings", "authors": ["Monica BILLIO"], "presenter": "Monica BILLIO"}]})
sessions_out.append({"session_title": "Plenary Session III - AI and the Integrity of Knowledge", "chair": "Marie-Anne BARBAT LAYANI, AMF", "date": "2026-03-31", "papers": [{"title": "AI and the Integrity of Knowledge", "authors": ["Markus LEIPPOLD"], "presenter": "Markus LEIPPOLD"}]})
sessions_out.append({"session_title": "Poster Session", "date": "2026-03-30", "papers": [{"title": p["title"], "authors": p["authors"], "presenter": p.get("presenter", p["authors"][0] if p["authors"] else "")} for p in posters]})

output = {
    "conference": {
        "name": "Financial Risks International Forum (RFILB)", "short_name": "RFILB",
        "year": 2026, "start_date": "2026-03-30", "end_date": "2026-03-31",
        "location": "Paris, France",
    },
    "scrape_metadata": {
        "scraped_at": "2026-06-13T17:00:00", "source_url": "https://www.risks-forum.org/PROGRAM",
        "program_available": True, "program_type": "web", "errors": [],
    },
    "sessions": sessions_out,
    "participants": sorted(participants.values(), key=lambda x: x["name"]),
}

print(f"Saved: {len(sessions_out)} sessions, {sum(len(s['papers']) for s in sessions_out)} papers, {len(output['participants'])} participants")

with open("/root/economics-conferences/rfilb2026/data.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
