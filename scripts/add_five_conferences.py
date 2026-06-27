#!/usr/bin/env python3
"""
Add 5 new conferences to the database:
1. ICMAIF 2026 (Crete, May 27-30)
2. RCEA 2026 (Madrid, May 25-27)
3. AMPF 2026 (Singapore, May 22)
4. 3CMFI 2026 (Frankfurt, Mar 23-24)
5. Danish Economic Society 2026 (Kolding, Jan 9-10)

Scrapes programs where available, builds v2 data.json, uploads to Drive.
"""

import json, os, sys, re, time
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from io import BytesIO

DATA_DIR = os.path.expanduser("~/economics-conferences")
NOW_ISO = datetime.now(timezone.utc).isoformat()
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"  ⚠ Failed: {url} — {e}")
                return ""

# ── 1. ICMAIF 2026 ──────────────────────────────────────────────

def scrape_icmaif():
    """Scrape ICMAIF 2026 program and participant list."""
    print("\n📌 ICMAIF 2026")
    
    # Get the conference program page
    html = fetch("https://icmaif.soc.uoc.gr/conference-program/")
    if not html:
        print("  ⚠ Program page not available")
        return None
    
    # Extract PDF link from program page
    pdf_match = re.search(r'href=[\'"]([^\'"]+\.pdf)[\'"][^>]*>Final Conference Program', html, re.IGNORECASE)
    pdf_url = pdf_match.group(1) if pdf_match else ""
    if pdf_url and not pdf_url.startswith("http"):
        pdf_url = "https://icmaif.soc.uoc.gr" + pdf_url
    
    # Try to get participant list
    participants_html = fetch("https://icmaif.soc.uoc.gr/list-of-participants/")
    
    # Try alternative URL
    if not participants_html or "Page not found" in participants_html:
        participants_html = fetch("https://icmaif.soc.uoc.gr/list-of-participants-2026/")
    
    # Parse participants if available
    participants = parse_icmaif_participants(participants_html)
    
    # Get keynote speakers from homepage
    html_home = fetch("https://icmaif.soc.uoc.gr/")
    keynotes = []
    if html_home:
        # Find keynote speakers
        kws = re.findall(r'<strong>(?:Keynote\s*Speaker|Invited\s*Speaker)[^<]*</strong>\s*:\s*([^<]+)', html_home, re.IGNORECASE)
        if not kws:
            # Try alternative pattern
            kws = re.findall(r'(?:Keynote|Invited)\s*(?:Speaker|Lecture)s?\s*:?\s*([A-Z][^<.]+?)(?:<|\.)', html_home)
        keynotes = [k.strip() for k in kws if k.strip()]
    
    print(f"  Keynotes: {keynotes}")
    print(f"  Participants found: {len(participants)}")
    print(f"  PDF Program: {pdf_url}")
    
    return build_icmaif_data(participants, keynotes, pdf_url)


def parse_icmaif_participants(html):
    """Parse ICMAIF participant list."""
    participants = []
    if not html or "Page not found" in html:
        return participants
    
    # Try to find participant entries
    text = re.sub(r'<[^>]+>', '\n', html)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Skip header/footer lines
    in_list = False
    for line in lines:
        if 'List of Participants' in line or 'Participants' in line:
            in_list = True
            continue
        if in_list and line and len(line) > 5 and not line.startswith('Page') and 'cookie' not in line.lower():
            # Check if it looks like a name
            if re.match(r'^[A-Z][a-z]', line) and not any(x in line.lower() for x in ['copyright', 'contact', 'home']):
                participants.append({"name": line, "institution": ""})
    
    return participants


