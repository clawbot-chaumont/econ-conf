#!/usr/bin/env python3
"""
Scraper for RCEA 2026 conference program from EditorialExpress.
Produces data.json v2 format with sessions, papers, and participants.
"""

import json
import os
import re
import urllib.request
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────────────────

CONFERENCE = {
    "title": "RCEA International Conference in Economics, Econometrics, and Finance",
    "short_name": "RCEA 2026",
    "year": 2026,
    "start_date": "2026-05-25",
    "end_date": "2026-05-27",
    "location": "Madrid, Spain",
}

URL = "http://editorialexpress.com/conference/202_RCEA_ICEEF/program/202_RCEA_ICEEF.html"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "data.json")


# ── HTML Fetching ──────────────────────────────────────────────────────────

def fetch_html(url: str) -> str:
    """Download the HTML page with a reasonable User-Agent."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return raw


# ── Parsing helpers ────────────────────────────────────────────────────────

def strip_html_tags(text: str) -> str:
    """Remove HTML tags from a string, collapsing whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_session_header(header_html: str) -> dict:
    """
    Parse a session header like:
      <a NAME="6">Session 5: <a href="#ss_6">CLIMATE AND ENERGY FINANCE CONFERENCE 1</a>
      <br>May 25, 2026 10:30 to 12:30<br>Location: Polavieja</a>

    Returns dict with session_number, title, date, time_start, time_end, location.
    """
    # Extract full text
    full_text = strip_html_tags(header_html)

    # Session number
    session_num = None
    m = re.search(r"Session\s+(\d+):", full_text)
    if m:
        session_num = int(m.group(1))

    # Date and times
    date_str = None
    time_start = None
    time_end = None
    # Pattern: "May 25, 2026 10:30 to 12:30"
    m = re.search(
        r"([A-Z][a-z]+ \d{1,2}, \d{4})\s+(\d{1,2}:\d{2})\s+to\s+(\d{1,2}:\d{2})",
        full_text,
    )
    if m:
        date_str = m.group(1)
        time_start = m.group(2)
        time_end = m.group(3)
        # Normalize date to ISO
        try:
            dt = datetime.strptime(date_str, "%B %d, %Y")
            date_iso = dt.strftime("%Y-%m-%d")
        except ValueError:
            date_iso = date_str
    else:
        date_iso = None

    # Location
    location = None
    m = re.search(r"Location:\s*(.+?)$", full_text)
    if m:
        location = m.group(1).strip()

    # Title — extract from inside <a href="#ss_...">...</a>
    title = None
    m = re.search(r'<a href="#ss_\d+">(.*?)</a>', header_html, re.DOTALL)
    if m:
        title = strip_html_tags(m.group(1))
    else:
        # Fallback: after "Session N: "
        m = re.search(r"Session\s+\d+:\s*(.+)", full_text)
        if m:
            title = m.group(1).strip()
            # Remove trailing date/time/location info
            for pattern in [r"\s+May\s+\d+.*", r"\s+Location:.*"]:
                title = re.sub(pattern, "", title).strip()

    return {
        "session_number": session_num,
        "title": title,
        "date": date_iso,
        "time_start": time_start,
        "time_end": time_end,
        "location": location,
    }


def parse_presenter_info(presenter_html: str) -> dict:
    """Parse a 'Presented by:' line into name, email, institution."""
    text = strip_html_tags(presenter_html)
    # Remove the "Presented by:" prefix
    text = re.sub(r"^Presented\s+by:\s*", "", text).strip()

    # Try to get email from the <a> tag
    email = None
    m = re.search(r'href="mailto:([^"]+)"', presenter_html)
    if m:
        email = m.group(1)

    # Try to get name from the <a> tag content
    name = None
    m = re.search(r'<a[^>]*>(.*?)</a>', presenter_html)
    if m:
        name = strip_html_tags(m.group(1))

    # Institution: everything after the last comma or after the </a> tag
    institution = None
    if name:
        # After the </a>, there's typically ", Institution"
        after_link = re.split(r"</a>", presenter_html, maxsplit=1)
        if len(after_link) > 1:
            inst_text = strip_html_tags(after_link[1])
            inst_text = re.sub(r"^[,;\s]+", "", inst_text)
            # Remove trailing garbage
            inst_text = re.sub(r"\s+$", "", inst_text)
            if inst_text:
                institution = inst_text

    # If name not found in <a>, use the full text before comma
    if not name:
        parts = text.split(",")
        if parts:
            name = parts[0].strip()

    return {
        "name": name or text,
        "email": email,
        "institution": institution,
    }


