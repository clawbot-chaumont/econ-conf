#!/usr/bin/env python3
"""
Master pipeline for conference scraping:
  1. Scrape / re-scrape conference program
  2. Convert to v2 schema
  3. Update Google Sheet
  4. Upload to Google Drive

Usage:
  python3 master_pipeline.py <short_name>    # Single conference
  python3 master_pipeline.py --all            # All conferences
  python3 master_pipeline.py --status         # Check status only
"""

import json, os, sys, re, time
from datetime import datetime, date

DATA_DIR = os.path.expanduser("~/economics-conferences")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

V2_SCHEMA_FILE = os.path.join(DATA_DIR, "SCHEMA_TARGET.md")

# Known conference info (2026 editions)
CONFERENCES_2026 = {
    "AEA": {
        "name": "American Economic Association Annual Meeting",
        "website": "https://www.aeaweb.org/conference/2026/program",
        "start_date": "2026-01-03", "end_date": "2026-01-05",
        "location": "San Francisco, USA",
        "scraper_type": "custom", "folder": "aea2026",
    },
    "AFA": {
        "name": "American Finance Association Annual Meeting",
        "website": "https://www.afajof.org/annual-meeting/",
        "start_date": "2026-01-03", "end_date": "2026-01-05",
        "location": "San Francisco, USA",
        "scraper_type": "web", "folder": "afa2026",
    },
    "AFSE": {
        "name": "Association Française de Sciences Economiques (AFSE)",
        "website": "https://afse2026.sciencesconf.org",
        "start_date": "2026-06-17", "end_date": "2026-06-19",
        "location": "Paris, France",
        "scraper_type": "sciencesconf", "folder": "afse2026",
    },
    "JMA": {
        "name": "Journées de Microéconomie Appliquée",
        "website": "https://jma2026.sciencesconf.org",
        "start_date": "2026-06-04", "end_date": "2026-06-05",
        "location": "France",
        "scraper_type": "sciencesconf", "folder": "jma2026",
    },
    "AFFI": {
        "name": "French Finance Association International Conference",
        "website": "https://affi2026.sciencesconf.org",
        "start_date": "2026-05-25", "end_date": "2026-05-27",
        "location": "France",
        "scraper_type": "sciencesconf", "folder": "affi2026",
    },
    "GDRE": {
        "name": "Symposium on Money Banking and Finance (GDRE)",
        "website": "https://gdre2026.sciencesconf.org",
        "start_date": "2026-06-22", "end_date": "2026-06-23",
        "location": "France",
        "scraper_type": "sciencesconf", "folder": "gdre2026",
    },
    "EEA": {
        "name": "European Economic Association Annual Congress",
        "website": "https://eea-esem2026.org",
        "start_date": "2026-08-17", "end_date": "2026-08-21",
        "location": "Dublin, Ireland",
        "scraper_type": "web", "folder": "eea2026",
    },
    "EFA": {
        "name": "European Finance Association Annual Meeting",
        "website": "https://www.conftool.com/efa2026",
        "start_date": "2026-08-19", "end_date": "2026-08-22",
        "location": "Netherlands",
        "scraper_type": "conftool", "folder": "efa2026",
    },
    "IAAE": {
        "name": "International Association for Applied Econometrics",
        "website": "https://iaae2026.org",
        "start_date": "2026-06-16", "end_date": "2026-06-19",
        "location": "Italy",
        "scraper_type": "web", "folder": "iaae2026",
    },
    "RES": {
        "name": "Royal Economic Society Annual Conference",
        "website": "https://res.org.uk/event-listing/res-2026-annual-conference/",
        "start_date": "2026-07-06", "end_date": "2026-07-08",
        "location": "Newcastle, United Kingdom",
        "scraper_type": "custom", "folder": "res2026",
    },
    "CEA": {
        "name": "Canadian Economics Association Annual Conference",
        "website": "https://economics.ca/2026/",
        "start_date": "2026-05-29", "end_date": "2026-05-31",
        "location": "Canada",
        "scraper_type": "web", "folder": "cea2026",
    },
    "WEAI": {
        "name": "Western Economics Association International",
        "website": "https://weai.org/conferences",
        "start_date": "2026-06-28", "end_date": "2026-07-02",
        "location": "USA",
        "scraper_type": "web", "folder": "weai2026",
    },
    "SIC": {
        "name": "NBER Summer Institute",
        "website": "https://www.nber.org/conferences/summer-institute-2026",
        "start_date": "2026-07-06", "end_date": "2026-07-24",
        "location": "Cambridge, USA",
        "scraper_type": "custom", "folder": "sic2026",
    },
    "BWBFI": {
        "name": "Bristol Workshop on Banking and Financial Intermediation",
        "website": "https://sites.google.com/view/banking-workshop",
        "start_date": "2026-06-11", "end_date": "2026-06-12",
        "location": "Bristol, United Kingdom",
        "scraper_type": "web", "folder": "bwbfi2026",
    },
    "IRMC": {
        "name": "International Risk Management Conference",
        "website": "https://www.therisksociety.com/irmc",
        "start_date": "2026-06-17", "end_date": "2026-06-19",
        "location": "International",
        "scraper_type": "web", "folder": "irmc2026",
    },
    "MOFIR": {
        "name": "Money and Finance Research Group Conference",
        "website": "https://www.mofir.net/conference",
        "start_date": "2026-09-03", "end_date": "2026-09-04",
        "location": "Milan, Italy",
        "scraper_type": "custom", "folder": "mofir2026",
    },
    "SCFICF": {
        "name": "Summer Conference on Financial Intermediation and Corporate Finance",
        "website": "https://summerfinconf.wixsite.com/mysite",
        "start_date": "2026-06-29", "end_date": "2026-07-01",
        "location": "International",
        "scraper_type": "custom", "folder": "scficf",
    },
    "AC-MFR": {
        "name": "Annual Conference on Macro-Finance Research",
        "website": "https://www.frbsf.org/news-and-media/events/conferences/2026/10/conference-on-macro-finance-research-2026/",
        "start_date": "2026-10-09", "end_date": "2026-10-09",
        "location": "San Francisco, USA",
        "scraper_type": "web", "folder": "ac-mfr",
    },
    "SSFMR": {
        "name": "Swiss Society for Financial Market Research Annual Meeting",
        "website": "https://www.fmpm.ch/",
        "start_date": "2026-04-01", "end_date": "2026-04-03",
        "location": "Zurich, Switzerland",
        "scraper_type": "web", "folder": "ssfmr2026",
    },
    "GFA": {
        "name": "German Finance Association Annual Meeting",
        "website": "https://bank.uni-hohenheim.de/dgf2026",
        "start_date": "2026-09-24", "end_date": "2026-09-26",
        "location": "Germany",
        "scraper_type": "web", "folder": "gfa2026",
    },
    "PDFM": {
        "name": "Paris December Finance Meeting",
        "website": "https://www.paris-december.eu/",
        "start_date": "2026-12-17", "end_date": "2026-12-18",
        "location": "Paris, France",
        "scraper_type": "web", "folder": "pdfm2026",
    },
    "CEBRA": {
        "name": "Central Bank Research Association Annual Meeting",
        "website": "https://cebra.org/meeting/",
        "start_date": "2026-08-27", "end_date": "2026-08-28",
        "location": "USA",
        "scraper_type": "web", "folder": "cebra2026",
    },
    "SFS": {
        "name": "Society for Financial Studies Cavalcade",
        "website": "https://sfs.org/cavalcade/",
        "start_date": "2026-05-13", "end_date": "2026-05-15",
        "location": "USA",
        "scraper_type": "web", "folder": "sfs2026",
    },
    "CEPRPS": {
        "name": "CEPR Paris Symposium",
        "website": "https://cepr.org/paris-symposium-2026",
        "start_date": "2026-12-08", "end_date": "2026-12-10",
        "location": "Paris, France",
        "scraper_type": "web", "folder": "ceprps2026",
    },
    "ECBARC": {
        "name": "ECB Annual Research Conference",
        "website": "https://www.ecb.europa.eu/pub/conferences/ecbforum/html/index.en.html",
        "start_date": "2026-09-21", "end_date": "2026-09-22",
        "location": "Frankfurt, Germany",
        "scraper_type": "web", "folder": "ecbarc2026",
    },
    "CMRC": {
        "name": "Community Banking Research Conference",
        "website": "https://www.csbs.org/community-banking-research-conference",
        "start_date": "2026-10-07", "end_date": "2026-10-08",
        "location": "USA",
        "scraper_type": "web", "folder": "cmrc2026",
    },
    "MYE": {
        "name": "Spring Meeting of Young Economists",
        "website": "https://smye2026.org",
        "start_date": "2026-05-18", "end_date": "2026-05-20",
        "location": "International",
        "scraper_type": "web", "folder": "mye2026",
    },
    "BFSR": {
        "name": "Bocconi Financial Stability and Regulation Conference",
        "website": "https://www.bancaditalia.it/pubblicazioni/altri-atti-convegni/",
        "start_date": "2026-03-17", "end_date": "2026-03-18",
        "location": "Milan, Italy",
        "scraper_type": "web", "folder": "bfsr2026",
    },
    "ESSFM": {
        "name": "European Summer Symposium in Financial Markets",
        "website": "https://cepr.org/essfm-2026",
        "start_date": "2026-07-12", "end_date": "2026-07-24",
        "location": "Switzerland",
        "scraper_type": "web", "folder": "essfm2026",
    },
    "MPRC": {
        "name": "ECB/IMF Macroprudential Policy and Research Conference",
        "website": "https://www.ecb.europa.eu/pub/conferences/html/index.en.html",
        "start_date": "2026-06-24", "end_date": "2026-06-25",
        "location": "Frankfurt, Germany",
        "scraper_type": "web", "folder": "mprc2026",
    },
    "SEA": {
        "name": "Southern Economic Association Annual Meeting",
        "website": "https://www.southerneconomic.org/",
        "start_date": "2026-11-21", "end_date": "2026-11-23",
        "location": "USA",
        "scraper_type": "web", "folder": "sea2026",
    },
    "SFWFIR": {
        "name": "BSE Summer Forum Workshop on Financial Intermediation and Risk",
        "website": "https://www.bse.eu/summer-forum/",
        "start_date": "2026-06-08", "end_date": "2026-06-09",
        "location": "Barcelona, Spain",
        "scraper_type": "web", "folder": "sfwfir2026",
    },
    "WCIEA": {
        "name": "World Congress of the International Economic Association",
        "website": "https://www.iea-world.com/",
        "start_date": "2026-06-22", "end_date": "2026-06-26",
        "location": "International",
        "scraper_type": "web", "folder": "wciea2026",
    },
    "NBER": {
        "name": "NBER Summer Institute",
        "website": "https://www.nber.org/conferences/summer-institute-2026",
        "start_date": "2026-07-06", "end_date": "2026-07-24",
        "location": "Cambridge, USA",
        "scraper_type": "custom", "folder": "nber2026",
    },
    "DES": {
        "name": "Danish Economic Society Annual Meeting",
        "website": "https://nationaloekonomiskforening.dk/",
        "start_date": "2026-01-01", "end_date": "2026-01-01",
        "location": "Denmark",
        "scraper_type": "custom", "folder": "des2026",
    },
    "3CMFI": {
        "name": "International Conference on Climate Macro Finance Interface",
        "website": "https://3cmfi.org/",
        "start_date": "2026-06-01", "end_date": "2026-06-02",
        "location": "International",
        "scraper_type": "custom", "folder": "3cmfi2026",
    },
    "ICMAIF": {
        "name": "International Conference on Macroeconomic Analysis and International Finance",
        "website": "https://icmaif.org/",
        "start_date": "2026-05-27", "end_date": "2026-05-29",
        "location": "Greece",
        "scraper_type": "custom", "folder": "icmaif2026",
    },
    "RCEA": {
        "name": "International Conference in Economics, Econometrics and Finance",
        "website": "https://rcea.org/",
        "start_date": "2026-07-01", "end_date": "2026-07-03",
        "location": "International",
        "scraper_type": "custom", "folder": "rcea2026",
    },
    "SWCFI": {
        "name": "BIS-CEPR-SFI Conference on Financial Intermediation",
        "website": "https://www.swiss-fi.com/conference-programme",
        "start_date": "2026-05-10", "end_date": "2026-05-13",
        "location": "Gerzensee, Switzerland",
        "scraper_type": "web", "folder": "swcfi2026",
    },
    "CMFR": {
        "name": "Conference on Financial Market Regulation",
        "website": "https://www.sec.gov/newsroom/meetings-events/13th-annual-conference-financial-market-regulation",
        "start_date": "2026-05-07", "end_date": "2026-05-08",
        "location": "Washington DC, USA",
        "scraper_type": "web", "folder": "cmfr2026",
    },
    "CSRA": {
        "name": "Bank of Finland/ESRB Conference on AI and Systemic Risk Analytics",
        "website": "https://www.suomenpankki.fi",
        "start_date": "2026-06-03", "end_date": "2026-06-04",
        "location": "Helsinki, Finland",
        "scraper_type": "web", "folder": "csra2026",
    },
    "RFILB": {
        "name": "Financial Risks International Forum",
        "website": "https://www.risks-forum.org/",
        "start_date": "2026-03-30", "end_date": "2026-03-31",
        "location": "Paris, France",
        "scraper_type": "web", "folder": "rfilb2026",
    },
    "WFA": {
        "name": "Western Finance Association Annual Meeting",
        "website": "https://westernfinance.org/conference-2026/",
        "start_date": "2026-06-21", "end_date": "2026-06-24",
        "location": "Denver, CO, USA",
        "scraper_type": "web", "folder": "wfa2026",
    },
    "BDPCEPR": {
        "name": "Banco de Portugal and CEPR Conference on Financial Intermediation",
        "website": "https://cepr.org/events/banco-de-portugal-and-cepr-conference-financial-intermediation-2026",
        "start_date": "2026-06-19", "end_date": "2026-06-20",
        "location": "Ponta Delgada, Azores, Portugal",
        "scraper_type": "web", "folder": "bdpcepr2026",
    },
}