def build_icmaif_data(participants, keynotes, pdf_url):
    """Build ICMAIF v2 data."""
    data = {
        "conference": {
            "name": "International Conference on Macroeconomic Analysis and International Finance",
            "short_name": "ICMAIF 2026",
            "year": 2026,
            "edition": "30th",
            "start_date": "2026-05-27",
            "end_date": "2026-05-30",
            "location": "Rethymno, Crete, Greece",
            "venue": "University of Crete",
            "city": "Rethymno",
            "country": "Greece",
            "website": "https://icmaif.soc.uoc.gr/",
            "program_url": "https://icmaif.soc.uoc.gr/conference-program/",
            "organizer": "University of Crete, Department of Economics",
            "extras": {
                "keynote_speakers": keynotes,
                "associated_journals": ["Journal of International Money and Finance", "Journal of Financial Stability", "Oxford Economic Papers", "Journal of Forecasting"],
                "special_issue_topics": [
                    "The Future of International Currencies in a World of Uncertainty",
                    "Banking, Systemic Risk, and Financial Stability",
                    "Forecasting in Economics and Finance: AI models and Big Data techniques vs Time Series methods"
                ],
                "ecb_presence": "Alexander Kleine (Talent Acquisition) - recruiting booth; Giulia Martorana presenting"
            }
        },
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://icmaif.soc.uoc.gr/",
            "program_url": pdf_url,
            "script_name": "add_five_conferences.py",
            "program_available": bool(pdf_url),
            "program_type": "pdf" if pdf_url else "web",
            "errors": [] if participants else ["Participant list not available as structured data"],
            "notes": f"30th edition. Found {len(participants)} participants. Program available as PDF at {pdf_url}"
        },
        "sessions": [{
            "session_id": "ICMAIF-K01",
            "session_title": "Keynote Sessions",
            "session_type": "Keynote",
            "date": "2026-05-27",
            "papers": [{"title": f"Keynote by {k}", "authors": [k], "presenter": k} for k in keynotes]
        }],
        "papers": [],
        "participants": participants,
        "total_sessions": 1,
        "total_papers": len(keynotes),
        "total_participants": len(participants)
    }
    return data


# ── 2. RCEA 2026 ────────────────────────────────────────────────

def scrape_rcea():
    """Scrape RCEA 2026 International Conference program."""
    print("\n📌 RCEA 2026")
    
    html = fetch("https://www.rcea.world/events/forthcoming-events/the-2026-rcea-international-conference")
    
    if not html:
        print("  ⚠ Page not available")
        return None
    
    # Look for program link
    prog_match = re.search(r'href=[\'"]([^\'"]*program[^\'"]*)[\'"]', html, re.IGNORECASE)
    prog_url = prog_match.group(1) if prog_match else ""
    if prog_url and not prog_url.startswith("http"):
        prog_url = "https://www.rcea.world" + prog_url
    
    # Extract description
    text = re.sub(r'<[^>]+>', '\n', html)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    desc_lines = []
    for line in lines:
        if any(w in line.lower() for w in ['conference venue', 'invites papers', 'bringing together', 'keynote', 'plenary']):
            desc_lines.append(line[:200])
    
    print(f"  Program URL: {prog_url}")
    print(f"  Description found: {len(desc_lines)} lines")
    
    data = {
        "conference": {
            "name": "RCEA International Conference in Economics, Econometrics, and Finance",
            "short_name": "RCEA 2026",
            "year": 2026,
            "edition": "2026",
            "start_date": "2026-05-25",
            "end_date": "2026-05-27",
            "location": "Madrid, Spain",
            "venue": "Universidad Pontificia de Comillas",
            "city": "Madrid",
            "country": "Spain",
            "website": "https://www.rcea.world/",
            "program_url": prog_url or "https://www.rcea.world/events/forthcoming-events/the-2026-rcea-international-conference",
            "organizer": "Rimini Centre for Economic Analysis (RCEA)",
            "extras": {
                "ecb_presence": "Andreea Liliana Vladu presenting 'Excess Liquidity and the Yield Curve'"
            }
        },
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://www.rcea.world/events/forthcoming-events/the-2026-rcea-international-conference",
            "program_url": prog_url,
            "script_name": "add_five_conferences.py",
            "program_available": bool(prog_url),
            "program_type": "web",
            "errors": [],
            "notes": f"Program available at {prog_url}. Papers in all areas of Economics, Econometrics, and Finance."
        },
        "sessions": [],
        "papers": [],
        "participants": [
            {"name": "Andreea Liliana Vladu", "institution": "European Central Bank", "papers": ["Excess Liquidity and the Yield Curve"], "is_presenter": True}
        ],
        "total_sessions": 0,
        "total_papers": 1,
        "total_participants": 1
    }
    return data


# ── 3. AMPF 2026 ────────────────────────────────────────────────

