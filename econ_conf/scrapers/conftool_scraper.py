#!/usr/bin/env python3
"""
Conftool Conference Scraper — extracts sessions, papers, authors, and
institutions from a Conftool conference agenda.

Usage:
    python3 conftool_scraper.py <base_url> [output_dir]

Examples:
    python3 conftool_scraper.py "https://www.conftool.com/efa2026"
    python3 conftool_scraper.py "https://www.conftool.com/efa2026" ~/economics-conferences/efa2026
"""
import re, json, time, urllib.request, urllib.error, sys, os, unicodedata
from collections import OrderedDict, Counter

BASE_URL = "https://www.conftool.com/efa2026"


def fetch(url, retries=3):
    """Fetch URL with retries and rate limiting."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; conftool-scraper)'
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1.5)
                continue
            raise


def get_session_ids_from_day(base_url, form_date):
    """Get all session IDs from a day's overview page."""
    url = f"{base_url}/index.php?page=browseSessions&ismobile=true&form_date={form_date}&mode=list"
    html = fetch(url)
    session_ids = re.findall(r"id='session_(\d+)'", html)
    session_ids2 = re.findall(r'form_session=(\d+)', html)
    return list(OrderedDict.fromkeys(session_ids + session_ids2))


def clean_html(html):
    """Remove HTML tags, decode entities."""
    html = re.sub(r'<br\s*/?>', ' ', html)
    html = re.sub(r'<[^>]+>', '', html)
    html = html.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    html = html.replace('&quot;', '"').replace('&#39;', "'")
    return html.strip()


def clean_institution_name(name):
    """
    Normalize institution name(s): remove affiliation numbers, country
    suffixes, research network suffixes, normalize accents and case.
    Handles semicolon-separated multi-institution strings.
    """
    if not name:
        return ""
    parts = re.split(r';\s*', name)
    cleaned = []
    for part in parts:
        cleaned.append(_clean_single_inst(part))
    return '; '.join(p for p in cleaned if p)


def _clean_single_inst(s):
    """Clean a single institution name string (no semicolons)."""
    if not s:
        return ""
    # 1. Decode HTML entities
    s = s.replace('&amp;', '&').replace('&amp', '&')
    # 2. Remove affiliation number prefix
    s = re.sub(r'^\d+\s*', '', s)
    # 3. Remove research network suffixes
    for pat in [r'\s*and\s+(CEPR|ECGI|NBER|SFI|CESifo|CEP|ABFER|ECB)\s*$',
                r'\s*,\s*(CEPR|ECGI|NBER|SFI)\s*$',
                r'\s*,\s+(CEPR|ECGI|NBER)']:
        s = re.sub(pat, '', s, flags=re.IGNORECASE)
    # 4. Remove country suffixes
    countries = '|'.join([
        'united states of america', 'united states', 'usa', 'united kingdom', 'uk',
        'france', 'germany', 'spain', 'italy', 'switzerland', 'netherlands',
        'china', 'singapore', 'australia', 'sweden', 'denmark', 'belgium',
        'austria', 'norway', 'finland', 'portugal', 'ireland', 'japan', 'india',
        'brazil', 'israel', 'turkey', 'poland', 'mexico', 'canada', 'chile',
        'new zealand', 'luxembourg', 'greece', 'romania', 'hungary', 'russia',
        'south korea', 'korea', 'argentina', 'egypt', 'thailand', 'colombia',
        'peru', 'nigeria', 'vietnam', 'taiwan', 'indonesia', 'malaysia',
        'philippines', 'south africa', 'saudi arabia', 'uae', 'qatar',
        'hong kong', 'czech republic', 'croatia', 'slovenia', 'slovakia',
        'estonia', 'latvia', 'lithuania', 'iceland', 'cyprus', 'malta',
    ])
    s = re.sub(r',\s*(' + countries + r')\s*$', '', s, flags=re.IGNORECASE)
    # 5. Normalize whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    # 6. Normalize accents to ASCII
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    # 7. Title case with acronym preservation
    acronyms = {'MIT', 'NYU', 'UCLA', 'LSE', 'HEC', 'INSEAD', 'CEPR', 'ECGI',
                'NBER', 'SFI', 'ECB', 'BIS', 'IMF', 'LBS', 'UBS', 'KCL', 'UCL',
                'YALE', 'ESSEC', 'KU', 'HK', 'NUS', 'HKUST', 'SAFE', 'BI', 'FGV', 'UIUC'}
    prepositions = {'the', 'a', 'an', 'and', 'of', 'in', 'at', 'for', 'to', 'by',
                    'with', 'on', 'from', 'de', 'la', 'le', 'les', 'des', 'du',
                    'et', 'en', 'das', 'der', 'die', 'von', 'und', 'zu'}
    words = s.split()
    result = []
    for w in words:
        lw = w.lower()
        if w == '&':
            result.append('&')
        elif lw in prepositions:
            result.append(lw)
        elif w.upper() in acronyms:
            result.append(w.upper())
        elif re.match(r'^I{1,3}$', w.upper()) or w.upper() == 'IV':
            result.append(w.upper())
        elif '-' in w and re.match(r'^[A-Za-z]+-[A-Za-z]+$', w):
            parts = w.split('-')
            result.append('-'.join(
                p.upper() if p.upper() in acronyms else p.capitalize() for p in parts
            ))
        else:
            result.append(w.capitalize())
    s = ' '.join(result)
    for old, new in [(' Of ', ' of '), (' And ', ' and '), (' The ', ' the '),
                     (' At ', ' at '), (' For ', ' for '), (' In ', ' in ')]:
        s = s.replace(old, new)
    if s and s[0].islower():
        s = s[0].upper() + s[1:]
    s = s.strip().rstrip(',; ')
    s = re.sub(r'\s+', ' ', s)
    return s