# ── Helpers ───────────────────────────────────────────────────────────

def load_data_json(folder_name):
    """Load existing data.json from conference folder."""
    path = os.path.join(DATA_DIR, folder_name, "data.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_data_json(folder_name, data):
    """Write data.json to conference folder."""
    conf_dir = os.path.join(DATA_DIR, folder_name)
    os.makedirs(conf_dir, exist_ok=True)
    path = os.path.join(conf_dir, "data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Écrit: {path}")
    return path


def get_session_title(sess):
    """Extract session title from various possible field names."""
    for key in ("session_title", "title", "name", "session_name", "topic"):
        val = sess.get(key)
        if val and isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def get_papers_array(sess):
    """Extract papers array from session, handling speakers format (EEA) and others."""
    papers = sess.get("papers", [])
    if isinstance(papers, list):
        return papers
    
    # Try speakers array (EEA format) — treat speakers as paper-less entries
    speakers = sess.get("speakers", [])
    if isinstance(speakers, list) and len(speakers) > 0:
        result = []
        for sp in speakers:
            if isinstance(sp, dict):
                sp_name = sp.get("name", "")
                if sp_name:
                    result.append({"title": "", "authors": [sp_name], "presenter": sp_name})
                else:
                    result.append({"title": ""})
            else:
                result.append({"title": str(sp)})
        return result
    
    return []


def get_institution(p):
    """Extract institution from various possible field names."""
    for key in ("institution", "institution_clean", "institution_raw", "affiliation", "org"):
        val = p.get(key)
        if val is not None:
            if isinstance(val, list):
                return "; ".join(str(x) for x in val)
            return str(val)
    return ""


def extract_paper_titles(p):
    """Extract paper titles from participant entry (handles dict, list, string)."""
    papers = p.get("papers", p.get("paper_titles", []))
    if isinstance(papers, list):
        titles = []
        for pt in papers:
            if isinstance(pt, dict):
                titles.append(pt.get("title", str(pt)))
            else:
                titles.append(str(pt))
        return titles
    elif isinstance(papers, str) and papers.strip():
        return [papers.strip()]
    return []


def normalize_participant_name(raw_name):
    """Clean trailing affiliation numbers from participant names."""
    import re
    if not raw_name or not isinstance(raw_name, str):
        return ""
    return re.sub(r'[\d,\s]+$', '', raw_name).strip()


def convert_to_v2(conf_key, old_data):
    """
    Convert any existing data to v2 schema.
    The v2 schema requires:
    - conference: dict (not string)
    - sessions: flat array, each with session_title (non-empty str) and papers (array)
    - participants: array with institution as string, papers as string array
    - scrape_metadata: dict
    """
    conf_info = CONFERENCES_2026.get(conf_key, {})
    
    # Build conference dict
    if isinstance(old_data.get("conference"), dict):
        conf = dict(old_data["conference"])
    elif isinstance(old_data.get("conference"), str):
        conf = {"name": old_data["conference"], "short_name": conf_key}
    else:
        conf = {"name": conf_info.get("name", conf_key), "short_name": conf_key}

    # Ensure mandatory conference fields
    conf.setdefault("name", conf_info.get("name", conf_key))
    conf.setdefault("short_name", conf_key)
    conf.setdefault("year", conf_info.get("year", 2026))
    conf.setdefault("start_date", conf_info.get("start_date", ""))
    conf.setdefault("end_date", conf_info.get("end_date", ""))
    conf.setdefault("location", conf_info.get("location", ""))
    
    # Any extra fields go into extras
    extras = {}
    for k in list(conf.keys()):
        if k not in ("name", "short_name", "year", "start_date", "end_date", "location"):
            extras[k] = conf.pop(k)
    if extras:
        conf["extras"] = extras

    # Convert sessions to flat array
    sessions_old = old_data.get("sessions", [])
    sessions_new = []
    for i, sess in enumerate(sessions_old):
        if not isinstance(sess, dict):
            continue
        
        # Get session title (try all possible field names)
        title = get_session_title(sess)
        if not title:
            title = f"Session {i + 1}"
        
        ns = {
            "session_title": title,
            "chair": sess.get("chair", sess.get("chairperson", "")),
            "date": sess.get("date", sess.get("day", "")),
            "time": sess.get("time", sess.get("timeslot", "")),
            "room": sess.get("room", sess.get("location", "")),
        }
        # Remove truly empty optional fields (chair, date, time, room are optional)
        for k in list(ns.keys()):
            if k != "session_title" and not ns[k]:
                del ns[k]
        
        # Convert papers (handles both regular papers and EEA speakers format)
        papers_raw = get_papers_array(sess)
        papers_new = []
        for paper in papers_raw:
            if isinstance(paper, str):
                papers_new.append({"title": paper, "authors": [], "presenter": ""})
            elif isinstance(paper, dict):
                authors = paper.get("authors", paper.get("author", ""))
                if isinstance(authors, str):
                    authors = [a.strip() for a in authors.split(";") if a.strip()]
                    if not authors and paper.get("author"):
                        authors = [paper["author"].strip()]
                elif isinstance(authors, list):
                    authors = [str(a) for a in authors]
                papers_new.append({
                    "title": paper.get("title", ""),
                    "authors": authors if isinstance(authors, list) else [authors] if authors else [],
                    "presenter": paper.get("presenter", paper.get("presenter_clean", "")),
                })
        
        # ALWAYS include papers array (even empty)—required by v2 schema
        ns["papers"] = papers_new
        sessions_new.append(ns)

    # Convert participants
    participants_old = old_data.get("participants", [])
    participants_new = []
    seen_names = set()
    for p in participants_old:
        name = normalize_participant_name(p.get("name", "")).strip()
        if not name or name.lower() in seen_names:
            continue
        seen_names.add(name.lower())
        
        institution = get_institution(p)
        
        paper_titles = extract_paper_titles(p)
        
        participants_new.append({
            "name": name,
            "institution": institution if institution else "",
            "is_presenter": p.get("is_presenter", p.get("role", "") == "presenter"),
            "papers": paper_titles,
        })

    # Build scrape_metadata
    source_url = conf_info.get("website", "")
    program_url = old_data.get("conference", {}).get("program_url", "") if isinstance(old_data.get("conference"), dict) else ""
    scrape_metadata = old_data.get("scrape_metadata", {})
    if not scrape_metadata or not isinstance(scrape_metadata, dict):
        scrape_metadata = {
            "scraped_at": datetime.now().isoformat(),
            "source_url": source_url or "unknown",
            "program_available": len(sessions_new) > 0,
            "program_type": "web",
            "errors": [],
        }
    scrape_metadata.setdefault("scraped_at", datetime.now().isoformat())
    scrape_metadata.setdefault("source_url", source_url or "unknown")
    scrape_metadata.setdefault("program_available", len(sessions_new) > 0)
    scrape_metadata.setdefault("program_type", "web")
    scrape_metadata.setdefault("errors", [])

    return {
        "conference": conf,
        "scrape_metadata": scrape_metadata,
        "sessions": sessions_new,
        "participants": participants_new,
    }


def update_google_sheet(conf_key, data, conf_info):
    """Update the Google Sheet with conference data."""
    try:
        from google.oauth2.credentials import Credentials
        import gspread
        
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_authorized_user_file(
            os.path.expanduser("~/.hermes/google_token.json"), SCOPES
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key("17sfWz82YgaoK6_Kznv1SNXTOO55RuuwCDMJ6RT3ZYgw")
        ws = sh.worksheet("Conferences")
        
        rows = ws.get_all_values()
        header = rows[0]
        all_rows = rows[1:]
        
        # Find existing row for this conference + year 2026
        target_row = None
        for i, row in enumerate(all_rows, start=2):  # 1-indexed, header is row 1
            if row[1].strip().upper() == conf_key.upper() and row[2].strip() == "2026":
                target_row = i
                break
        
        # If not found, find the row for the conference (any year) and update
        if not target_row:
            for i, row in enumerate(all_rows, start=2):
                if row[1].strip().upper() == conf_key.upper():
                    target_row = i
                    break
        
        if target_row:
            now_str = datetime.now().strftime("%d/%m/%Y")
            updates = {}
            
            # Website_link (col 6, 0-indexed=5)
            website = conf_info.get("website", "")
            if website:
                updates[5] = website
            
            # Entry_check_date (col 40, 0-indexed=39)
            updates[39] = now_str
            
            # Event dates
            if data["conference"].get("start_date"):
                updates[22] = data["conference"]["start_date"]
            if data["conference"].get("end_date"):
                updates[23] = data["conference"]["end_date"]
            
            for col_idx, val in updates.items():
                ws.update_cell(target_row, col_idx + 1, val)
            
            print(f"  📊 Google Sheet ligne {target_row} mise à jour")
        else:
            print(f"  ⚠️ Row not found for {conf_key}")
            
    except Exception as e:
        print(f"  ⚠️ Sheet update skipped: {e}")


def upload_to_drive(conf_key, conf_info):
    """Upload the script and data.json to Google Drive."""
    try:
        from google.oauth2.credentials import Credentials as OAuthCreds
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        token_path = os.path.expanduser("~/.hermes/google_token.json")
        with open(token_path) as f:
            token_data = json.load(f)
        oauth_creds = OAuthCreds.from_authorized_user_info(token_data)
        drive = build('drive', 'v3', credentials=oauth_creds)
        
        FOLDER_ID = "1IQY4Ip1X2ZzsxLn14okVcvMuV0CQGQOQ"
        
        folder_name = conf_info["folder"]
        conf_dir = os.path.join(DATA_DIR, folder_name)
        
        # Upload data.json
        json_path = os.path.join(conf_dir, "data.json")
        if os.path.exists(json_path):
            clean = conf_info["name"].replace(" ", "_").replace(",","").replace("-","_").replace("/","_")
            drive_name = f"{conf_key}_2026_{clean[:40]}.json"
            clean_name_drive = drive_name[:100]
            
            # Delete old version
            results = drive.files().list(
                q=f"'{FOLDER_ID}' in parents and name='{clean_name_drive}' and trashed=false",
                fields="files(id, name)"
            ).execute()
            for existing_file in results.get('files', []):
                drive.files().delete(fileId=existing_file['id']).execute()
            
            media = MediaFileUpload(json_path, mimetype='application/json', resumable=True)
            f = drive.files().create(
                body={'name': clean_name_drive, 'parents': [FOLDER_ID]},
                media_body=media,
                fields='id, name, size'
            ).execute()
            size_kb = int(f.get('size', 0)) // 1024
            print(f"  ☁️  JSON uploadé: {clean_name_drive} ({size_kb} KB)")
        
        # Upload the scraping script
        py_files = [f for f in os.listdir(conf_dir) if f.endswith('.py')]
        if not py_files:
            return
        
        SCRIPTS_FOLDER_ID = "1r1C-IuO5RS6zqSme2ETBE8PK8cy7b1IA"
        for pyf in py_files:
            py_path = os.path.join(conf_dir, pyf)
            drive_name = f"{conf_key}_{pyf}"
            
            results = drive.files().list(
                q=f"'{SCRIPTS_FOLDER_ID}' in parents and name='{drive_name}' and trashed=false",
                fields="files(id, name)"
            ).execute()
            for existing_file in results.get('files', []):
                drive.files().delete(fileId=existing_file['id']).execute()
            
            media = MediaFileUpload(py_path, mimetype='text/x-python', resumable=True)
            f = drive.files().create(
                body={'name': drive_name, 'parents': [SCRIPTS_FOLDER_ID]},
                media_body=media,
                fields='id, name, size'
            ).execute()
            print(f"  ☁️  Script uploadé: {drive_name}")
            
    except Exception as e:
        print(f"  ⚠️ Drive upload skipped (non-fatal): {e}")


def process_conference(conf_key):
    """Process a single conference: load, convert, write, update sheet, upload."""
    conf_info = CONFERENCES_2026.get(conf_key)
    if not conf_info:
        print(f"❌ Unknown conference: {conf_key}")
        return False
    
    folder = conf_info["folder"]
    print(f"\n{'='*60}")
    print(f"🏛️  {conf_info['name']} ({conf_key})")
    print(f"   Dossier: {folder}")
    print(f"{'='*60}")
    
    # Load existing data
    old_data = load_data_json(folder)
    
    if old_data and (old_data.get("sessions") or old_data.get("participants")):
        # Convert existing data to v2
        print(f"   📦 Données existantes: {len(old_data.get('participants', []))} participants, {len(old_data.get('sessions', []))} sessions")
        print(f"   🔄 Conversion vers schéma v2...")
        new_data = convert_to_v2(conf_key, old_data)
    else:
        # Need to create fresh template
        print(f"   ⚠️ Aucune donnée existante — création d'un template vide...")
        new_data = convert_to_v2(conf_key, {
            "conference": conf_info["name"],
            "sessions": [],
            "participants": [],
            "scrape_date": datetime.now().isoformat(),
        })
    
    # Write
    write_data_json(folder, new_data)
    
    # Print summary
    np = len(new_data.get("participants", []))
    ns = len(new_data.get("sessions", []))
    print(f"   📊 Résultat: {np} participants, {ns} sessions")
    
    # Update sheet
    update_google_sheet(conf_key, new_data, conf_info)
    
    # Upload to Drive
    upload_to_drive(conf_key, conf_info)
    
    return True


def status_all():
    """Show status of all conferences."""
    print(f"\n{'='*60}")
    print("📊 STATUS DE TOUTES LES CONFÉRENCES")
    print(f"{'='*60}")
    print(f"{'Short':12s} {'Folder':18s} {'P':>5s} {'S':>5s} {'v2?':6s}")
    print("-"*48)
    
    for key, info in sorted(CONFERENCES_2026.items()):
        folder = info["folder"]
        data = load_data_json(folder)
        if data:
            np = len(data.get("participants", []))
            ns = len(data.get("sessions", []))
            has_v2 = isinstance(data.get("conference"), dict) and "scrape_metadata" in data
            v2_str = "✅" if has_v2 else "🔄"
            print(f"{key:12s} {folder:18s} {np:5d} {ns:5d} {v2_str:6s}")
        else:
            print(f"{key:12s} {folder:18s} {'-':>5s} {'-':>5s} {'❌':6s} (no data)")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 master_pipeline.py <short_name>   — Process one conference")
        print("  python3 master_pipeline.py --status       — Show status")
        print("  python3 master_pipeline.py list           — List all conferences")
        print()
        print("Available conferences:")
        for key in sorted(CONFERENCES_2026.keys()):
            info = CONFERENCES_2026[key]
            print(f"  {key:12s} — {info['name']}")
        return
    
    cmd = sys.argv[1].upper()
    
    if cmd == "--STATUS":
        status_all()
    elif cmd == "LIST":
        print("Available conferences (2026):")
        for key in sorted(CONFERENCES_2026.keys()):
            info = CONFERENCES_2026[key]
            folder = info["folder"]
            has_data = os.path.exists(os.path.join(DATA_DIR, folder, "data.json"))
            marker = "✅" if has_data else " "
            print(f"  {marker} {key:12s} → {folder:18s} — {info['name']}")
    else:
        if cmd not in CONFERENCES_2026:
            print(f"❌ Unknown conference: {cmd}")
            sys.exit(1)
        process_conference(cmd)


if __name__ == "__main__":
    main()