def build_ampf():
    """Build AMPF 2026 data (forum, not easily scrapeable)."""
    print("\n📌 AMPF 2026 (Asian Monetary Policy Forum)")
    
    data = {
        "conference": {
            "name": "Asian Monetary Policy Forum",
            "short_name": "AMPF 2026",
            "year": 2026,
            "edition": "13th",
            "start_date": "2026-05-22",
            "end_date": "2026-05-22",
            "location": "Singapore",
            "venue": "Conrad Singapore Orchard",
            "city": "Singapore",
            "country": "Singapore",
            "website": "https://abfer.org/20-events/asian-monetary-policy-forum",
            "program_url": "",
            "organizer": "Asian Bureau of Finance and Economic Research (ABFER), NUS Business School, Chicago Booth, Monetary Authority of Singapore",
            "extras": {
                "format": "By-invitation forum for policymakers and academics",
                "ecb_presence": "Philip R. Lane gave the opening address 'Europe and the world economy'"
            }
        },
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://abfer.org/20-events/asian-monetary-policy-forum",
            "script_name": "add_five_conferences.py",
            "program_available": False,
            "program_type": "manual",
            "errors": ["Program not publicly available (invitation-only forum)"],
            "notes": "13th edition. Invitation-only forum for high-level central bankers and academics. Philip R. Lane (ECB) gave opening address."
        },
        "sessions": [{
            "session_id": "AMPF-S01",
            "session_title": "Opening Address: Europe and the World Economy",
            "session_type": "Plenary",
            "date": "2026-05-22",
            "papers": [{"title": "Europe and the World Economy", "authors": ["Philip R. Lane"], "presenter": "Philip R. Lane"}]
        }],
        "papers": [],
        "participants": [
            {"name": "Philip R. Lane", "institution": "European Central Bank", "is_presenter": True, "papers": ["Europe and the World Economy"]}
        ],
        "total_sessions": 1,
        "total_papers": 1,
        "total_participants": 1
    }
    return data


# ── 4. 3CMFI 2026 ──────────────────────────────────────────────

def scrape_3cmfi():
    """Scrape 3rd International Conference on the Climate-Macro-Finance Interface program."""
    print("\n📌 3CMFI 2026")
    
    html = fetch("https://editorialexpress.com/conference/3CMFI/program/3CMFI.html")
    if not html:
        print("  ⚠ Program not available")
        return build_3cmfi_basic()
    
    # Parse sessions and participants
    sessions = []
    participants_dict = {}
    
    # Split into session blocks
    blocks = re.split(r'<tr[^>]*>', html)
    
    current_session = None
    for block in blocks:
        # Check if this is a session header
        header_match = re.search(r'<a[^>]*>\s*Session\s*(\d+)', block)
        if header_match:
            if current_session:
                sessions.append(current_session)
            session_num = header_match.group(1)
            # Get session title
            title_match = re.search(r'<a[^>]*>\s*Session\s*\d+\s*:\s*([^<]+)</a>', block)
            title = title_match.group(1).strip() if title_match else f"Session {session_num}"
            current_session = {
                "session_id": f"3CMFI-S{session_num}",
                "session_title": title,
                "session_type": "Contributed",
                "papers": []
            }
        
        # Paper entries have author info
        if current_session:
            paper_match = re.search(r'<p[^>]*>\s*<strong>([^<]+)</strong>', block)
            if paper_match:
                paper_title = paper_match.group(1).strip()
                
                # Authors are typically after the title
                author_match = re.search(r'</strong>\s*<br>\s*([^<]+)', block)
                authors_text = author_match.group(1).strip() if author_match else ""
                authors = [a.strip() for a in re.split(r',|;', authors_text) if a.strip()]
                
                current_session["papers"].append({
                    "title": paper_title,
                    "authors": authors,
                    "presenter": authors[0] if authors else ""
                })
                
                for a in authors:
                    if a not in participants_dict:
                        participants_dict[a] = {"name": a, "institution": "", "is_presenter": True, "papers": []}
                    participants_dict[a]["papers"].append(paper_title)
    
    if current_session:
        sessions.append(current_session)
    
    # Get the index of all participants for institutions
    # The page has a link to an index
    print(f"  Sessions: {len(sessions)}")
    print(f"  Papers: {sum(len(s['papers']) for s in sessions)}")
    print(f"  Participants: {len(participants_dict)}")
    
    data = {
        "conference": {
            "name": "Third International Conference on the Climate-Macro-Finance Interface",
            "short_name": "3CMFI 2026",
            "year": 2026,
            "edition": "3rd",
            "start_date": "2026-03-23",
            "end_date": "2026-03-24",
            "location": "Frankfurt, Germany",
            "venue": "Leibniz Institute for Financial Research SAFE, Goethe University Frankfurt",
            "city": "Frankfurt",
            "country": "Germany",
            "website": "https://safe-frankfurt.de/news-media/events/event-view/3rd-international-conference-on-the-climate-macro-finance-interface-3cmfi.html",
            "program_url": "https://editorialexpress.com/conference/3CMFI/program/3CMFI.html",
            "organizer": "Leibniz SAFE, RCEA-Europe, Deutsche Bundesbank, European Central Bank",
            "extras": {
                "keynote_speakers": ["Sabine Mauderer (Bundesbank)"],
                "ecb_presence": "Philip R. Lane (keynote 'AI and the euro area economy'), Alexander Popov (discussant), Caroline Willeke (chair), Margherita Giuzio (co-organizer)",
                "theme": "Emerging Macroeconomic, Financial, and Environmental Policy Challenges in an Era of Policrisis and Rising Uncertainties"
            }
        },
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://editorialexpress.com/conference/3CMFI/program/3CMFI.html",
            "script_name": "add_five_conferences.py",
            "program_available": True,
            "program_type": "web",
            "errors": [],
            "notes": f"Full program scraped from EditorialExpress. {sum(len(s['papers']) for s in sessions)} papers across {len(sessions)} sessions."
        },
        "sessions": sessions,
        "papers": [],
        "participants": list(participants_dict.values()),
        "total_sessions": len(sessions),
        "total_papers": sum(len(s['papers']) for s in sessions),
        "total_participants": len(participants_dict)
    }
    return data