def parse_session_detail(base_url, session_id):
    """Parse a single session detail page and extract papers."""
    url = f"{base_url}/index.php?page=browseSessions&ismobile=true&form_session={session_id}&mode=list"
    html = fetch(url)

    # Session metadata
    title_m = re.search(r"<span class='font11'><b>(.*?)</b></span>", html, re.DOTALL)
    session_title = clean_html(title_m.group(1)) if title_m else "Unknown"

    chair_m = re.search(r"Session Chair:\s*</i></span><span[^>]*><b>(.*?)</b>", html)
    session_chair = clean_html(chair_m.group(1)) if chair_m else ""

    time_m = re.search(r"<b>(\d+:\d+[ap]m - \d+:\d+[ap]m)</b>", html)
    session_time = time_m.group(1).strip() if time_m else ""

    date_m = re.search(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s*(\d+/\w+/\d+)", html)
    session_date = date_m.group(0).strip() if date_m else ""

    loc_m = re.search(r"Location:</i></span> <span[^>]*><b>(.*?)</b>", html)
    session_location = clean_html(loc_m.group(1)) if loc_m else ""

    # Papers
    papers = []
    paper_blocks = re.findall(
        r"<div id='paperID(\d+)'>(.*?)</div>\s*</div>\s*</div>", html, re.DOTALL
    )

    for paper_id_str, paper_html in paper_blocks:
        title_m = re.search(r'<p class="paper_title">(.*?)</p>', paper_html, re.DOTALL)
        paper_title = clean_html(title_m.group(1)) if title_m else ""

        author_m = re.search(r'<p class="paper_author">(.*?)</p>', paper_html, re.DOTALL)
        author_html = author_m.group(1) if author_m else ""

        # Parse authors
        authors = []
        raw_authors = re.findall(r'(<u>.*?</u>|<u>.*?|[^,]+?)(?=$|,\s*)', author_html)
        for raw in raw_authors:
            raw = raw.strip()
            if not raw:
                continue
            is_presenter = '<u>' in raw
            name = re.sub(r'<[^>]+>', '', raw).strip()
            name = re.sub(r'[\d,\s]+$', '', name).strip()  # Remove trailing superscript numbers + commas
            name = re.sub(r'\s+', ' ', name).strip()
            if name and not re.match(r'^[\d\s/;,]+$', name) and len(name) > 1:
                authors.append({"name": name, "is_presenter": is_presenter})

        org_m = re.search(r'<p class="paper_organisation">(.*?)</p>', paper_html, re.DOTALL)
        institution = clean_html(org_m.group(1)) if org_m else ""

        papers.append({
            "paper_id": int(paper_id_str),
            "title": paper_title,
            "authors": authors,
            "institution": institution,
            "institution_clean": clean_institution_name(institution),
        })

    return {
        "session_title": session_title,
        "session_chair": session_chair,
        "session_time": session_time,
        "session_date": session_date,
        "session_location": session_location,
        "papers": papers,
    }


def scrape(base_url, dates=None):
    """
    Scrape a Conftool conference agenda.

    Args:
        base_url: e.g. "https://www.conftool.com/efa2026"
        dates: list of date strings like ["2026-08-19", ...] or None for defaults

    Returns:
        dict with sessions, papers, and participants
    """
    if dates is None:
        dates = ["2026-08-19", "2026-08-20", "2026-08-21", "2026-08-22"]

    print(f"Scanning dates: {', '.join(dates)}")

    all_ids = []
    for day in dates:
        ids = get_session_ids_from_day(base_url, day)
        for sid in ids:
            if sid not in all_ids:
                all_ids.append(sid)
    print(f"{len(all_ids)} session references found")

    all_papers = []
    sessions = []
    for i, sid in enumerate(all_ids):
        try:
            sdata = parse_session_detail(base_url, sid)
            if sdata["papers"]:
                sdata["session_id"] = int(sid)
                sessions.append(sdata)
                all_papers.extend(sdata["papers"])
            if (i + 1) % 10 == 0:
                print(f"  [{i+1}/{len(all_ids)}] ... {len(all_papers)} papers so far")
        except Exception as e:
            print(f"\n  Session {sid}: {e}")
        time.sleep(0.3)

    print(f"\n{len(all_papers)} papers across {len(sessions)} sessions")

    # Build participant index
    participants = {}
    for p in all_papers:
        for a in p["authors"]:
            name = a["name"]
            if name not in participants:
                participants[name] = {
                    "name": name,
                    "institution": p["institution"],
                    "institution_clean": p["institution_clean"],
                    "papers": [],
                    "is_presenter": False,
                }
            participants[name]["papers"].append({
                "paper_id": p["paper_id"],
                "title": p["title"],
                "session": p.get("session_title", ""),
            })
            if a["is_presenter"]:
                participants[name]["is_presenter"] = True

    # Stabilize institutions per participant
    for name, pdata in participants.items():
        insts = [pp["institution"] for pp in all_papers
                 if any(a["name"] == name for a in pp["authors"])]
        insts_clean = [pp["institution_clean"] for pp in all_papers
                       if any(a["name"] == name for a in pp["authors"])]
        if insts:
            pdata["institution"] = Counter(insts).most_common(1)[0][0]
        if insts_clean:
            pdata["institution_clean"] = Counter(insts_clean).most_common(1)[0][0]

    return {
        "conference": os.path.basename(base_url.rstrip("/")).upper() + " Conference",
        "base_url": base_url,
        "total_papers": len(all_papers),
        "total_sessions": len(sessions),
        "total_participants": len(participants),
        "sessions": sessions,
        "participants_by_name": sorted(participants.values(), key=lambda x: x["name"]),
        "papers_flat": all_papers,
    }


# ── Known safe institution merges (variant -> canonical) ──────────
SAFE_MERGES = {
    'The Ohio State University': 'Ohio State University',
    'The University of Hong Kong': 'University of Hong Kong',
    'The University of Texas at Austin': 'University of Texas at Austin',
    'The University of Texas at Dallas': 'University of Texas at Dallas',
    'The University of Manchester, Alliance Business School': 'University of Manchester',
    'University of Texas - Austin': 'University of Texas at Austin',
    'Wharton School of the University of Pennsylvania': 'The Wharton School, University of Pennsylvania',
    'Wharton School, University of Pennsylvania': 'The Wharton School, University of Pennsylvania',
    'The Wharton School, University of Pennsylvania': 'The Wharton School, University of Pennsylvania',
    'Wharton': 'The Wharton School, University of Pennsylvania',
    'The Wharton School': 'The Wharton School, University of Pennsylvania',
    'Wharton School of Business, University of Pennsylvania': 'The Wharton School, University of Pennsylvania',
    'University of Pennsylvania Wharton': 'The Wharton School, University of Pennsylvania',
    'Federal Reserve Board of Governors': 'Federal Reserve Board',
    'Board of Governors of the Federal Reserve': 'Federal Reserve Board',
    'Goethe University': 'Goethe University Frankfurt',
    'University of Notredame': 'University of Notre Dame',
    'University of St.gallen': 'University of St. Gallen',
    'Shanghai Jiaotong University': 'Shanghai Jiao Tong University',
    'University of California, Berkeley': 'University of California Berkeley',
    'University of Colorado - Boulder': 'University of Colorado Boulder',
    'University of Illinois at Urbana-Champaign': 'University of Illinois Urbana-Champaign',
    'University of North Carolina - Chapel Hill': 'University of North Carolina Chapel Hill',
    'London School of Economics and Political Science': 'London School of Economics',
    'Vrije Universiteit Amsterdam, Netherlands, the': 'Vrije Universiteit Amsterdam',
    'Booth School of Business, University of Chicago': 'University of Chicago',
    'University of Chicago Booth School of Business': 'University of Chicago',
    'Kelley School of Business, Indiana University': 'Indiana University',
    'Wisconsin School of Business, University of Wisconsin-Madison': 'University of Wisconsin-Madison',
    'Fisher College of Business, Ohio State University': 'Ohio State University',
    'Mccombs School of Business, University of Texas at Austin': 'University of Texas at Austin',
    'R.h. Smith School of Business, University of Maryland': 'University of Maryland',
    'University of Maryland at College Park': 'University of Maryland',
    'Rotman School of Management, University of Toronto': 'University of Toronto',
    'Sauder School of Business, University of British Columbia': 'University of British Columbia',
    'Foster School of Business, University of Washington': 'University of Washington',
    'Johns Hopkins University, Carey School of Business': 'Johns Hopkins University',
    'Emory University Goizueta Business School': 'Emory University',
    'Stanford Gsb': 'Stanford University',
    'Stanford': 'Stanford University',
    'Uc Berkeley Haas': 'University of California Berkeley',
    'Uc Berkeley': 'University of California Berkeley',
    'University of Michigan, Stephen M. Ross School of Business': 'University of Michigan',
    'University of Lausanne and Swiss Finance Institute': 'University of Lausanne',
    'Swiss Finance Institute, Epfl': 'Swiss Finance Institute',
    'University of Houston, Bauer': 'University of Houston',
    'NBER &': 'NBER', 'Nber': 'NBER',
    'Leibniz Institute for Financial Research SAFE &': 'Leibniz Institute for Financial Research SAFE',
    'Leibniz Institute for Financial Research, SAFE': 'Leibniz Institute for Financial Research SAFE',
    'Frankfurt School of Finance &': 'Frankfurt School of Finance & Management',
    'Frankfurt School of Finance and Management': 'Frankfurt School of Finance & Management',
    'Frankfurt School': 'Frankfurt School of Finance & Management',
    'Bayes Business School (formerly Cass)': 'Bayes Business School',
    'INSEAD and Wharton': 'INSEAD',
    'UIUC Gies': 'UIUC',
    'UCLA': 'University of California Los Angeles',
}


def deduplicate_institutions(data):
    """
    Apply safe institution name merges to clean up duplicates.
    Modifies 'institution_clean' in each paper in-place.
    """
    for p in data["papers_flat" if "papers_flat" in data else "papers"]:
        inst_field = "institution_clean"
        if inst_field not in p:
            continue
        parts = p[inst_field].split("; ")
        result = []
        for part in parts:
            part = part.strip()
            if part in SAFE_MERGES:
                part = SAFE_MERGES[part]
            if part and part not in result:
                result.append(part)
        p[inst_field] = "; ".join(result)
    
    # Rebuild participant index with dedup'd institutions
    # (only if we have participants_by_name)
    if "participants_by_name" in data:
        for pdata in data["participants_by_name"]:
            insts = [pp["institution_clean"] for pp in data["papers_flat"]
                     if any(a["name"] == pdata["name"] for a in pp["authors"])]
            if insts:
                from collections import Counter
                pdata["institution_clean"] = Counter(insts).most_common(1)[0][0]
    
    return data


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    conf_name = os.path.basename(url.rstrip('/'))
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser(f"~/economics-conferences/{conf_name}")

    os.makedirs(outdir, exist_ok=True)
    data = scrape(url)
    data = deduplicate_institutions(data)

    out_json = os.path.join(outdir, "data.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    out_csv = os.path.join(outdir, "participants.csv")
    with open(out_csv, "w", encoding="utf-8") as f:
        f.write("Name,Institution,Papers\n")
        for p in data["participants_by_name"]:
            papers_str = " | ".join(f"{pp['title']} [{pp['session']}]" for pp in p["papers"])
            f.write(f"{p['name']},{p['institution_clean']},\"{papers_str}\"\n")

    print(f"\nOutput: {outdir}/")
    print(f"  data.json          ({len(data['papers_flat'])} papers, {len(data['participants_by_name'])} participants)")
    print(f"  participants.csv")
