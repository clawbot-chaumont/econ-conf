#!/usr/bin/env python3
"""
Scraper for 3CMFI 2026 program from EditorialExpress HTML.
Extracts sessions and papers from the 'Detailed List of Sessions' section.
Outputs data.json in v2 format.

Parses Table 5 of the HTML which contains all session details with
487 rows covering all 35 sessions and 94 papers.
"""

import json
import os
import re
import sys
from bs4 import BeautifulSoup, NavigableString, Tag

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
INPUT_FILE = "/tmp/3cmfi_program.html"
OUTPUT_DIR = os.path.expanduser("~/economics-conferences/3cmfi2026")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "data.json")

# Conference metadata
CONFERENCE = {
    "id": "3cmfi2026",
    "name": "3rd International Conference on the Climate-Macro-Finance Interface",
    "short_name": "3CMFI 2026",
    "year": 2026,
    "month": "March",
    "start_date": "2026-03-23",
    "end_date": "2026-03-24",
    "location": "Frankfurt, Germany",
    "venue": "Goethe University Frankfurt / Leibniz Institute for Financial Research SAFE",
    "url": "https://www.rcea.world/events/forthcoming-events/emerging-economic-policy-challenges-in-an-era-of-policrises",
    "description": "The Third International Conference on the Climate-Macro-Finance Interface (3CMFI), hosted by the Leibniz Institute for Financial Research SAFE and Goethe University Frankfurt.",
    "scraper_version": "v4",
    "total_sessions": 35,
    "total_papers": 94,
}

# Sessions to skip (no papers)
NON_PAPER_KEYWORDS = [
    "REGISTRATION", "WELCOME", "KEYNOTE", "LUNCH", "COFFEE", "COCKTAIL",
    "RECEPTION", "BREAK", "Pay‑as‑you‑go",
    "BUNDESBANK SPECIAL", "ECB SPECIAL",
]

# Sessions from summary table that HAVE papers (paper count > 0)
# Sessions 6-12, 19-31 (paper sessions)
PAPER_SESSION_NUMBERS = set(range(6, 13)) | set(range(19, 32))