def build_3cmfi_basic():
    """Fallback minimal 3CMFI entry."""
    return {
        "conference": {
            "name": "Third International Conference on the Climate-Macro-Finance Interface",
            "short_name": "3CMFI 2026",
            "year": 2026,
            "edition": "3rd",
            "start_date": "2026-03-23",
            "end_date": "2026-03-24",
            "location": "Frankfurt, Germany",
            "venue": "SAFE, Goethe University Frankfurt",
            "organizer": "Leibniz SAFE, RCEA-Europe, Deutsche Bundesbank, ECB",
            "website": "https://safe-frankfurt.de/news-media/events/event-view/3rd-international-conference-on-the-climate-macro-finance-interface-3cmfi.html",
            "extras": {
                "ecb_presence": "Philip R. Lane (keynote), Alexander Popov (discussant), Caroline Willeke (chair)"
            }
        },
        "scrape_metadata": {
            "scraped_at": NOW_ISO, "program_available": False,
            "errors": ["Program page not accessible"],
            "script_name": "add_five_conferences.py"
        },
        "sessions": [], "papers": [], "participants": [],
        "total_sessions": 0, "total_papers": 0, "total_participants": 0
    }


# ── 5. Danish Economic Society 2026 ──────────────────────────────

def build_danish_econ():
    """Build Danish Economic Society 2026 data."""
    print("\n📌 Danish Economic Society 2026")
    
    data = {
        "conference": {
            "name": "Danish Economic Society Annual Meeting",
            "short_name": "DES 2026",
            "year": 2026,
            "edition": "2026",
            "start_date": "2026-01-09",
            "end_date": "2026-01-10",
            "location": "Kolding, Denmark",
            "venue": "Koldingfjord",
            "city": "Kolding",
            "country": "Denmark",
            "website": "https://nof.econ.ku.dk/arrangementer/årsmoeder/",
            "program_url": "https://nof.econ.ku.dk/arrangementer/årsmoeder/",
            "organizer": "Nationaløkonomisk Forening (Danish Economic Society)",
            "extras": {
                "keynote_speakers": ["Philip R. Lane (European Central Bank)", "Signe Krogstrup (Danmarks Nationalbank)"],
                "theme": "Danish and international economic policy",
                "language": "Danish / English"
            }
        },
        "scrape_metadata": {
            "scraped_at": NOW_ISO,
            "source_url": "https://nof.econ.ku.dk/arrangementer/årsmoeder/",
            "script_name": "add_five_conferences.py",
            "program_available": False,
            "program_type": "manual",
            "errors": ["Program page in Danish, parallel sessions not available online"],
            "notes": "Philip R. Lane gave keynote 'The euro in a changing world'. Danish central bank governor and other Danish economists also spoke."
        },
        "sessions": [{
            "session_id": "DES-K01",
            "session_title": "Keynote: The euro in a changing world",
            "session_type": "Keynote",
            "date": "2026-01-09",
            "papers": [{"title": "The euro in a changing world", "authors": ["Philip R. Lane"], "presenter": "Philip R. Lane"}]
        }],
        "papers": [],
        "participants": [
            {"name": "Philip R. Lane", "institution": "European Central Bank", "is_presenter": True, "papers": ["The euro in a changing world"]}
        ],
        "total_sessions": 1,
        "total_papers": 1,
        "total_participants": 1
    }
    return data


# ── Pipeline ────────────────────────────────────────────────────

