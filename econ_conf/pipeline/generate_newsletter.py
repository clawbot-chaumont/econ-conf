#!/usr/bin/env python3
"""
Central Bank Research Pulse — Newsletter Generator
===================================================
Generates the bi-weekly newsletter by:
  1. Loading working papers from the scraper JSON (or running the scraper)
  2. Loading conference data from ~/economics-conferences/*/data.json
  3. Searching for CfP deadlines
  4. Composing the email body
  5. Sending via Gmail

Usage:
  python3 generate_newsletter.py                          # Run with existing data
  python3 generate_newsletter.py --scrape                 # Re-run scraper first
  python3 generate_newsletter.py --send --to email@ecb    # Send to a specific address
"""

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
DATA_DIR = os.path.expanduser("~/economics-conferences")
SCRAPER = os.path.join(DATA_DIR, "pipeline", "working_papers_scraper.py")
OUTPUT_FILE = "/tmp/working_papers_output.json"
NEWSLETTER_FILE = "/tmp/newsletter_body.txt"
HERMES_HOME = os.environ.get("HERMES_HOME", "/usr/local/lib/hermes-agent")
GMAIL_SCRIPT = os.path.join(HERMES_HOME, "skills/productivity/google-workspace/scripts/google_api.py")
DRIVE_FOLDER = "1IQY4Ip1X2ZzsxLn14okVcvMuV0CQGQOQ"  # Conferences_hermes_agent

TODAY = datetime.now(timezone.utc)
TODAY_STR = TODAY.strftime("%Y-%m-%d")
CUTOFF_STR = (TODAY - timedelta(days=14)).strftime("%Y-%m-%d")

# ── Conference metadata (name, website, scraper type) ──────────────────────
# Extracted from master_pipeline.py + manual lookups
CONFERENCE_INFO = {
    "afse2026": {
        "name": "AFSE 2026 — 74e Congrès de l'Association Française de Sciences Économiques",
        "website": "https://afse2026.sciencesconf.org",
        "location": "Paris, France",
    },
    "irmc2026": {
        "name": "IRMC 2026 — International Risk Management Conference",
        "website": "https://www.therisksociety.com/irmc",
        "location": "International",
    },
    "bdpcepr2026": {
        "name": "Banco de Portugal & CEPR Conference on Financial Intermediation",
        "website": "https://cepr.org/events/banco-de-portugal-and-cepr-conference-financial-intermediation-2026",
        "location": "Ponta Delgada, Açores, Portugal",
    },
    "gdre2026": {
        "name": "GDRE — Symposium on Money, Banking and Finance",
        "website": "https://gdre2026.sciencesconf.org",
        "location": "France",
    },
    "wfa2026": {
        "name": "Western Finance Association Annual Meeting",
        "website": "https://westernfinance.org/conference-2026/",
        "location": "Denver, CO, USA",
    },
    "wciea2026": {
        "name": "21st World Congress of the International Economic Association",
        "website": "https://www.iea-world.org",
        "location": "Belgrade, Serbie",
    },
    "iaae2026": {
        "name": "IAAE 2026 — International Association for Applied Econometrics",
        "website": "https://iaae2026.org",
        "location": "Carcavelos, Lisbonne, Portugal",
    },
    "mprc2026": {
        "name": "ECB/IMF Macroprudential Policy and Research Conference",
        "website": "https://www.ecb.europa.eu/press/conferences/html/index.en.html",
        "location": "Francfort, Allemagne",
    },
    "weai2026": {
        "name": "WEAI 2026 — Western Economics Association International",
        "website": "https://weai.org/conferences",
        "location": "USA",
    },
    "scficf": {
        "name": "SCFICF — Summer Conference on Financial Intermediation and Corporate Finance",
        "website": "https://summerfinconf.wixsite.com/mysite",
        "location": "International",
    },
}

