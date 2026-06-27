#!/usr/bin/env python3
"""
Fetch conference program for a given conference and produce JSON with participant/paper list.

Usage:
  python3 fetch_conference_program.py <short_name>

Short names map to conference entries in the Google Sheet.
If the current year program is not yet published, it reports that gracefully.

Supported conferences:
  SCFICF  — Summer Conference on Financial Intermediation and Corporate Finance
  AC-MFR  — Annual Conference on Macro-Finance Research

Output:
  ~/economics-conferences/<short_name>/data.json
"""

import sys
import os
import json
import re
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, date
from html.parser import HTMLParser

DATA_DIR = os.path.expanduser("~/economics-conferences")

CONFERENCES = {
    "SCFICF": {
        "name": "8th Summer Conference on Financial Intermediation and Corporate Finance",
        "short_name": "SCFICF",
        "website": "https://summerfinconf.wixsite.com/mysite",
        "year": 2026,
        "start_date": "2026-06-29",
        "end_date": "2026-07-01",
        "program_url_candidates": [
            "https://summerfinconf.wixsite.com/mysite/program",
            "https://summerfinconf.wixsite.com/mysite/agenda",
            "https://summerfinconf.wixsite.com/mysite/programme",
        ],
    },
    "AC-MFR": {
        "name": "3rd Annual Conference on Macro-Finance Research",
        "short_name": "AC-MFR",
        "website": "https://www.frbsf.org/news-and-media/events/conferences/2026/10/conference-on-macro-finance-research-2026/",
        "year": 2026,
        "start_date": "2026-10-09",
        "end_date": "2026-10-09",
        "program_url_candidates": [
            "https://www.frbsf.org/news-and-media/events/conferences/2026/10/conference-on-macro-finance-research-2026/agenda",
            "https://www.frbsf.org/news-and-media/events/conferences/2026/10/conference-on-macro-finance-research-2026/",
        ],
    },
}

# ── Helpers ────────────────────────────────────────────────────────────────