def parse_session_chair(chair_html: str) -> dict | None:
    """Parse a 'Session Chair:' line into name, email, institution."""
    text = strip_html_tags(chair_html)
    text = re.sub(r"^Session\s+Chair:\s*", "", text).strip()
    if not text:
        return None

    email = None
    m = re.search(r'href="mailto:([^"]+)"', chair_html)
    if m:
        email = m.group(1)

    name = None
    m = re.search(r'<a[^>]*>(.*?)</a>', chair_html)
    if m:
        name = strip_html_tags(m.group(1))

    institution = None
    if name:
        after_link = re.split(r"</a>", chair_html, maxsplit=1)
        if len(after_link) > 1:
            inst_text = strip_html_tags(after_link[1])
            inst_text = re.sub(r"^[,;\s]+", "", inst_text)
            inst_text = re.sub(r"\s+$", "", inst_text)
            if inst_text:
                institution = inst_text

    if not name:
        name = text

    return {
        "name": name,
        "email": email,
        "institution": institution,
    }


# ── Main Parsing ───────────────────────────────────────────────────────────

def parse_program(html: str) -> dict:
    """
    Parse the full RCEA program HTML.

    The 'Detailed List of Sessions' section contains:
    - <tr bgcolor="lightgrey"> for session headers
    - <tr><td align=left> for session chair, paper titles, presenters
    """
    # Locate the Detailed List of Sessions section
    detail_marker = "Detailed List of Sessions"
    idx = html.find(detail_marker)
    if idx < 0:
        raise ValueError("Could not find 'Detailed List of Sessions' in HTML")

    detail_section = html[idx:]

    sessions = []
    participants = {}  # email -> participant info (deduplicated)
    paper_counter = 0

    # Split by session headers (bgcolor="lightgrey")
    session_blocks = re.split(
        r'(<tr bgcolor="lightgrey"><th align=left>.*?</th></tr>)',
        detail_section,
        flags=re.DOTALL,
    )

    # The split gives [before_first_session, header1, content1, header2, content2, ...]
    current_session = None
    current_session_html = ""  # raw HTML for the current session block

    for i, block in enumerate(session_blocks):
        if block.startswith('<tr bgcolor="lightgrey"'):
            # This is a session header — save previous session if any
            if current_session is not None:
                parsed = finalize_session(
                    current_session, current_session_html
                )
                if parsed:
                    sessions.append(parsed)
                    # Track participants
                    for paper in parsed.get("papers", []):
                        for pres in paper.get("presenters", []):
                            email = pres.get("email")
                            if email:
                                key = email.lower().strip()
                                if key not in participants:
                                    participants[key] = {
                                        "name": pres["name"],
                                        "email": email,
                                        "institution": pres.get("institution"),
                                    }
                            else:
                                # Use name+institution as key
                                key = f"{pres.get('name','')}|{pres.get('institution','')}"
                                if key not in participants:
                                    participants[key] = {
                                        "name": pres["name"],
                                        "email": None,
                                        "institution": pres.get("institution"),
                                    }

            # Parse new session header
            header_info = parse_session_header(block)
            current_session = header_info
            current_session_html = ""

        elif current_session is not None:
            # Content belongs to current session
            current_session_html += block

    # Don't forget the last session
    if current_session is not None:
        parsed = finalize_session(current_session, current_session_html)
        if parsed:
            sessions.append(parsed)
            for paper in parsed.get("papers", []):
                for pres in paper.get("presenters", []):
                    email = pres.get("email")
                    if email:
                        key = email.lower().strip()
                        if key not in participants:
                            participants[key] = {
                                "name": pres["name"],
                                "email": email,
                                "institution": pres.get("institution"),
                            }
                    else:
                        key = f"{pres.get('name','')}|{pres.get('institution','')}"
                        if key not in participants:
                            participants[key] = {
                                "name": pres["name"],
                                "email": None,
                                "institution": pres.get("institution"),
                            }

    # Sort participants list
    participants_list = sorted(participants.values(), key=lambda p: p["name"].lower())

    return {
        "conference": CONFERENCE,
        "sessions": sessions,
        "participants": participants_list,
    }