def clean_text(text):
    """Clean and normalize text."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ')
    return text.strip()


def is_non_paper_session(session_title):
    """Check if a session title indicates it has no papers."""
    title_upper = session_title.upper().replace('\xa0', ' ')
    for kw in NON_PAPER_KEYWORDS:
        if kw.upper().replace('\xa0', ' ') in title_upper:
            return True
    return False


def parse_session_header(th_tag):
    """Extract session info from a <th> tag with bgcolor='lightgrey'."""
    # Find the inner <a> tag with name attribute (BS4 normalizes to lowercase)
    a_tag = th_tag.find('a', attrs={'name': True})
    if not a_tag:
        return None

    # Get the text of the entire <a> tag
    full_text = a_tag.get_text(separator='\n', strip=True)
    full_text = full_text.replace('\xa0', ' ')

    # Extract session number
    session_num = None
    match = re.search(r'Session\s+(\d+):', full_text)
    if match:
        session_num = int(match.group(1))

    # Extract title from inner <a> (href="#ss_XX")
    title = ""
    inner_a = a_tag.find('a', href=True)
    if inner_a:
        title = clean_text(inner_a.get_text())
    else:
        # Fallback: extract title from text after "Session N: "
        if match:
            after_session = full_text[match.end():]
            title = clean_text(after_session.split('\n')[0])
        else:
            title = clean_text(full_text.split('\n')[0])

    # Extract date/time
    date_time = ""
    dt_match = re.search(r'(March\s+\d+,\s+\d{4}\s+\d+:\d+\s+to\s+\d+:\d+)', full_text)
    if dt_match:
        date_time = dt_match.group(1)

    # Extract location
    location = ""
    loc_match = re.search(r'Location:\s*(.*?)$', full_text)
    if loc_match:
        location = clean_text(loc_match.group(1))

    return {
        "session_number": session_num,
        "title": title,
        "date_time": date_time,
        "location": location,
    }


def extract_paper_title(td_tag):
    """Extract paper title from a <td align=left> containing the title."""
    # Check for <details> (abstract)
    paper_title = ""
    abstract_text = ""
    slides_url = ""

    details = td_tag.find('details')
    if details:
        # Title is everything before <details>
        title_chars = []
        for content in td_tag.contents:
            if isinstance(content, NavigableString):
                title_chars.append(str(content))
            elif isinstance(content, Tag):
                if content.name == 'details':
                    break
                title_chars.append(content.get_text())
        raw_title = ' '.join(title_chars)
        # Split on <br> and take first meaningful part
        parts = raw_title.split('\n')
        paper_title = clean_text(parts[0]) if parts else ""

        # Extract abstract
        summary = details.find('summary')
        if summary:
            summary.extract()
        abstract_text = clean_text(details.get_text(separator=' ', strip=True))
    else:
        # No details - title is the full text
        paper_title = clean_text(td_tag.get_text(separator=' ', strip=True))

    # Check for slides link inside this td
    slides_a = td_tag.find('a', href=lambda h: h and 'download.cgi' in h)
    if slides_a:
        slides_url = slides_a.get('href', '')

    return paper_title, abstract_text, slides_url


def main():
    """Main scraping function."""
    print(f"Reading program from: {INPUT_FILE}")

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find Table 5 - the detailed sessions table (largest table with lightgrey rows)
    all_tables = soup.find_all('table')
    sessions_table = None
    for tbl in all_tables:
        trs = tbl.find_all('tr')
        if len(trs) > 400:  # Table 5 has ~487 rows
            sessions_table = tbl
            break

    if not sessions_table:
        # Fallback: find table with most rows
        sessions_table = max(all_tables, key=lambda t: len(t.find_all('tr')))

    print(f"Using table with {len(sessions_table.find_all('tr'))} rows")

    # Get all tr elements in document order
    all_trs = sessions_table.find_all('tr', recursive=True)

    sessions = []
    current_session = None
    current_paper = None

    i = 0
    while i < len(all_trs):
        tr = all_trs[i]

        # --- SESSION HEADER ---
        if tr.get('bgcolor') == 'lightgrey':
            # Finalize any pending paper
            if current_paper is not None and current_session is not None:
                if current_paper['title'] and current_paper not in current_session['papers']:
                    current_session['papers'].append(current_paper)
                current_paper = None

            # Save the previous session if we have one
            if current_session:
                sessions.append(current_session)

            th_tag = tr.find('th', align='left')
            if th_tag:
                session_info = parse_session_header(th_tag)
                if session_info and session_info['session_number'] is not None:
                    title = session_info['title']
                    snum = session_info['session_number']

                    if not is_non_paper_session(title):
                        current_session = {
                            "session_number": snum,
                            "title": title,
                            "date_time": session_info['date_time'],
                            "location": session_info['location'],
                            "papers": [],
                        }
                    else:
                        current_session = None
                else:
                    current_session = None
            else:
                current_session = None

            i += 1
            continue

        # --- PROCESS PAPER ROWS (only if we have a current session) ---
        if current_session is None:
            i += 1
            continue

        # Get td align=left from this tr
        td = tr.find('td', align='left')
        if td is None:
            i += 1
            continue

        td_text = td.get_text(separator=' ', strip=True)
        td_text = td_text.replace('\xa0', ' ').strip()

        # --- SPACER ROW (<p>) ---
        p_tag = td.find('p')
        if p_tag and (not td_text or td_text.strip() in ['', ' ']):
            i += 1
            continue

        # --- SLIDES-ONLY ROW (standalone slides link) ---
        slides_a = td.find('a', href=lambda h: h and 'download.cgi' in h)
        if slides_a and (not td_text.strip() or td_text.strip() == '[slides]'):
            if current_paper is not None:
                current_paper['slides_url'] = slides_a.get('href', '')
            i += 1
            continue

        # --- PAPER TITLE ROW ---
        # Not a spacer, not a "By" line, not a "Presented by" line, not a slides-only row
        if not td_text.startswith('By ') and not td_text.startswith('Presented by:'):
            paper_title, abstract_text, slides_url = extract_paper_title(td)

            if paper_title:
                # Finalize previous paper if it's incomplete (no presenter yet but we found new title)
                # This handles edge cases
                if current_paper is not None:
                    if current_paper['title'] and current_paper not in current_session['papers']:
                        current_session['papers'].append(current_paper)

                current_paper = {
                    "title": paper_title,
                    "authors": [],
                    "presenter": "",
                    "abstract": abstract_text,
                }
                if slides_url:
                    current_paper["slides_url"] = slides_url

            i += 1
            continue

        # --- "By" LINE ---
        if td_text.startswith('By '):
            if current_paper is not None:
                # Get text preserving <br> separators for multi-author entries
                td_text_raw = td.get_text(separator='\n', strip=True)
                # Split by newlines (from <br> tags)
                author_lines = [l.strip() for l in td_text_raw.split('\n') if l.strip()]
                for line in author_lines:
                    # Remove "By " or "&nbsp;&nbsp;&nbsp;By " prefix
                    line = re.sub(r'^(By\s+|\s+)', '', line).strip()
                    line = line.replace('\xa0', ' ').strip()
                    if line and line not in current_paper['authors']:
                        current_paper['authors'].append(line)

            i += 1
            continue

        # --- "Presented by" LINE ---
        if td_text.startswith('Presented by:'):
            if current_paper is not None:
                pres = td_text[len('Presented by:'):].strip()
                pres = pres.replace('\xa0', ' ').strip()
                # Clean up: remove extra space before comma (from <a> tag separation)
                pres = re.sub(r'\s+,', ',', pres)
                pres = clean_text(pres)
                if pres:
                    current_paper['presenter'] = pres

                # Finalize paper and add to session
                if current_paper['title'] and current_paper not in current_session['papers']:
                    current_session['papers'].append(current_paper)
                current_paper = None

            i += 1
            continue

        # --- SLIDES LINK ROW (standalone) ---
        slides_a = td.find('a', href=lambda h: h and 'download.cgi' in h)
        if slides_a and current_paper:
            current_paper['slides_url'] = slides_a.get('href', '')
            i += 1
            continue

        # --- ANYTHING ELSE ---
        i += 1

    # Don't forget the last session
    if current_session:
        # Finalize any pending paper
        if current_paper is not None:
            if current_paper['title'] and current_paper not in current_session['papers']:
                current_session['papers'].append(current_paper)
            current_paper = None
        sessions.append(current_session)

    # Debug: print what we found
    print(f"\nTotal sessions extracted: {len(sessions)}")
    total_papers = sum(len(s['papers']) for s in sessions)
    print(f"Total papers extracted: {total_papers}")

    for s in sessions:
        print(f"  Session {s['session_number']:2d}: {s['title'][:70]:70s} ({len(s['papers'])} papers)")

    # Build output
    output = {
        "conference": CONFERENCE,
        "sessions": sessions,
    }
    output['conference']['extracted_papers'] = total_papers

    # Write output
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nOutput saved to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
