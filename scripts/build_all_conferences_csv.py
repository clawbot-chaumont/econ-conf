#!/usr/bin/env python3
"""
Build a single giant CSV from all scraped conference data.json files,
then upload it to Google Drive.
"""

import csv
import json
import os

DATA_DIR = os.path.expanduser("~/economics-conferences")
OUTPUT_CSV = os.path.join(DATA_DIR, "ALL_CONFERENCES_2026.csv")

# Fields for the flat CSV — one row per participant per conference
FIELDS = [
    # Conference
    "conference_short_name",
    "conference_name",
    "conference_year",
    "conference_start_date",
    "conference_end_date",
    "conference_location",
    "scrape_source_url",
    "scrape_date",
    # Participant
    "participant_name",
    "participant_institution",
    "participant_is_presenter",
    "participant_paper_count",
    "participant_papers",                # semicolon-separated
    # Session info for the participant
    "participant_session_count",
    "participant_session_titles",         # semicolon-separated
    "participant_session_dates",          # semicolon-separated
    "participant_session_chairs",         # semicolon-separated
    # Aggregate conference stats
    "conference_total_sessions",
    "conference_total_participants",
    "conference_total_papers_in_sessions",
    "conference_total_papers_standalone",
]


def build_name_to_session_lookup(sessions):
    """Build a mapping from participant name → list of session dicts they appear in."""
    name_to_sessions = {}
    for sess in sessions:
        papers = sess.get("papers", [])
        for paper in papers:
            authors = paper.get("authors", [])
            presenter = paper.get("presenter", "")
            all_names = list(authors) + ([presenter] if presenter else [])
            for name in all_names:
                if name not in name_to_sessions:
                    name_to_sessions[name] = []
                name_to_sessions[name].append(sess)
    return name_to_sessions


def count_papers_in_sessions(sessions):
    total = 0
    for sess in sessions:
        total += len(sess.get("papers", []))
    return total


def build_rows(data, folder_name):
    """Yield CSV rows (as dicts) from a single data.json."""
    conf = data.get("conference", {})
    if isinstance(conf, str):
        # Legacy format — convert inline
        conf = {"name": conf, "short_name": folder_name.upper().replace("2026", "").strip("_")}
    meta = data.get("scrape_metadata", {})

    conf_short = conf.get("short_name", folder_name)
    conf_name = conf.get("name", "")
    conf_year = conf.get("year", 2026)
    conf_start = conf.get("start_date", "")
    conf_end = conf.get("end_date", "")
    conf_loc = conf.get("location", "")
    scrape_url = meta.get("source_url", "")
    scrape_date = meta.get("scraped_at", "")

    sessions = data.get("sessions", [])
    participants = data.get("participants", [])
    papers_standalone = data.get("papers", [])

    total_sessions = len(sessions)
    total_participants = len(participants)
    total_papers_sessions = count_papers_in_sessions(sessions)
    total_papers_standalone = len(papers_standalone)

    # Build lookup from participant name → sessions they're in
    name_to_sessions = build_name_to_session_lookup(sessions)

    if not participants:
        # If no participants but we have sessions, derive virtual participants from papers
        for sess in sessions:
            for paper in sess.get("papers", []):
                for author in paper.get("authors", []):
                    row = {
                        "conference_short_name": conf_short,
                        "conference_name": conf_name,
                        "conference_year": conf_year,
                        "conference_start_date": conf_start,
                        "conference_end_date": conf_end,
                        "conference_location": conf_loc,
                        "scrape_source_url": scrape_url,
                        "scrape_date": scrape_date,
                        "participant_name": author,
                        "participant_institution": "",
                        "participant_is_presenter": "TRUE" if author == paper.get("presenter", "") else "FALSE",
                        "participant_paper_count": 1,
                        "participant_papers": paper.get("title", ""),
                        "participant_session_count": 1,
                        "participant_session_titles": sess.get("session_title", ""),
                        "participant_session_dates": sess.get("date", ""),
                        "participant_session_chairs": sess.get("chair", ""),
                        "conference_total_sessions": total_sessions,
                        "conference_total_participants": total_participants,
                        "conference_total_papers_in_sessions": total_papers_sessions,
                        "conference_total_papers_standalone": total_papers_standalone,
                    }
                    yield row
        return

    for p in participants:
        name = p.get("name", "")
        institution = p.get("institution", "")
        is_presenter = p.get("is_presenter", False)
        papers_list = p.get("papers", p.get("paper_titles", []))
        papers_str = "; ".join(papers_list) if papers_list else ""
        paper_count = len(papers_list)

        # Find which sessions this participant is in
        p_sessions = name_to_sessions.get(name, [])
        session_count = len(p_sessions)
        def safe_str(v):
            return str(v) if not isinstance(v, str) else v
        session_titles = "; ".join(sorted(set(safe_str(s.get("session_title", "")) for s in p_sessions)))
        session_dates = "; ".join(set(str(s.get("date", "")) for s in p_sessions if s.get("date")))
        session_chairs = "; ".join(sorted(set(safe_str(s.get("chair", "")) for s in p_sessions if s.get("chair"))))

        row = {
            "conference_short_name": conf_short,
            "conference_name": conf_name,
            "conference_year": conf_year,
            "conference_start_date": conf_start,
            "conference_end_date": conf_end,
            "conference_location": conf_loc,
            "scrape_source_url": scrape_url,
            "scrape_date": scrape_date,
            "participant_name": name,
            "participant_institution": institution,
            "participant_is_presenter": "TRUE" if is_presenter else "FALSE",
            "participant_paper_count": paper_count,
            "participant_papers": papers_str,
            "participant_session_count": session_count,
            "participant_session_titles": session_titles,
            "participant_session_dates": session_dates,
            "participant_session_chairs": session_chairs,
            "conference_total_sessions": total_sessions,
            "conference_total_participants": total_participants,
            "conference_total_papers_in_sessions": total_papers_sessions,
            "conference_total_papers_standalone": total_papers_standalone,
        }
        yield row