# ── CfP metadata ────────────────────────────────────────────────────────────
CALLS_FOR_PAPERS = [
    {
        "deadline": "15 juin",
        "conference": "ECB Conference on Financial Stability and Macroprudential Policy",
        "date": "2–3 décembre 2026",
        "location": "Francfort, Allemagne",
        "url": "https://www.ecb.europa.eu/press/conferences/html/20261202_financial_stability.en.html",
        "details": "Soumission PDF à MacropruConference@ecb.europa.eu",
    },
    {
        "deadline": "21 juin",
        "conference": "National Bank of Ukraine / NBP — Central Banks Response to Future Challenges",
        "date": "21–22 septembre 2026",
        "location": "Kyiv, Ukraine (hybride)",
        "url": "https://cepr.org/events/call-papers-central-banks-response-future-challenges-resilience-credibility-and-innovation",
        "details": "Résilience, crédibilité et innovation",
    },
    {
        "deadline": "23 juin",
        "conference": "Central Bank of Ireland, UCD & CEPR — Macro-Finance and Financial Stability Policies",
        "date": "30 novembre 2026",
        "location": "Dublin, Irlande",
        "url": "https://www.centralbank.ie/events/2026/11/30/default-calendar/conference-on-macro-finance-and-financial-stability-policies-2026",
        "details": "Notification par mi-août",
    },
    {
        "deadline": "29 juin",
        "conference": "10th Annual Workshop of the ESCB Research Cluster 3 — Financial Stability, Macroprudential Regulation and Microprudential Supervision",
        "date": "À déterminer",
        "location": "",
        "url": "https://www.ecb.europa.eu/press/conferences/html/index.en.html",
        "details": "Workshop dédié à la stabilité financière",
    },
    {
        "deadline": "30 juin",
        "conference": "BoJ — Economics of Payments XV",
        "date": "9–10 novembre 2026",
        "location": "Tokyo, Japon",
        "url": "https://www.imes.boj.or.jp/en/eop/cfp.html",
        "details": "Paiements, fintech, CBDCs",
    },
    {
        "deadline": "30 juin",
        "conference": "Global Research Forum on International Macroeconomics & Finance (Fed)",
        "date": "À déterminer",
        "location": "",
        "url": "https://www.federalreserve.gov/conferences/global-research-forum-on-international-macroeconomics-and-finance.htm",
        "details": "Macroéconomie internationale et finance",
    },
    {
        "deadline": "30 juin",
        "conference": "ICBFS 2026 — International Conference in Banking and Financial Studies",
        "date": "10–11 septembre 2026",
        "location": "",
        "url": "https://icbfs2026.sciencesconf.org",
        "details": "Banque, finance comportementale, big data",
    },
    {
        "deadline": "30 juin",
        "conference": "Banca d'Italia / ECB Workshop — China shock 2.0: Causes, Consequences and Policy Responses",
        "date": "À déterminer",
        "location": "",
        "url": "https://www.ecb.europa.eu/press/conferences/html/index.en.html",
        "details": "Impact du choc chinois sur l'économie globale",
    },
]


# ── Helpers ─────────────────────────────────────────────────────────────────

def is_ecb(inst_str):
    """Check if an institution string references the ECB."""
    if not inst_str:
        return False
    keywords = ["ecb", "european central bank", "banque centrale européenne",
                "banque centrale europeenne", "bce", "europeiska centralbanken",
                "ezb", "europäische zentralbank", "banca centrale europea",
                "euroopan keskuspankki"]
    for kw in keywords:
        if kw in inst_str:
            return True
    return False

