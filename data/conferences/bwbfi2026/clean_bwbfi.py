#!/usr/bin/env python3
"""
BWBFI 2026 — Produce v2 output directly (standalone converter).

Handles:
  - Malformed authors (string dicts → plain names)
  - Empty session titles → generate descriptive "Session N" fallback
  - None/null → "" for institutions
  - Participants linked to their papers
  - Full v2 schema with conference, sessions, participants, scrape_metadata
"""
import json
import re
import os
from datetime import datetime, timezone

DATA_PATH = os.path.expanduser("~/economics-conferences/bwbfi2026/data.json")


def parse_author_string(s):
    """Extract name from a string like "{'name': 'Haelim Anderson', 'institution': '...'}" """
    m = re.search(r"'name':\s*'([^']+)'", s)
    if m:
        return m.group(1)
    m = re.search(r'"name":\s*"([^"]+)"', s)
    if m:
        return m.group(1)
    return s.strip()


def clean_none(val):
    """Replace None/NoneType with empty string."""
    if val is None or val == "None" or (isinstance(val, str) and val.strip().lower() == "none"):
        return ""
    return val


def deep_clean_none(obj):
    """Recursively replace None → '' in dicts/lists."""
    if isinstance(obj, dict):
        return {k: deep_clean_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_clean_none(v) for v in obj]
    elif obj is None:
        return ""
    return obj


def ensure_v2_schema(data):
    """Convert the whole structure to v2 schema, patching any issues."""

    # ── 1. Fix conference ──
    if isinstance(data.get("conference"), str):
        data["conference"] = {"name": data["conference"]}
    conf = data.setdefault("conference", {})
    conf.setdefault("name", "9th Bristol Workshop on Banking and Financial Intermediation (BWBFI 2026)")
    conf.setdefault("short_name", "BWBFI")
    conf.setdefault("year", 2026)
    conf.setdefault("start_date", "2026-06-11")
    conf.setdefault("end_date", "2026-06-12")
    conf.setdefault("location", "Bristol, United Kingdom")

    # ── 2. Fix sessions ──
    sessions = data.get("sessions", [])
    for i, session in enumerate(sessions, start=1):
        # Generate descriptive title if missing/empty
        title = session.get("session_title", "").strip()
        if not title:
            # Try alternate keys
            title = session.get("title", session.get("name", "")).strip()
        if not title:
            title = f"Session {i}"
        session["session_title"] = title

        # Ensure papers key exists
        session.setdefault("papers", [])

        # Fix authors in papers
        for paper in session["papers"]:
            cleaned_authors = []
            for author in paper.get("authors", []):
                if isinstance(author, str) and author.startswith("{"):
                    cleaned_authors.append(parse_author_string(author))
                else:
                    cleaned_authors.append(author)
            paper["authors"] = cleaned_authors

        # Fix chair
        chair = session.get("chair", "")
        if isinstance(chair, str) and chair.startswith("{"):
            session["chair"] = parse_author_string(chair)

        # Ensure each paper has required fields
        for paper in session["papers"]:
            paper.setdefault("title", "")
            paper.setdefault("authors", [])
            paper.setdefault("presenter", "")

    # ── 3. Build author→papers mapping ──
    author_to_papers = {}
    for session in sessions:
        for paper in session.get("papers", []):
            for author_name in paper.get("authors", []):
                if author_name not in author_to_papers:
                    author_to_papers[author_name] = []
                author_to_papers[author_name].append(paper["title"])

    # ── 4. Fix participants ──
    participants = data.get("participants", [])
    for participant in participants:
        name = participant.get("name", "")
        # Link papers
        if name in author_to_papers:
            participant["papers"] = author_to_papers[name]
            participant["is_presenter"] = True
        # Fix institution: None → ""
        participant["institution"] = clean_none(participant.get("institution", ""))
        # Ensure papers is a list
        participant.setdefault("papers", [])
        # Ensure is_presenter exists
        participant.setdefault("is_presenter", False)

    # ── 5. Deep clean None → "" ──
    data = deep_clean_none(data)

    # ── 6. Ensure scrape_metadata ──
    metadata = data.setdefault("scrape_metadata", {})
    metadata.setdefault("scraped_at", datetime.now(timezone.utc).isoformat())
    metadata.setdefault("source_url", "https://sites.google.com/view/banking-workshop")
    metadata.setdefault("program_available", len(sessions) > 0)
    metadata.setdefault("program_type", "web")

    # Summary notes
    total_papers = sum(len(s.get("papers", [])) for s in sessions)
    total_participants = len(data.get("participants", []))
    metadata["notes"] = f"{len(sessions)} sessions, {total_papers} papers, {total_participants} participants"

    return data


def validate(data):
    """Validate v2 schema requirements."""
    errors = []
    warnings = []

    # Conference must be a dict
    if not isinstance(data.get("conference"), dict):
        errors.append("conference is not a dict")

    # Sessions must be a list
    sessions = data.get("sessions", [])
    if not isinstance(sessions, list):
        errors.append("sessions is not a list")

    for i, s in enumerate(sessions):
        title = s.get("session_title", "")
        if not title or not isinstance(title, str):
            errors.append(f"Session {i+1}: missing or invalid session_title")
        if "papers" not in s:
            errors.append(f"Session {i+1}: missing papers key")
        elif not isinstance(s["papers"], list):
            errors.append(f"Session {i+1}: papers is not a list")
        else:
            for j, p in enumerate(s["papers"]):
                if "title" not in p:
                    errors.append(f"Session {i+1}, paper {j+1}: missing title")
                if "authors" not in p:
                    errors.append(f"Session {i+1}, paper {j+1}: missing authors")
                if "presenter" not in p:
                    warnings.append(f"Session {i+1}, paper {j+1}: missing presenter")

    # Participants must be a list
    participants = data.get("participants", [])
    if not isinstance(participants, list):
        errors.append("participants is not a list")
    else:
        for i, p in enumerate(participants):
            if "name" not in p:
                errors.append(f"Participant {i+1}: missing name")
            if "institution" not in p:
                warnings.append(f"Participant {i+1}: missing institution")
            if "papers" not in p:
                warnings.append(f"Participant {i+1}: missing papers")
            if "is_presenter" not in p:
                warnings.append(f"Participant {i+1}: missing is_presenter")

    # No None/null values
    raw = json.dumps(data)
    if "None" in raw or "null" in raw.lower():
        remaining = raw.count("null") + raw.count("None")
        warnings.append(f"Found ~{remaining} None/null values remaining")

    return errors, warnings


def main():
    # Load
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to clean v2
    data = ensure_v2_schema(data)

    # Write
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Validate
    errors, warnings = validate(data)

    # Summary
    sessions = data.get("sessions", [])
    total_papers = sum(len(s.get("papers", [])) for s in sessions)
    total_participants = len(data.get("participants", []))

    print(f"\n{'='*55}")
    print("BWBFI 2026 — v2 Output Complete")
    print(f"{'='*55}")
    print(f"  Sessions:     {len(sessions)}")
    for s in sessions:
        n_p = len(s.get("papers", []))
        print(f"    - {s['session_title']} ({n_p} papers)")
    print(f"  Total papers: {total_papers}")
    print(f"  Participants: {total_participants}")
    print()

    if errors:
        print(f"❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    ✗ {e}")
    else:
        print("✅ No errors!")

    if warnings:
        print(f"⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    ⚠ {w}")
    else:
        print("✅ No warnings!")

    print(f"\n💾 Written to: {DATA_PATH}")
    return len(errors) == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