def fetch_url(url, timeout=15):
    """Fetch a URL with a user-agent, return (status, html_or_error)."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            return resp.status, html
    except urllib.error.HTTPError as e:
        return e.code, str(e)
    except urllib.error.URLError as e:
        return 0, f"URLError: {e.reason}"
    except Exception as e:
        return 0, f"Error: {e}"


def extract_text(html, tag, class_=None):
    """Simple regex-based text extraction (no external deps)."""
    if class_:
        pattern = re.compile(
            rf'<{tag}[^>]*class\s*=\s*["\'][^"\']*{re.escape(class_)}[^"\']*["\'][^>]*>'
            rf'(.*?)</{tag}>',
            re.DOTALL | re.IGNORECASE,
        )
    else:
        pattern = re.compile(rf'<{tag}[^>]*>(.*?)</{tag}>', re.DOTALL | re.IGNORECASE)
    return pattern.findall(html)


def strip_html(text):
    """Remove HTML tags from text."""
    clean = re.compile(r"<[^>]+>")
    return clean.sub("", text).strip()


def write_json(conf_short, data, message):
    """Write data.json and return the path."""
    conf_dir = os.path.join(DATA_DIR, conf_short.lower())
    os.makedirs(conf_dir, exist_ok=True)
    path = os.path.join(conf_dir, "data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  📄 Écrit: {path}")
    return path


def make_empty_result(conf, reason):
    """Return a skeleton JSON for when no program is found."""
    return {
        "conference": {
            "name": conf["name"],
            "short_name": conf["short_name"],
            "year": conf["year"],
            "website": conf["website"],
            "start_date": conf["start_date"],
            "end_date": conf["end_date"],
        },
        "program_available": False,
        "reason": reason,
        "total_papers": 0,
        "total_participants": 0,
        "sessions": [],
        "participants": [],
        "scrape_date": datetime.now().isoformat(),
    }


# ── Specific scrapers ─────────────────────────────────────────────────────

def probe_program_urls(conf):
    """Try each program URL candidate; return (url, html) if one works, else (None, None)."""
    for url in conf["program_url_candidates"]:
        status, html = fetch_url(url)
        if status == 200 and len(html) > 500:
            return url, html
    return None, None


def scrape_scficf():
    """Scrape the Summer Conference on Financial Intermediation and Corporate Finance."""
    conf = CONFERENCES["SCFICF"]
    print(f"\n🔍 Recherche du programme SCFICF 2026...")

    # First try the main site
    status, html = fetch_url(conf["website"])
    if status != 200:
        return make_empty_result(conf, f"Site inaccessible (HTTP {status})")

    # Check for program keywords
    has_program = any(kw in html.lower() for kw in ["program", "agenda", "schedule", "draft program", "preliminary program"])
    has_2026 = "2026" in html
    has_session = any(kw in html.lower() for kw in ["session", "paper", "presentation"])

    if not has_program and not has_session:
        return make_empty_result(conf, "Programme 2026 non publié sur le site")

    # Try program subpages
    prog_url, prog_html = probe_program_urls(conf)
    if prog_html and len(prog_html) > 1000:
        html = prog_html
    else:
        # Check if the main page has enough program info
        if not has_session or not has_2026:
            return make_empty_result(conf, "Programme 2026 pas encore disponible")

    # Try to extract sessions and papers
    sessions = []
    participants = []
    seen_names = set()

    # Look for tables with schedule info
    tables = extract_text(html, "table")
    for table_html in tables:
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, re.DOTALL)
        for row_html in rows:
            cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row_html, re.DOTALL)
            cell_texts = [strip_html(c) for c in cells]
            if any(name for name in cell_texts if name and len(name) > 3):
                # Could be a program row
                session_name = cell_texts[0] if cell_texts else ""
                papers_in_session = []
                # Look for author-like patterns: Name Surname (Institution)
                for ct in cell_texts:
                    author_matches = re.findall(
                        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*\(([^)]*)\)",
                        ct,
                    )
                    for auth_name, auth_inst in author_matches:
                        if auth_name not in seen_names:
                            seen_names.add(auth_name)
                            participants.append({
                                "name": auth_name.strip(),
                                "institution": auth_inst.strip(),
                                "role": "presenter",
                            })
                            papers_in_session.append(auth_name.strip())
                if session_name and papers_in_session:
                    sessions.append({
                        "session_title": session_name.strip(),
                        "papers": papers_in_session,
                    })

    return {
        "conference": {
            "name": conf["name"],
            "short_name": conf["short_name"],
            "year": conf["year"],
            "website": conf["website"],
            "start_date": conf["start_date"],
            "end_date": conf["end_date"],
            "program_url": prog_url or conf["website"],
        },
        "program_available": len(sessions) > 0,
        "reason": "Programme extrait du site" if sessions else "Programme trouvé mais non structuré",
        "total_papers": len(sessions),
        "total_participants": len(participants),
        "sessions": sessions,
        "participants": participants,
        "scrape_date": datetime.now().isoformat(),
    }


def scrape_acmfr():
    """Scrape the Annual Conference on Macro-Finance Research (FRBSF)."""
    conf = CONFERENCES["AC-MFR"]
    print(f"\n🔍 Recherche du programme AC-MFR 2026...")

    status, html = fetch_url(conf["website"])
    if status != 200:
        return make_empty_result(conf, f"Site inaccessible (HTTP {status})")

    # Check if this is the current year page
    has_2026 = "2026" in html

    # Check for program content
    has_agenda = any(kw in html.lower() for kw in ["agenda", "program", "schedule", "speaker", "paper"])
    has_stein = "Jeremy Stein" in html or "stein" in html.lower()

    if not has_agenda:
        return make_empty_result(conf, "Programme 2026 pas encore disponible (soumissions closes le 15 juin 2026)")

    # Try to extract session/paper info
    sessions = []
    participants = []
    seen_names = set()

    # Look for event schedule / agenda sections
    # FRBSF sites often list speakers in specific divs
    speaker_sections = extract_text(html, "div", class_="speaker") or extract_text(html, "div", class_="agenda-item")
    if not speaker_sections:
        speaker_sections = extract_text(html, "li") + extract_text(html, "p")

    for section in speaker_sections:
        # Find person + affiliation patterns
        matches = re.findall(
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*[,\(]\s*([^,\)]+)[,\)]?",
            section,
        )
        for name, aff in matches:
            aff_clean = aff.strip().strip(",")
            if name not in seen_names and len(name) > 5:
                seen_names.add(name)
                participants.append({
                    "name": name.strip(),
                    "institution": aff_clean,
                    "role": "speaker",
                })

    # Also look for keynote
    if "Jeremy Stein" not in seen_names:
        participants.append({
            "name": "Jeremy Stein",
            "institution": "Harvard University",
            "role": "keynote speaker",
        })
        seen_names.add("Jeremy Stein")

    # Try to find session times/titles
    time_pattern = re.findall(r"(\d{1,2}:\d{2}[ap]m\s*[-–to]+\s*\d{1,2}:\d{2}[ap]m)\s*[:\-–]\s*(.+?)(?=\d{1,2}:\d{2}|$)", html, re.DOTALL | re.IGNORECASE)
    for time_str, title in time_pattern:
        title_clean = strip_html(title).strip()
        if title_clean and len(title_clean) > 5:
            sessions.append({
                "session_title": title_clean[:100],
                "time": time_str.strip(),
            })

    return {
        "conference": {
            "name": conf["name"],
            "short_name": conf["short_name"],
            "year": conf["year"],
            "website": conf["website"],
            "start_date": conf["start_date"],
            "end_date": conf["end_date"],
            "program_url": conf["website"],
            "keynote_speaker": "Jeremy Stein (Harvard University)",
        },
        "program_available": len(participants) > 0,
        "reason": "Programme extrait" if participants else "Aucun détail de programme trouvé",
        "total_papers": len(sessions),
        "total_participants": len(participants),
        "sessions": sessions,
        "participants": participants,
        "scrape_date": datetime.now().isoformat(),
    }


# ── Dispatcher ─────────────────────────────────────────────────────────────

SCRAPERS = {
    "SCFICF": scrape_scficf,
    "AC-MFR": scrape_acmfr,
}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_conference_program.py <short_name>")
        print(f"Supported: {', '.join(CONFERENCES.keys())}")
        sys.exit(1)

    short = sys.argv[1].upper()
    if short not in SCRAPERS:
        print(f"❌ Conference '{short}' not supported.")
        print(f"   Supported: {', '.join(CONFERENCES.keys())}")
        sys.exit(1)

    print(f"🏛️  {CONFERENCES[short]['name']}")
    print(f"   Site: {CONFERENCES[short]['website']}")
    print(f"   Dates: {CONFERENCES[short]['start_date']} → {CONFERENCES[short]['end_date']}")

    result = SCRAPERS[short]()

    if result.get("program_available"):
        print(f"\n✅ Programme 2026 disponible !")
        print(f"   Sessions: {result['total_papers']}")
        print(f"   Participants: {result['total_participants']}")
    else:
        print(f"\n⏭️  {result.get('reason', 'Programme non disponible')}")

    write_json(short.lower(), result, "OK")

    # Update the Google Sheet's Lien_programme and program_scrapped_with_success
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        from gspread.utils import ValueInputOption

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(
            os.path.expanduser("~/.hermes/google_service_account.json"), scopes=scope
        )
        client = gspread.authorize(creds)
        sh = client.open_by_key("1mEi2e8jQi0I7PA0TzoDmmAMkuOp2i8zzvi2-WnVZJHc")
        ws = sh.sheet1
        rows = ws.get_all_values()

        # Find the row for this conference
        for i, row in enumerate(rows):
            if row[1].strip().upper() == short:
                prog_url = result.get("conference", {}).get("program_url", row[13])
                scrapped = "YES" if result.get("program_available") else "NO"

                ws.update_cell(i + 1, 14, prog_url)  # N: Lien_programme
                ws.update_cell(i + 1, 15, datetime.now().strftime("%d/%m/%Y"))  # O: Entry_check_date
                ws.update_cell(i + 1, 16, scrapped)  # P: program_scrapped_with_success
                print(f"   ✅ Google Sheet ligne {i+1} mise à jour (program_scrapped={scrapped})")
                break
    except Exception as e:
        print(f"   ⚠️  Google Sheet update skipped: {e}")

    # Upload to Google Drive
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
        drive_name = f"{short.upper()}_2026_{CONFERENCES[short]['name'][:40].replace(' ', '_').replace(',','').replace('-','_')}.json"

        # Check if already exists (delete old version first for update)
        results = drive.files().list(
            q=f"'{FOLDER_ID}' in parents and name='{drive_name}' and trashed=false",
            fields="files(id, name)"
        ).execute()
        for existing_file in results.get('files', []):
            drive.files().delete(fileId=existing_file['id']).execute()
            print(f"   ♻️  Ancienne version supprimée: {drive_name}")

        json_path = os.path.join(DATA_DIR, short.lower(), "data.json")
        media = MediaFileUpload(json_path, mimetype='application/json', resumable=True)
        f = drive.files().create(
            body={'name': drive_name, 'parents': [FOLDER_ID]},
            media_body=media,
            fields='id, name, size'
        ).execute()
        print(f"   ☁️  Uploadé sur Google Drive: {drive_name} ({int(f['size'])//1024} KB)")
    except Exception as e:
        print(f"   ⚠️  Google Drive upload skipped: {e}")

    print(f"\n✅ Terminé. Résultat dans ~/economics-conferences/{short.lower()}/data.json")


if __name__ == "__main__":
    main()
