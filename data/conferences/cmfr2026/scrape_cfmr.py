#!/usr/bin/env python3
"""Final CFMR scraper - proper institution mapping."""
import requests
import json
import re
from bs4 import BeautifulSoup

BASE = "https://www.conftool.org/cfmr2026"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_day(date_str):
    url = f"{BASE}/index.php?page=browseSessions&form_date={date_str}&mode=list&presentations=show"
    resp = requests.get(url, timeout=15, headers=HEADERS)
    soup = BeautifulSoup(resp.content, "html.parser")
    sessions = []
    
    for a in soup.find_all("a", class_="font10"):
        b = a.find("b")
        if not b:
            continue
        session_title = b.get_text(strip=True)
        if not session_title:
            continue
        
        parent_td = a.find_parent("td")
        time_text = ""
        chair = ""
        if parent_td:
            txt = parent_td.get_text()
            tm = re.search(r"(\d+:\d+[ap]m\s*-\s*\d+:\d+[ap]m)", txt)
            if tm:
                time_text = tm.group(1)
            cm = re.search(r"(?:Session\s+)?Chair[:\s]+([A-Za-z\s,.\-']+)", txt)
            if cm:
                chair = cm.group(1).strip().rstrip(",").strip()[:80]
        
        papers = []
        current = a.find_next("div", class_="paper")
        while current:
            if current.find("p", class_="paper_abstract") and not current.find("p", class_="paper_title"):
                current = current.find_next("div", class_="paper")
                continue
            
            prev_a = current.find_previous("a", class_="font10")
            if prev_a:
                nb = prev_a.find("b")
                if nb and nb.get_text(strip=True) != session_title:
                    break
            
            title_el = current.find("p", class_="paper_title")
            if title_el:
                title = title_el.get_text(strip=True)
                author_el = current.find("p", class_="paper_author")
                org_el = current.find("p", class_="paper_organisation")
                
                # Build institution map
                inst_map = {}
                default_inst = ""
                if org_el:
                    for sup in org_el.find_all("sup"):
                        num = sup.get_text(strip=True)
                        following = ""
                        for sib in sup.next_siblings:
                            if sib.name == "sup":
                                break
                            if isinstance(sib, str):
                                following += sib
                        following = following.strip().rstrip(";").strip()
                        inst_map[num] = following
                    if not inst_map:
                        default_inst = org_el.get_text(strip=True)
                
                # Parse authors
                authors_list = []
                presenter = ""
                for child in author_el.children if author_el else []:
                    if isinstance(child, str):
                        text = child.strip().strip(",").strip()
                        if text:
                            authors_list.append({"name": text, "inst": default_inst})
                    elif child.name == "u":
                        name = child.get_text(strip=True).rstrip(",").strip()
                        if name:
                            authors_list.append({"name": name, "inst": default_inst})
                            presenter = name
                    elif child.name == "sup":
                        num = child.get_text(strip=True)
                        if authors_list and num in inst_map:
                            authors_list[-1]["inst"] = inst_map[num]
                
                if not presenter and authors_list:
                    presenter = authors_list[0]["name"]
                
                papers.append({
                    "title": title,
                    "authors_data": authors_list,
                    "presenter": presenter,
                })
            
            nxt = current.find_next("div", class_="paper")
            if nxt and nxt.find("p", class_="paper_abstract") and not nxt.find("p", class_="paper_title"):
                nxt = nxt.find_next("div", class_="paper")
            current = nxt
        
        sessions.append({
            "session_title": session_title,
            "chair": chair,
            "time": time_text,
            "date": date_str,
            "papers": papers,
        })
    return sessions

# Scrape both days
all_sessions = []
for ds in ["2026-05-07", "2026-05-08"]:
    all_sessions.extend(scrape_day(ds))

# Build output
from collections import OrderedDict
participant_data = OrderedDict()
v2_sessions = []

for s in all_sessions:
    vpapers = []
    for p in s.get("papers", []):
        authors = [a["name"] for a in p.get("authors_data", [])]
        presenter = p.get("presenter", authors[0] if authors else "")
        vpapers.append({"title": p["title"], "authors": authors, "presenter": presenter})
        
        for ad in p.get("authors_data", []):
            name = ad["name"]
            inst = ad.get("inst", "")
            if name not in participant_data:
                participant_data[name] = {"name": name, "institution": inst, "is_presenter": name == presenter, "papers": [p["title"]]}
            else:
                if p["title"] not in participant_data[name]["papers"]:
                    participant_data[name]["papers"].append(p["title"])
                if name == presenter:
                    participant_data[name]["is_presenter"] = True
    
    vs = {"session_title": s["session_title"]}
    if s.get("chair"): vs["chair"] = s["chair"]
    if s.get("date"): vs["date"] = s["date"]
    vs["papers"] = vpapers
    v2_sessions.append(vs)

output = {
    "conference": {
        "name": "13th Annual Conference on Financial Market Regulation (CFMR)",
        "short_name": "CMFR", "year": 2026,
        "start_date": "2026-05-07", "end_date": "2026-05-08",
        "location": "Washington DC, USA",
    },
    "scrape_metadata": {
        "scraped_at": "2026-06-13T17:00:00",
        "source_url": "https://www.conftool.org/cfmr2026/sessions.php",
        "program_available": True, "program_type": "web", "errors": [],
    },
    "sessions": v2_sessions,
    "participants": sorted(participant_data.values(), key=lambda x: x["name"]),
}

print(f"Sessions: {len(output['sessions'])}")
for s in output["sessions"]:
    print(f"  {s['session_title']} [{s.get('chair','?')}]: {len(s['papers'])} papers")
print(f"Participants: {len(output['participants'])}")
hi = sum(1 for p in output["participants"] if p.get("institution","").strip())
print(f"With institution: {hi}")

# Show mapping
print("\n=== Institution check ===")
for s in output["sessions"]:
    for p in s["papers"]:
        if len(p["authors"]) > 1:
            for a in p["authors"]:
                pd = participant_data.get(a, {})
                print(f"  {a:30s} -> {pd.get('institution','?')}")

with open("/root/economics-conferences/cmfr2026/data.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print("\nSaved!")
