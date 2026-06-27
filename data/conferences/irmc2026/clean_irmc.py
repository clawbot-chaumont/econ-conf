#!/usr/bin/env python3
"""
IRMC 2026 — Produce v2 output directly (standalone converter).

Handles:
  - Sessions with empty titles → generate descriptive fallback
  - Coffee break / non-paper sessions → ensure papers: []
  - None/null → "" for institutions
  - Full v2 schema
"""
import json
import os
from datetime import datetime, timezone

DATA_PATH = os.path.expanduser("~/economics-conferences/irmc2026/data.json")


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


def ensure_papers_array(session):
    """Ensure the session has a papers key, defaulting to [] if missing."""
    if "papers" not in session:
        session["papers"] = []
    papers = session["papers"]
    if not isinstance(papers, list):
        # If it's something weird, replace with []
        session["papers"] = []
    return session


def fill_paper_fields(paper):
    """Ensure each paper has the required v2 fields."""
    paper.setdefault("title", "")
    paper.setdefault("authors", [])
    paper.setdefault("presenter", "")
    # Normalize authors list
    authors = paper.get("authors", [])
    if isinstance(authors, str):
        # Split by comma or semicolon
        parts = [a.strip() for a in authors.replace(";", ",").split(",") if a.strip()]
        paper["authors"] = parts
    return paper


def ensure_v2_schema(data):
    """Convert the whole structure to v2 schema."""

    # ── 1. Fix conference ──
    if isinstance(data.get("conference"), str):
        data["conference"] = {"name": data["conference"]}
    conf = data.setdefault("conference", {})
    conf.setdefault("name", "International Risk Management Conference")
    conf.setdefault("short_name", "IRMC")
    conf.setdefault("year", 2026)
    conf.setdefault("start_date", "2026-06-17")
    conf.setdefault("end_date", "2026-06-19")
    conf.setdefault("location", "Warsaw, Poland")

    # ── 2. Fix sessions ──
    sessions = data.get("sessions", [])
    break_keywords = ["COFFEE", "LUNCH", "BREAK", "REGISTRATION", "GALA", "DINNER", "WELCOME"]

    for i, session in enumerate(sessions, start=1):
        # Normalize session keys
        if "session_title" not in session:
            for key in ("title", "name", "session_name", "topic"):
                if key in session and session[key]:
                    session["session_title"] = session[key]
                    break

        # Generate fallback title if empty
        title = session.get("session_title", "").strip()
        if not title:
            session["session_title"] = f"Session {i}"

        # Ensure papers key exists (key fix for coffee breaks, lunches, etc.)
        session = ensure_papers_array(session)

        # Fill paper fields
        for j, paper in enumerate(session.get("papers", [])):
            session["papers"][j] = fill_paper_fields(paper)

        # Normalize date/time fields
        for field in ("date", "time", "room", "chair"):
            val = session.get(field, "")
            if isinstance(val, str):
                session[field] = val.strip()
            elif val is None:
                session[field] = ""

    # ── 3. Build author→papers mapping and participants ──
    participants_dict = {}
    
    # First, collect existing participants
    existing_participants = {}
    for p in data.get("participants", []):
        name = p.get("name", "").strip()
        if name:
            existing_participants[name.lower()] = p

    # Build from sessions
    session_participants = {}
    for session in sessions:
        chair = session.get("chair", "").strip()
        if chair and chair.lower() not in session_participants:
            session_participants[chair.lower()] = {"name": chair, "papers": [], "is_presenter": False}
        
        for paper in session.get("papers", []):
            for author_name in paper.get("authors", []):
                author_name = author_name.strip()
                if not author_name:
                    continue
                key = author_name.lower()
                if key not in session_participants:
                    # Check institution from existing participants
                    inst = ""
                    if key in existing_participants:
                        inst = clean_none(existing_participants[key].get("institution", ""))
                    session_participants[key] = {
                        "name": author_name,
                        "institution": inst,
                        "is_presenter": True,
                        "papers": [],
                    }
                if paper.get("title") and paper["title"] not in session_participants[key]["papers"]:
                    session_participants[key]["papers"].append(paper["title"])

    # Merge existing participants that aren't authors but are in the list
    for key, p in existing_participants.items():
        if key not in session_participants:
            session_participants[key] = {
                "name": p.get("name", ""),
                "institution": clean_none(p.get("institution", "")),
                "is_presenter": p.get("is_presenter", False),
                "papers": p.get("papers", []),
            }

    participants = list(session_participants.values())

    # ── 4. Deep clean None → "" ──
    data = deep_clean_none(data)

    # ── 5. Ensure scrape_metadata ──
    metadata = data.setdefault("scrape_metadata", {})
    metadata.setdefault("scraped_at", datetime.now(timezone.utc).isoformat())
    metadata.setdefault("source_url", "https://www.therisksociety.com/irmc")
    metadata.setdefault("program_available", len(sessions) > 0)
    metadata.setdefault("program_type", "web")

    total_papers = sum(len(s.get("papers", [])) for s in sessions)
    metadata["notes"] = f"{len(sessions)} sessions, {total_papers} papers, {len(participants)} participants"

    # Update data
    data["sessions"] = sessions
    data["participants"] = participants

    return data


def validate(data):
    """Validate v2 schema requirements."""
    errors = []
    warnings = []

    if not isinstance(data.get("conference"), dict):
        errors.append("conference is not a dict")

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
                # Check for empty titles in non-break sessions
                if not p.get("title") and "COFFEE" not in title.upper() and "LUNCH" not in title.upper():
                    warnings.append(f"Session {i+1}, paper {j+1}: empty title")

    participants = data.get("participants", [])
    if not isinstance(participants, list):
        errors.append("participants is not a list")

    # Check for None values
    raw = json.dumps(data)
    null_count = raw.count("null") - raw.count('"null"')
    none_count = raw.count("None")
    if null_count > 0 or none_count > 0:
        warnings.append(f"Found {null_count} null + {none_count} None value(s) remaining")

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
    print("IRMC 2026 — v2 Output Complete")
    print(f"{'='*55}")
    print(f"  Sessions:     {len(sessions)}")
    coffee_break_count = sum(1 for s in sessions if "COFFEE" in s.get("session_title", "").upper())
    lunch_count = sum(1 for s in sessions if "LUNCH" in s.get("session_title", "").upper())
    paper_sessions = len(sessions) - coffee_break_count - lunch_count
    print(f"    Paper sessions:  {paper_sessions}")
    print(f"    Coffee breaks:   {coffee_break_count}")
    print(f"    Lunch sessions:  {lunch_count}")
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