def run_scraper():
    """Run the working papers scraper."""
    print("→ Running working papers scraper...", file=sys.stderr)
    result = subprocess.run(
        ["python3", SCRAPER],
        capture_output=True, text=True, timeout=120, cwd=os.path.dirname(SCRAPER)
    )
    if result.returncode != 0:
        print(f"  [WARN] Scraper exited {result.returncode}: {result.stderr[:200]}", file=sys.stderr)
    # Find JSON in output
    idx = result.stdout.find("{")
    if idx >= 0:
        data = json.loads(result.stdout[idx:])
        with open(OUTPUT_FILE, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  → {len(data.get('papers',[]))} papers saved to {OUTPUT_FILE}", file=sys.stderr)
        return data
    return {"papers": [], "metadata": {}}


def load_papers():
    """Load working papers from the JSON output file."""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return run_scraper()


def load_conference_data(folder):
    """Load a single conference's data.json."""
    fp = os.path.join(DATA_DIR, folder, "data.json")
    if not os.path.exists(fp):
        return None
    try:
        with open(fp) as f:
            return json.load(f)
    except Exception:
        return None


def next_two_weeks_conferences():
    """
    Returns conferences that overlap with [TODAY, TODAY+14].
    Each entry: {folder, name, start, end, location, website, ecb_presenters[], sessions_count}
    """
    two_weeks = TODAY + timedelta(days=14)
    result = []
    for folder, info in sorted(CONFERENCE_INFO.items()):
        d = load_conference_data(folder)
        if d is None:
            continue
        conf = d.get("conference", {})
        start_str = conf.get("start_date", "")
        end_str = conf.get("end_date", "")

        # Parse dates
        start = None
        end = None
        for s in [start_str, end_str]:
            try:
                dt = datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if start is None:
                    start = dt
                else:
                    end = dt
            except (ValueError, TypeError):
                pass

        if end is None:
            end = start

        # Check if in window
        if start and (start <= two_weeks and end >= TODAY):
            # Find ECB presenters — handle multiple data schemas
            ecb_list = []
            sessions = d.get("sessions", [])
            for sess in sessions:
                # Schema 1: participants array
                for p in sess.get("participants", []):
                    inst = (p.get("institution") or p.get("affiliation") or "").lower()
                    if is_ecb(inst):
                        ecb_list.append({
                            "name": p.get("name", "?"),
                            "institution": p.get("institution", "") or p.get("affiliation", ""),
                            "title": p.get("title", ""),
                            "session": sess.get("session_title", ""),
                            "role": p.get("role", "Participant"),
                        })

                # Schema 2: chair object (WFA, AFSE, etc.)
                chair = sess.get("chair") or {}
                if isinstance(chair, dict) and chair.get("institution"):
                    if is_ecb(chair.get("institution", "").lower()):
                        ecb_list.append({
                            "name": chair.get("name", "?"),
                            "institution": chair.get("institution", ""),
                            "title": "",
                            "session": sess.get("session_title", ""),
                            "role": "Chair",
                        })

                # Schema 3: papers[].authors (no institution — skip)
                # Schema 4: papers[].discussants[] (WFA-style)
                for paper in sess.get("papers", []):
                    for disc in paper.get("discussants", []):
                        if isinstance(disc, dict) and disc.get("institution"):
                            if is_ecb(disc.get("institution", "").lower()):
                                ecb_list.append({
                                    "name": disc.get("name", "?"),
                                    "institution": disc.get("institution", ""),
                                    "title": paper.get("title", ""),
                                    "session": sess.get("session_title", ""),
                                    "role": "Discussant",
                                })

                # Schema 5: papers[].presenter object
                for paper in sess.get("papers", []):
                    pres = paper.get("presenter")
                    if isinstance(pres, dict):
                        inst = (pres.get("institution") or "").lower()
                        if is_ecb(inst):
                            ecb_list.append({
                                "name": pres.get("name", pres.get("author", "?")),
                                "institution": pres.get("institution", ""),
                                "title": paper.get("title", ""),
                                "session": sess.get("session_title", ""),
                                "role": "Presenter",
                            })

            # ── Schema 6: top-level data["participants"] (MOST COMMON schema) ──
            top_participants = d.get("participants", [])
            if top_participants:
                seen_ecb_names = {p["name"].lower() for p in ecb_list}
                for p in top_participants:
                    inst = (p.get("institution") or p.get("affiliation") or "").lower()
                    if is_ecb(inst):
                        pname = p.get("name", "?")
                        if pname.lower() not in seen_ecb_names:
                            papers_list = p.get("papers", []) or p.get("paper_titles", [])
                            paper_str = "; ".join(papers_list[:2]) if papers_list else ""
                            ecb_list.append({
                                "name": pname,
                                "institution": p.get("institution", "") or p.get("affiliation", ""),
                                "title": paper_str,
                                "session": "",
                                "role": "Participant",
                            })
                            seen_ecb_names.add(pname.lower())

            result.append({
                "folder": folder,
                "name": info["name"],
                "website": info["website"],
                "location": info["location"],
                "start": start_str,
                "end": end_str,
                "start_dt": start,
                "ecb_presenters": ecb_list,
                "sessions_count": len(sessions),
                "total_participants": len(top_participants) if top_participants else sum(len(s.get("participants", [])) for s in sessions),
            })
    return sorted(result, key=lambda x: x["start_dt"] if x["start_dt"] else TODAY)


def format_conf_date(start_str, end_str):
    """Format date range like '22–24 juin'"""
    try:
        start = datetime.strptime(start_str, "%Y-%m-%d")
        end = datetime.strptime(end_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return f"{start_str}–{end_str}"

    months_fr = ["janvier", "février", "mars", "avril", "mai", "juin",
                 "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

    if start.month == end.month:
        return f"{start.day}–{end.day} {months_fr[start.month-1]}"
    else:
        return f"{start.day} {months_fr[start.month-1]} – {end.day} {months_fr[end.month-1]}"


# ── Newsletter Body Builder ─────────────────────────────────────────────────

def build_newsletter(papers_data, conferences):
    papers = papers_data.get("papers", [])
    lines = []

    # ── Header ──
    lines.append("🏛️ CENTRAL BANK RESEARCH PULSE")
    lines.append("Your bi-weekly curated briefing of global central bank research and academic opportunities.")
    lines.append(f"📅 Période couverte : {CUTOFF_STR} — {TODAY_STR}")
    lines.append("")

    # ── Section 1: CfP ──
    lines.append("═" * 60)
    lines.append("1. ⏳ NEXT DEADLINES & CALLS FOR PAPERS")
    lines.append("═" * 60)
    lines.append("")

    for cfp in CALLS_FOR_PAPERS:
        lines.append(f"📅 {cfp['deadline']}")
        lines.append(f"{cfp['conference']}")
        if cfp['date']:
            lines.append(f"   {cfp['date']}" + (f" — {cfp['location']}" if cfp['location'] else ""))
        if cfp['details']:
            lines.append(f"   {cfp['details']}")
        if cfp['url']:
            lines.append(f"   🔗 {cfp['url']}")
        lines.append("")

    # ── Section 2: Conferences ──
    lines.append("═" * 60)
    lines.append("2. 🗓️ CONFERENCES IN THE NEXT TWO WEEKS")
    lines.append("═" * 60)
    lines.append("")

    # Only include conferences with ECB participants
    ecb_conferences = [c for c in conferences if c["ecb_presenters"]]

    if not ecb_conferences:
        lines.append("_Aucune conférence avec participants ECB identifiés dans les deux prochaines semaines._")
        lines.append("")
    else:
        for c in ecb_conferences:
            date_fmt = format_conf_date(c["start"], c["end"])
            lines.append(f"📌 {date_fmt} | {c['name']}")
            lines.append(f"   📍 {c['location']}")
            if c["website"]:
                lines.append(f"   🔗 {c['website']}")

            lines.append(f"   🏦 ECB Presenters ({len(c['ecb_presenters'])}):")
            for p in c["ecb_presenters"]:
                line = f"      • {p['name']} ({p['role']})"
                if p["title"]:
                    line += f" — \"{p['title'][:80]}\""
                lines.append(line)
            lines.append("")

    # ── Section 3: Working Papers ──
    lines.append("═" * 60)
    lines.append("3. 📈 THE MACRO VIEW: TOP WORKING PAPERS")
    lines.append("═" * 60)
    lines.append("")

    # Group by source
    sources_order = [
        ("ECB Working Paper", "🏦 EUROPEAN CENTRAL BANK"),
        ("FEDS (Federal Reserve Board)", "🇺🇸 FEDERAL RESERVE BOARD — FEDS"),
        ("BIS Working Paper", "🏦 BANK FOR INTERNATIONAL SETTLEMENTS"),
        ("Bank of England Staff Working Paper", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 BANK OF ENGLAND"),
    ]

    by_source = defaultdict(list)
    for p in papers:
        by_source[p["source"]].append(p)

    total_count = 0
    for src_key, header in sources_order:
        pp_list = by_source.get(src_key, [])
        if not pp_list:
            continue
        total_count += len(pp_list)

        lines.append("─" * 55)
        lines.append(header)
        lines.append("─" * 55)
        lines.append("")

        pp_list.sort(key=lambda x: x.get("publication_date", ""), reverse=True)
        for p in pp_list:
            pid = p.get("paper_number", "")
            title = p["title"]
            authors = ", ".join(p.get("authors", []))
            pub_date = p.get("publication_date", "")
            abstract = p.get("abstract", "")
            pdf_url = p.get("pdf_url", "")
            page_url = p.get("url", "")
            doi = p.get("doi", "")

            # Build title with URL
            if page_url:
                title_line = f"{pid} — {title}" if pid else f"— {title}"
                title_line += f"\n   🔗 {page_url}"
            else:
                title_line = f"{pid} — {title}" if pid else f"— {title}"
                if pdf_url:
                    title_line += f"\n   📄 {pdf_url}"
            lines.append(title_line)

            if authors:
                lines.append(f"   {', '.join(p.get('authors', []))} · {pub_date}")
            else:
                lines.append(f"   {pub_date}")

            # Add PDF link if not already shown with title
            extra_urls = ""
            if not page_url and pdf_url:
                extra_urls += f"📄 {pdf_url}"
            if doi:
                if extra_urls:
                    extra_urls += "  |  "
                extra_urls += f"DOI: {doi}"
            if extra_urls:
                lines.append(f"   {extra_urls}")
            lines.append("")

    # ── Summary ──
    lines.append("═" * 60)
    lines.append("📊 RÉSUMÉ")
    lines.append("═" * 60)
    lines.append("")

    lines.append(f"{'Source':40s} | {'Papiers':>8s}")
    lines.append("-" * 52)
    for src_key, header in sources_order:
        count = len(by_source.get(src_key, []))
        if count > 0:
            label = src_key.split("(")[0].strip()
            lines.append(f"{label:40s} | {count:8d}")
    lines.append("-" * 52)
    lines.append(f"{'Total':40s} | {total_count:8d}")
    lines.append("")

    lines.append(f"📁 Données complètes : https://drive.google.com/file/d/1ZvN5H2OuksKIyoV2FtdDT3qV4o4snlb6/view")
    lines.append("")

    # ── Footer ──
    next_issue = TODAY + timedelta(days=14)
    lines.append("═" * 60)
    lines.append(f"Prochaine édition : {next_issue.strftime('%d %B %Y')}")
    lines.append("Pour soumettre un papier, une conférence ou un appel à contributions : répondre à cet email.")
    lines.append("═" * 60)

    return "\n".join(lines)


def send_email(body, recipient):
    """Send the newsletter via Gmail."""
    subject = f"🏛️ Central Bank Research Pulse — {TODAY_STR}"
    # Write body to temp file
    with open(NEWSLETTER_FILE, "w") as f:
        f.write(body)
    print(f"→ Newsletter body saved ({len(body)} chars)", file=sys.stderr)

    cmd = [
        "python3", GMAIL_SCRIPT, "gmail", "send",
        "--to", recipient,
        "--subject", subject,
        "--body", body,
    ]
    print(f"→ Sending to {recipient}...", file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        print(f"  ✓ Sent! ID: {result.stdout.strip()}", file=sys.stderr)
    else:
        print(f"  ✗ Failed: {result.stderr[:500]}", file=sys.stderr)
    return result.returncode == 0


def main():
    # Parse args
    do_scrape = "--scrape" in sys.argv
    do_send = "--send" in sys.argv
    recipient = None
    for i, arg in enumerate(sys.argv):
        if arg == "--to" and i + 1 < len(sys.argv):
            recipient = sys.argv[i + 1]

    # Default recipient if sending
    if do_send and not recipient:
        recipient = "Antoine.baena@ecb.europa.eu"

    # Step 1: Load/run scraper
    if do_scrape or not os.path.exists(OUTPUT_FILE):
        papers_data = run_scraper()
    else:
        papers_data = load_papers()

    papers = papers_data.get("papers", [])
    print(f"📚 {len(papers)} working papers loaded", file=sys.stderr)

    # Step 2: Load conference data
    conferences = next_two_weeks_conferences()
    print(f"🗓️ {len(conferences)} conferences in the next 2 weeks", file=sys.stderr)

    # Step 3: Build newsletter
    body = build_newsletter(papers_data, conferences)
    with open(NEWSLETTER_FILE, "w") as f:
        f.write(body)
    print(f"📝 Newsletter saved to {NEWSLETTER_FILE}", file=sys.stderr)

    # Step 4: Send if requested
    if do_send and recipient:
        success = send_email(body, recipient)
        return 0 if success else 1

    print(f"\n📄 Preview first 500 chars:", file=sys.stderr)
    print(body[:500], file=sys.stderr)
    print(f"\n... Use --send --to email@domain to send", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