def main():
    all_rows = []
    conferences_found = []
    errors = []

    # Scan all subdirectories for data.json
    for item in sorted(os.listdir(DATA_DIR)):
        subdir = os.path.join(DATA_DIR, item)
        data_json = os.path.join(subdir, "data.json")
        if not os.path.isdir(subdir) or not os.path.isfile(data_json):
            continue

        try:
            with open(data_json, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            errors.append((item, str(e)))
            continue

        rows = list(build_rows(data, item))
        all_rows.extend(rows)
        conf_name = data.get("conference", {}).get("name", item) if isinstance(data.get("conference"), dict) else item
        n_parts = len(data.get("participants", []))
        n_sessions = len(data.get("sessions", []))
        conferences_found.append(f"{item}: {conf_name} — {n_parts} participants, {n_sessions} sessions → {len(rows)} CSV rows")

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    # Print summary
    print(f"✅ CSV written: {OUTPUT_CSV}")
    print(f"   Total rows: {len(all_rows)}")
    print(f"   Conferences: {len(conferences_found)}")
    print()
    print("Conferences included:")
    for c in conferences_found:
        print(f"   • {c}")

    if errors:
        print(f"\n⚠️  Errors ({len(errors)}):")
        for folder, err in errors:
            print(f"   • {folder}: {err}")

    print(f"\n{'='*60}")
    print(f"Now uploading to Google Drive…")

    import subprocess
    result = subprocess.run(
        ["python3", os.path.expanduser("~/.hermes/skills/productivity/google-workspace/scripts/google_api.py"),
         "drive", "upload",
         OUTPUT_CSV,
         "--name", "ALL_CONFERENCES_2026.csv",
         "--parent", "1IQY4Ip1X2ZzsxLn14okVcvMuV0CQGQOQ"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        upload_data = json.loads(result.stdout)
        print(f"✅ Uploaded to Drive!")
        print(f"   File: {upload_data['name']}")
        print(f"   ID:   {upload_data['id']}")
        print(f"   Link: {upload_data['webViewLink']}")
    else:
        print(f"❌ Upload failed: {result.stderr}")
        print(f"Stdout: {result.stdout}")


if __name__ == "__main__":
    main()