def save_data(short_name, data):
    folder = os.path.join(DATA_DIR, short_name.lower().replace(" ", "_"))
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "data.json")
    
    # Add some participant validation
    for p in data.get("participants", []):
        p.setdefault("institution", "")
        p.setdefault("papers", [])
        p.setdefault("paper_titles", [])
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    size = os.path.getsize(path) / 1024
    print(f"  💾 Saved: {path} ({size:.1f} KB)")
    return path


def upload_to_drive(data_path, short_name, folder_id, drive_name):
    """Upload a file to Google Drive."""
    try:
        from google.oauth2.credentials import Credentials as OAuthCreds
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        token_path = os.path.expanduser("~/.hermes/google_token.json")
        with open(token_path) as f:
            token_data = json.load(f)
        oauth_creds = OAuthCreds.from_authorized_user_info(token_data)
        drive = build('drive', 'v3', credentials=oauth_creds)
        
        # Delete old version
        results = drive.files().list(
            q=f"'{folder_id}' in parents and name='{drive_name}' and trashed=false",
            fields="files(id, name)"
        ).execute()
        for f in results.get('files', []):
            drive.files().delete(fileId=f['id']).execute()
        
        media = MediaFileUpload(data_path, mimetype='application/json', resumable=True)
        f = drive.files().create(
            body={'name': drive_name, 'parents': [folder_id]},
            media_body=media,
            fields='id, name, size'
        ).execute()
        print(f"  ☁️ Uploaded: {drive_name} ({int(f['size'])//1024} KB)")
        return True
    except Exception as e:
        print(f"  ⚠ Drive upload failed: {e}")
        return False


def main():
    JSON_FOLDER = "1IQY4Ip1X2ZzsxLn14okVcvMuV0CQGQOQ"
    
    conferences = [
        ("icmaif2026", "ICMAIF_2026_30th_International_Conference_on_Macroeconomic_Analysis_and_International_Finance.json", scrape_icmaif),
        ("rcea2026", "RCEA_2026_International_Conference_in_Economics_Econometrics_Finance.json", scrape_rcea),
        ("ampf2026", "AMPF_2026_13th_Asian_Monetary_Policy_Forum.json", build_ampf),
        ("3cmfi2026", "3CMFI_2026_3rd_International_Conference_on_Climate_Macro_Finance_Interface.json", scrape_3cmfi),
        ("des2026", "DES_2026_Danish_Economic_Society_Annual_Meeting.json", build_danish_econ),
    ]
    
    results = {}
    for short_name, drive_name, scraper_fn in conferences:
        print(f"\n{'='*60}")
        print(f"  Conference: {short_name}")
        print(f"{'='*60}")
        
        try:
            data = scraper_fn()
            if data:
                path = save_data(short_name, data)
                upload_to_drive(path, short_name, JSON_FOLDER, drive_name)
                results[short_name] = {
                    "sessions": data.get("total_sessions", 0),
                    "participants": data.get("total_participants", 0),
                    "papers": data.get("total_papers", 0),
                    "drive_file": drive_name
                }
            else:
                print(f"  ❌ Scraper returned no data")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    for short, r in results.items():
        print(f"  ✅ {short:15s} | {r['sessions']} sessions | {r['participants']} participants | {r['papers']} papers")
    
    # Save the script itself
    try:
        from google.oauth2.credentials import Credentials as OAuthCreds
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        token_path = os.path.expanduser("~/.hermes/google_token.json")
        with open(token_path) as f:
            token_data = json.load(f)
        oauth_creds = OAuthCreds.from_authorized_user_info(token_data)
        drive = build('drive', 'v3', credentials=oauth_creds)
        SCRIPT_FOLDER = "1r1C-IuO5RS6zqSme2ETBE8PK8cy7b1IA"
        script_name = "add_five_conferences.py"
        results = drive.files().list(
            q=f"'{SCRIPT_FOLDER}' in parents and name='{script_name}' and trashed=false",
            fields="files(id, name)"
        ).execute()
        for f in results.get('files', []):
            drive.files().delete(fileId=f['id']).execute()
        media = MediaFileUpload(__file__, mimetype='text/x-python', resumable=True)
        f = drive.files().create(
            body={'name': script_name, 'parents': [SCRIPT_FOLDER]},
            media_body=media,
            fields='id, name, size'
        ).execute()
        print(f"\n☁️ Script uploaded to Drive: {script_name} ({int(f['size'])//1024} KB)")
    except Exception as e:
        print(f"\n⚠ Script upload skipped: {e}")


if __name__ == "__main__":
    main()
