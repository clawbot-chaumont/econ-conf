#!/usr/bin/env python3
"""Validation script for RCEA 2026 scraper output."""

import json
import sys

DATA_FILE = "/root/economics-conferences/rcea2026/data.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

errors = []
warnings = []

# 1. Conference metadata
conf = data.get("conference", {})
checks = {
    "title": "RCEA International Conference in Economics, Econometrics, and Finance",
    "short_name": "RCEA 2026",
    "year": 2026,
    "start_date": "2026-05-25",
    "end_date": "2026-05-27",
    "location": "Madrid, Spain",
}
for key, expected in checks.items():
    actual = conf.get(key)
    if actual != expected:
        errors.append(f"conference.{key}: expected {expected!r}, got {actual!r}")

# 2. Session count
sessions = data.get("sessions", [])
expected_sessions = 82
if len(sessions) != expected_sessions:
    errors.append(f"Expected {expected_sessions} sessions, got {len(sessions)}")

# 3. Paper count
total_papers = sum(len(s.get("papers", [])) for s in sessions)
expected_papers = 282
if total_papers != expected_papers:
    errors.append(f"Expected {expected_papers} papers, got {total_papers}")

# 4. Check some specific sessions
session_map = {s["session_number"]: s for s in sessions if s.get("session_number")}

# Check session 5 (CLIMATE AND ENERGY FINANCE CONFERENCE 1) - should have papers
s5 = session_map.get(5)
if s5:
    if s5["title"] != "CLIMATE AND ENERGY FINANCE CONFERENCE 1":
        errors.append(f"Session 5 title mismatch: {s5['title']}")
    if len(s5.get("papers", [])) != 5:
        errors.append(f"Session 5 expected 5 papers, got {len(s5.get('papers', []))}")
    if s5.get("chair") and s5["chair"]["name"] != "Natalia Fabra":
        warnings.append(f"Session 5 chair name unexpected: {s5['chair']['name']}")
else:
    warnings.append("Session 5 not found in session_map")

# Check REGISTRATION (session 1) - should have no papers
s1 = session_map.get(1)
if s1:
    if s1["title"] != "REGISTRATION":
        errors.append(f"Session 1 title mismatch: {s1['title']}")
    if s1.get("papers"):
        errors.append(f"Session 1 (REGISTRATION) should have no papers, got {len(s1['papers'])}")
    if s1.get("date") != "2026-05-25":
        warnings.append(f"Session 1 date unexpected: {s1.get('date')}")
else:
    warnings.append("Session 1 not found in session_map")

# Check KEYNOTE SESSION 1 (session 3) - should have no papers
s3 = session_map.get(3)
if s3:
    if "KEYNOTE" not in (s3.get("title") or ""):
        warnings.append(f"Session 3 title unexpected: {s3.get('title')}")
    if s3.get("papers"):
        errors.append(f"Session 3 (KEYNOTE) should have no papers, got {len(s3['papers'])}")
else:
    warnings.append("Session 3 not found in session_map")

# 5. Check participants
participants = data.get("participants", [])
if len(participants) < 200:
    errors.append(f"Expected at least 200 participants, got {len(participants)}")

# Check known participants exist
known = [
    ("Natalia Fabra", "natalia.fabra@gmail.com", "CEMFI"),
    ("Isabel Figuerola Ferretti", "ifiguerola@comillas.edu", "ICADE"),
    ("Claudio Morana", "claudio.morana@unimib.it", "Università di Milano-Bicocca"),
]
for name, email, inst in known:
    found = [p for p in participants if p.get("email") == email]
    if not found:
        # Try by name
        found = [p for p in participants if name.lower() in p.get("name", "").lower()]
    if not found:
        warnings.append(f"Known participant {name} ({email}) not found in participants list")
    else:
        p = found[0]
        if name not in p.get("name", ""):
            warnings.append(f"Participant {email}: expected name {name!r}, got {p.get('name')!r}")

# 6. Validate paper structure
for s in sessions:
    for p in s.get("papers", []):
        if not p.get("title"):
            errors.append(f"Session {s.get('session_number')}: paper with no title")
        if not p.get("presenters"):
            title_preview = (p.get('title') or '?')[:50]
            errors.append(f"Session {s.get('session_number')}, paper '{title_preview}': no presenters")
        for pres in p.get("presenters", []):
            if not pres.get("name"):
                errors.append(f"Session {s.get('session_number')}: presenter with no name")
            if not pres.get("institution"):
                title_prefix = (p.get('title') or '?')[:50]
                warnings.append(f"Session {s.get('session_number')}, paper '{title_prefix}': presenter '{pres.get('name')}' has no institution")

# 7. Check session numbers are unique and sequential
sess_nums = sorted([s["session_number"] for s in sessions if s.get("session_number")])
for i, n in enumerate(sess_nums):
    if n != i + 1:
        warnings.append(f"Session numbers not sequential: expected {i+1}, got {n}")
        break

# ── Report ─────────────────────────────────────────────────────────────────
print("=" * 60)
print("VALIDATION REPORT")
print("=" * 60)
print(f"Sessions:  {len(sessions)}")
print(f"Papers:    {total_papers}")
print(f"Participants: {len(participants)}")
print()
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  ✗ {e}")
else:
    print("ERRORS: 0 ✓")
print()
if warnings:
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  ⚠ {w}")
else:
    print("WARNINGS: 0 ✓")
print()
if not errors:
    print("✅ VALIDATION PASSED")
    sys.exit(0)
else:
    print("❌ VALIDATION FAILED")
    sys.exit(1)