def finalize_session(session_info: dict, content_html: str) -> dict | None:
    """
    Extract papers and chair from a session's content block.
    """
    if session_info is None:
        return None

    # Extract session chair
    chair = None
    chair_m = re.search(
        r'<tr><td align=left>\s*Session Chair:\s*(.*?)</td></tr>',
        content_html,
        re.DOTALL,
    )
    if chair_m:
        chair = parse_session_chair(chair_m.group(1))

    # Extract papers
    papers = []
    # Split content by <tr><td align=left>&nbsp;<p></td> as paper separators
    paper_blocks = re.split(
        r'<tr><td align=left>\s*&nbsp;<p>\s*</td>',
        content_html,
        flags=re.DOTALL,
    )

    for block in paper_blocks:
        # Each paper block should have a title and optionally a presenter line
        block = block.strip()
        if not block:
            continue

        # Skip the session chair block explicitly
        if "Session Chair:" in block:
            continue

        # Find title and presenter
        # Title is in: <tr><td align=left>TITLE</td>
        # Presenter is in: <tr><td align=left>&nbsp;&nbsp;&nbsp;Presented by: ...
        title_m = re.search(
            r'<tr><td align=left>(.*?)</td>',
            block,
            re.DOTALL,
        )
        if not title_m:
            continue

        title_html = title_m.group(1).strip()
        title = strip_html_tags(title_html)

        # Skip empty titles or separator-like content
        if not title or title == "&nbsp;" or title == "\xa0" or title == " ":
            continue

        # Skip "Session Chair:" rows that weren't caught above
        if title.startswith("Session Chair:"):
            continue

        # Find presenter
        presenter_m = re.search(
            r'<tr><td align=left>\s*&nbsp;&nbsp;&nbsp;Presented by:\s*(.*?)</td>',
            block,
            re.DOTALL,
        )
        presenters = []
        if presenter_m:
            presenter_info = parse_presenter_info(presenter_m.group(1))
            presenters.append(presenter_info)

        paper_entry = {
            "id": f"P{len(papers) + 1}",
            "title": title,
            "presenters": presenters,
        }
        papers.append(paper_entry)

    return {
        "id": f"S{session_info.get('session_number', '')}",
        "session_number": session_info.get("session_number"),
        "title": session_info.get("title"),
        "date": session_info.get("date"),
        "time_start": session_info.get("time_start"),
        "time_end": session_info.get("time_end"),
        "location": session_info.get("location"),
        "chair": chair,
        "papers": papers,
    }


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print(f"Fetching {URL} ...")
    html = fetch_html(URL)
    print(f"Downloaded {len(html)} bytes")

    print("Parsing program ...")
    data = parse_program(html)

    print(f"  Sessions: {len(data['sessions'])}")
    total_papers = sum(len(s.get("papers", [])) for s in data["sessions"])
    print(f"  Papers:   {total_papers}")
    print(f"  Participants: {len(data['participants'])}")

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nOutput written to {OUTPUT_FILE}")

    # Summary stats
    sessions_with_papers = sum(1 for s in data["sessions"] if s.get("papers"))
    print(f"\nSessions with papers: {sessions_with_papers}")
    print(f"Sessions without papers: {len(data['sessions']) - sessions_with_papers}")

    # Show sample session
    for s in data["sessions"]:
        if s.get("papers"):
            print(f"\nSample session: #{s['session_number']} - {s['title']}")
            print(f"  Chair: {s['chair']['name'] if s.get('chair') else 'N/A'}")
            print(f"  Papers ({len(s['papers'])}):")
            for p in s["papers"][:3]:
                for pres in p["presenters"]:
                    print(f"    - {p['title']}")
                    print(f"      by {pres['name']} ({pres['institution']})")
            if len(s["papers"]) > 3:
                print(f"      ... and {len(s['papers'])-3} more")
            break


if __name__ == "__main__":
    main()
