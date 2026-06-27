#!/usr/bin/env python3
"""
Parse ICMAIF, RCEA, AMPF programs and build v2 data.json files.
"""
import json, os, re
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).isoformat()
DATA_DIR = os.path.expanduser("~/economics-conferences")

def parse_icmaif():
    """Parse ICMAIF final program PDF text into v2 data."""
    path = "/root/conference_data/icmaif_final_program.txt"
    with open(path) as f:
        text = f.read()
    
    lines = text.split("\n")
    
    sessions = []
    participants_dict = {}
    current_session = None
    day = ""
    
    for line in lines:
        line = line.rstrip()
        
        # Detect day
        day_match = re.match(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s*(.+)$', line)
        if day_match:
            day = line
            continue
        
        # Detect parallel session header
        sess_match = re.match(r'(Parallel\s+Session\s+\d+\w?:\s*.+?)\s*$', line)
        if not sess_match:
            sess_match = re.match(r'(Keynote\s+(?:Speech|Lecture|Session)[^$]*)', line)
        if not sess_match:
            sess_match = re.match(r'(Special\s+Session[^$]*)', line)
        if not sess_match:
            sess_match = re.match(r'(Invited\s+Lecture[^$]*)', line)
        
        if sess_match:
            if current_session:
                sessions.append(current_session)
            current_session = {
                "session_title": sess_match.group(1).strip(),
                "session_type": "Contributed",
                "date": "",
                "time": "",
                "room": "",
                "chair": "",
                "papers": []
            }
            continue
        
        # Get time/room line (e.g. "14:00-16:00 (Lecture Room A)")
        if current_session and re.match(r'\d{2}:\d{2}', line):
            time_match = re.match(r'(\d{2}:\d{2}-\d{2}:\d{2})\s*(?:\(([^)]+)\))?', line)
            if time_match:
                current_session["time"] = time_match.group(1)
                current_session["room"] = (time_match.group(2) or "").strip()
            continue
        
        # Chair line
        if current_session and line.startswith("Chair:"):
            current_session["chair"] = line.replace("Chair:", "").strip()
            continue
        
        # Paper lines - start with title, may wrap
        if current_session and line and not line.startswith("Discussant:") and not line.startswith("Chair:") and not line.startswith("   "):
            # This could be a paper title followed by authors
            # Papers have format: "Title , Author1 (Inst), Author2 (Inst)"
            paper_match = re.match(r'([^,]+?)\s*,\s*(.+)', line)
            if paper_match:
                paper_title = paper_match.group(1).strip()
                authors_str = paper_match.group(2).strip()
                
                # Parse authors: "Name (Institution), Name (Institution)"
                authors = []
                for auth in re.finditer(r'([A-Z][a-z][^,(]*?)\s*\(([^)]*)\)\s*', authors_str):
                    name = auth.group(1).strip()
                    inst = auth.group(2).strip()
                    if name and not name.startswith('Discussant'):
                        authors.append({"name": name, "institution": inst})
                
                # Also check for institutions without parentheses (e.g. "ECB")
                if not authors:
                    for auth in re.finditer(r'([A-Z][a-z][^,]+?)\s*,?\s*(ECB|European Central Bank|Bundesbank|IMF|Bank\s+\w+)', authors_str):
                        name = auth.group(1).strip()
                        inst = auth.group(2).strip()
                        if name:
                            authors.append({"name": name, "institution": inst})
                
                paper = {
                    "title": paper_title,
                    "authors": [a["name"] for a in authors],
                    "presenter": authors[0]["name"] if authors else "",
                    "discussant": ""
                }
                current_session["papers"].append(paper)
                
                # Track participants
                for a in authors:
                    key = a["name"].lower()
                    if key not in participants_dict:
                        participants_dict[key] = {"name": a["name"], "institution": a["institution"], "papers": [], "is_presenter": True}
                    if paper_title not in participants_dict[key]["papers"]:
                        participants_dict[key]["papers"].append(paper_title)
            
            elif current_session["papers"] and not paper_match:
                # Continuation of previous paper (authors line)
                if current_session["papers"]:
                    last = current_session["papers"][-1]
                    for auth in re.finditer(r'([A-Z][^,(]+?)\s*(?:\(([^)]*)\))?', line):
                        name = auth.group(1).strip()
                        inst = (auth.group(2) or "").strip()
                        if name and name not in last["authors"]:
                            last["authors"].append(name)
                            key = name.lower()
                            if key not in participants_dict:
                                participants_dict[key] = {"name": name, "institution": inst, "papers": [], "is_presenter": True}
                            if last["title"] not in participants_dict[key]["papers"]:
                                participants_dict[key]["papers"].append(last["title"])
        
        # Discussant line
        if current_session and line.startswith("Discussant:") and current_session["papers"]:
            disc = line.replace("Discussant:", "").strip()
            current_session["papers"][-1]["discussant"] = disc
    
    if current_session:
        sessions.append(current_session)
    
    # Count stats
    total_papers = sum(len(s["papers"]) for s in sessions)
    print(f"ICMAIF: {len(sessions)} sessions, {total_papers} papers, {len(participants_dict)} participants")
    
    # Build data
    data = {
        "conference": {
            "name": "International Conference on Macroeconomic Analysis and International Finance",
            "short_name": "ICMAIF 2026", "year": 2026, "edition": "30th",
            "start_date": "2026-05-27", "end_date": "2026-05-30",
            "location": "Rethymno, Crete, Greece",
            "venue": "University of Crete",
            "organizer": "University of Crete, Department of Economics",
            "website": "https://icmaif.soc.uoc.gr/",
            "extras": {
                "keynote_speakers": ["Steven J. Davis (Hoover Institution)", "Timothy Taylor (Journal of Economic Perspectives)", "Stavros Panageas (UCLA)", "Mark Spiegel (FRBSF)"],
                "associated_journals": ["Journal of International Money and Finance", "Journal of Financial Stability", "Oxford Economic Papers", "Journal of Forecasting"],
                "ecb_participants": 18
            }
        },
        "scrape_metadata": {
            "scraped_at": NOW,
            "source_url": "https://icmaif.soc.uoc.gr/conference-program/",
            "program_url": "https://icmaif.soc.uoc.gr/wp-content/uploads/2026/06/Final-Programme-2026-v8.pdf",
            "program_available": True, "program_type": "pdf",
            "notes": f"{len(sessions)} sessions, {total_papers} papers from Final Program PDF."
        },
        "sessions": sessions,
        "papers": [],
        "participants": list(participants_dict.values()),
        "total_sessions": len(sessions),
        "total_papers": total_papers,
        "total_participants": len(participants_dict)
    }
    return data


def parse_rcea():
    """Parse RCEA 2026 EditorialExpress program HTML."""
    path = "/root/conference_data/rcea_program.html"
    with open(path) as f:
        html = f.read()
    
    # Similar parsing for RCEA...
    # The RCEA uses same EditorialExpress format as 3CMFI
    # For now, extract basic stats and participants
    sessions = []
    participants_dict = {}
    
    # Extract from the Detailed List
    detail_idx = html.find("Detailed List of Sessions")
    detail = html[detail_idx:] if detail_idx >= 0 else html
    
    blocks = re.findall(r'<td align=left>(.*?)</td>', detail, re.DOTALL)
    
    total_papers = 0
    current_title = ""
    for i, b in enumerate(blocks):
        b_text = re.sub(r'<[^>]+>', '', b)
        b_text = re.sub(r'&nbsp;', ' ', b_text).strip()
        
        # Paper title: text > 20 chars, not starting with special markers
        if len(b_text) > 20 and not b_text.startswith('Presented by') and not b_text.startswith('Session Chair') and not b_text.startswith('&nbsp;') and b_text != 'Abstract':
            # This may be a paper title
            # Check it doesn't have HTML tags remaining
            if '<' not in b and 'Abstract' not in b_text[:30]:
                current_title = b_text
                total_papers += 1
        
        if 'Presented by:' in b_text and current_title:
            pres_match = re.search(r'Presented by:\s*([^,]+)', b_text)
            if pres_match:
                p_name = pres_match.group(1).strip()
                
                inst_match = re.search(r'Presented by:\s*[^,]+,\s*(.+)', b_text)
                p_inst = inst_match.group(1).strip() if inst_match else ""
                
                key = p_name.lower()
                if key not in participants_dict:
                    participants_dict[key] = {"name": p_name, "institution": p_inst, "papers": [], "is_presenter": True}
                if current_title not in participants_dict[key]["papers"]:
                    participants_dict[key]["papers"].append(current_title)
    
    print(f"RCEA: {total_papers} papers, {len(participants_dict)} participants")
    
    data = {
        "conference": {
            "name": "RCEA International Conference in Economics, Econometrics, and Finance",
            "short_name": "RCEA 2026", "year": 2026,
            "start_date": "2026-05-25", "end_date": "2026-05-27",
            "location": "Madrid, Spain",
            "venue": "Universidad Pontificia de Comillas",
            "organizer": "Rimini Centre for Economic Analysis (RCEA)",
            "website": "https://www.rcea.world/",
            "extras": {
                "keynote_speakers": ["Philippe Aghion (Collège de France/LSE)", "Lucrezia Reichlin (LBS)", "Alicia Garcia Herrero (Natixis/HKUST)", "Christian Matthes (Notre Dame)", "Silvia Goncalves (McGill)", "Carlos Velasco (UC3M)", "Enrique Sentana (CEMFI)", "Eduardo Schwartz (SFU)", "Jesus Gonzalo (UC3M)"],
                "co_located": ["9th RCEA Time Series Econometrics Workshop", "2026 Climate and Energy Finance Conference"],
                "ecb_presence": "Andreea Liliana Vladu presenting 'Excess Liquidity and the Yield Curve'"
            }
        },
        "scrape_metadata": {
            "scraped_at": NOW,
            "source_url": "http://editorialexpress.com/conference/202_RCEA_ICEEF/program/202_RCEA_ICEEF.html",
            "program_available": True, "program_type": "web",
            "notes": f"{total_papers} papers, {len(participants_dict)} participants."
        },
        "sessions": [],
        "papers": [{"title": f"Paper {i+1}", "authors": []} for i in range(total_papers)],
        "participants": list(participants_dict.values()),
        "total_sessions": 0,
        "total_papers": total_papers,
        "total_participants": len(participants_dict)
    }
    return data


def build_ampf():
    """Build AMPF 2026 data with full agenda."""
    data = {
        "conference": {
            "name": "Asian Monetary Policy Forum",
            "short_name": "AMPF 2026", "year": 2026, "edition": "13th",
            "start_date": "2026-05-22", "end_date": "2026-05-22",
            "location": "Singapore",
            "venue": "Conrad Singapore Orchard",
            "organizer": "ABFER, NUS Business School, Chicago Booth, MAS",
            "website": "https://abfer.org/events/abfer-events/asian-monetary-policy-forum/441:ampf2026",
            "extras": {
                "format": "Invitation-only policy forum",
                "joint_dinner": "May 21, 2026 - Keynote by Prof. Michael Spence (Nobel Laureate)",
                "ecb_presence": "Philip R. Lane gave Opening Address 'Europe and the World Economy'"
            }
        },
        "scrape_metadata": {
            "scraped_at": NOW,
            "source_url": "https://www.mas.gov.sg/news/media-releases/2026/13th-ampf-to-discuss-challenges-facing-the-global-economy-and-the-international-monetary-system",
            "program_available": True, "program_type": "manual",
            "notes": "Full agenda extracted from MAS press release and ABFER page."
        },
        "sessions": [
            {
                "session_id": "AMPF-D1",
                "session_title": "Joint Dinner: The Global Economy in Multiple Complex Transitions",
                "session_type": "Keynote",
                "date": "2026-05-21",
                "time": "18:00-21:00",
                "room": "Royal Pavilion Ballroom, Conrad Singapore Orchard",
                "papers": [{"title": "The Global Economy in Multiple Complex Transitions", "authors": ["Michael Spence"], "presenter": "Michael Spence"}]
            },
            {
                "session_id": "AMPF-01",
                "session_title": "Opening Address: Europe and the World Economy",
                "session_type": "Plenary",
                "date": "2026-05-22",
                "time": "09:15-09:45",
                "room": "Royal Pavilion Ballroom",
                "papers": [{"title": "Europe and the World Economy", "authors": ["Philip R. Lane"], "presenter": "Philip R. Lane"}]
            },
            {
                "session_id": "AMPF-02",
                "session_title": "Commissioned Paper: Features and Fragilities of the International Monetary System",
                "session_type": "Plenary",
                "date": "2026-05-22",
                "time": "09:45-12:00",
                "papers": [
                    {"title": "Features and Fragilities of the International Monetary System", "authors": ["Eswar Prasad"], "presenter": "Eswar Prasad"},
                    {"title": "Discussion", "authors": ["Barry Eichengreen"], "presenter": "Barry Eichengreen"},
                    {"title": "Discussion", "authors": ["Danny Quah"], "presenter": "Danny Quah"}
                ]
            },
            {
                "session_id": "AMPF-03",
                "session_title": "Luncheon Address: Trump Trade Policy and the World Trade System",
                "session_type": "Plenary",
                "date": "2026-05-22",
                "time": "12:45-13:45",
                "papers": [{"title": "Trump Trade Policy and the World Trade System", "authors": ["Douglas Irwin"], "presenter": "Douglas Irwin"}]
            },
            {
                "session_id": "AMPF-04",
                "session_title": "Policy Panel: The Evolving Contours of the Global Financial System",
                "session_type": "Panel",
                "date": "2026-05-22",
                "time": "13:45-15:10",
                "papers": [{"title": "Panel Discussion: The Evolving Contours of the Global Financial System", "authors": ["Viral Acharya", "Wenxin Du", "Ross Levine"], "presenter": "Amit Seru (Chair)"}]
            }
        ],
        "papers": [],
        "participants": [
            {"name": "Philip R. Lane", "institution": "European Central Bank", "is_presenter": True, "papers": ["Europe and the World Economy"]},
            {"name": "Eswar Prasad", "institution": "Cornell University", "is_presenter": True, "papers": ["Features and Fragilities of the International Monetary System"]},
            {"name": "Barry Eichengreen", "institution": "UC Berkeley", "is_presenter": True, "papers": ["Discussion of Prasad paper"]},
            {"name": "Danny Quah", "institution": "National University of Singapore", "is_presenter": True, "papers": ["Discussion of Prasad paper"]},
            {"name": "Douglas Irwin", "institution": "Dartmouth College", "is_presenter": True, "papers": ["Trump Trade Policy and the World Trade System"]},
            {"name": "Michael Spence", "institution": "Stanford University (Nobel Laureate)", "is_presenter": True, "papers": ["The Global Economy in Multiple Complex Transitions"]},
            {"name": "Viral Acharya", "institution": "New York University", "is_presenter": True, "papers": ["Panel: The Evolving Contours of the Global Financial System"]},
            {"name": "Wenxin Du", "institution": "Harvard Business School", "is_presenter": True, "papers": ["Panel: The Evolving Contours of the Global Financial System"]},
            {"name": "Ross Levine", "institution": "Hoover Institution, Stanford University", "is_presenter": True, "papers": ["Panel: The Evolving Contours of the Global Financial System"]},
            {"name": "Amit Seru", "institution": "Stanford Graduate School of Business", "is_presenter": True, "papers": ["Panel Chair"]},
            {"name": "Steven J. Davis", "institution": "Hoover Institution", "is_presenter": True, "papers": ["Chair: Keynote Q&A", "Chair: Luncheon Address"]},
            {"name": "Edward Robinson", "institution": "Monetary Authority of Singapore", "is_presenter": True, "papers": ["Welcome Remarks"]},
            {"name": "Sumit Agarwal", "institution": "National University of Singapore", "is_presenter": True, "papers": ["Chair: Discussion", "Closing Remarks"]},
            {"name": "Alvin Tan", "institution": "Ministry of Trade and Industry, Singapore", "is_presenter": False, "papers": []}
        ],
        "total_sessions": 5,
        "total_papers": 7,
        "total_participants": 14
    }
    return data


def save_and_upload(short_name, data, drive_name):
    """Save data.json and upload to Drive."""
    folder = os.path.join(DATA_DIR, short_name)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "data.json")
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    size_kb = os.path.getsize(path) / 1024
    print(f"  💾 {path} ({size_kb:.1f} KB)")
    print(f"     {data.get('total_sessions', 0)} sessions, {data.get('total_papers', 0)} papers, {data.get('total_participants', 0)} participants")
    
    # Upload
    try:
        from google.oauth2.credentials import Credentials as OAuthCreds
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        token_path = os.path.expanduser("~/.hermes/google_token.json")
        with open(token_path) as f:
            td = json.load(f)
        oauth_creds = OAuthCreds.from_authorized_user_info(td)
        drive = build('drive', 'v3', credentials=oauth_creds)
        
        FOLDER = "1IQY4Ip1X2ZzsxLn14okVcvMuV0CQGQOQ"
        results = drive.files().list(
            q=f"'{FOLDER}' in parents and name='{drive_name}' and trashed=false",
            fields="files(id, name)"
        ).execute()
        for f in results.get('files', []):
            drive.files().delete(fileId=f['id']).execute()
        
        media = MediaFileUpload(path, mimetype='application/json', resumable=True)
        f = drive.files().create(
            body={'name': drive_name, 'parents': [FOLDER]},
            media_body=media,
            fields='id, name, size'
        ).execute()
        print(f"  ☁️ Uploaded: {drive_name} ({int(f['size'])//1024} KB)")
    except Exception as e:
        print(f"  ⚠ Upload failed: {e}")


def main():
    print("=" * 60)
    
    # 1. ICMAIF
    print("\n📌 ICMAIF 2026 - Parsing Final Program PDF...")
    icmaif_data = parse_icmaif()
    save_and_upload("icmaif2026", icmaif_data,
        "ICMAIF_2026_30th_International_Conference_on_Macroeconomic_Analysis_and_International_Finance.json")
    
    # 2. RCEA
    print("\n📌 RCEA 2026 - Parsing EditorialExpress program...")
    rcea_data = parse_rcea()
    save_and_upload("rcea2026", rcea_data,
        "RCEA_2026_International_Conference_in_Economics_Econometrics_Finance.json")
    
    # 3. AMPF
    print("\n📌 AMPF 2026 - Building full agenda...")
    ampf_data = build_ampf()
    save_and_upload("ampf2026", ampf_data,
        "AMPF_2026_13th_Asian_Monetary_Policy_Forum.json")
    
    print("\n✅ All done!")

if __name__ == "__main__":
    main()
