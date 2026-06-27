#!/usr/bin/env python3
"""
Parser for MYE/EAYE 2026 program from PDF-extracted text.
Uses whitespace-gap column splitting (3+ spaces as column separator).

Reads: /tmp/mye_program.txt
Writes: ~/economics-conferences/mye2026/data.json
"""

import json
import os
import re
from collections import OrderedDict

INPUT_FILE = "/tmp/mye_program.txt"
OUTPUT_FILE = os.path.expanduser("~/economics-conferences/mye2026/data.json")

ROOM_FLOORS = {
    "Oteiza": "1st Floor", "Etxepare": "1st Floor",
    "Arriaga": "2nd Floor", "Laboa": "2nd Floor",
    "Elhuyar": "Ground Floor",
}

DAY_NUM_MAP = {1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 2, 9: 3, 10: 3}
DAY_DATES = {1: "2026-05-18", 2: "2026-05-19", 3: "2026-05-20"}

ROOMS_DAY1 = ["Oteiza", "Etxepare", "Arriaga", "Laboa"]
ROOMS_DAY23 = ["Elhuyar", "Oteiza", "Etxepare", "Arriaga", "Laboa"]


def read_lines():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    text = text.replace("\f", "\n")
    return [l.rstrip() for l in text.split("\n")]


def split_into_columns(line, num_rooms):
    """
    Split a line by 3+ spaces. Returns list of column texts,
    padding to num_rooms entries (room 0 = label area, then rooms 1..N).
    """
    parts = re.split(r"\s{3,}", line)
    result = []
    for p in parts:
        p = p.strip()
        if p:
            result.append(p)
    # Pad: first entry might be empty (for continuation lines)
    # We want: [label_or_empty, room1_text, room2_text, ...]
    # If we have (num_rooms+1) entries, first is label
    # If we have num_rooms entries, first IS room1 (no label)
    # If we have fewer, pad with empty strings
    if len(result) >= num_rooms + 1:
        # Has label prefix
        result = result[:num_rooms + 1]
    elif len(result) == num_rooms:
        # No label prefix — prepend empty label
        result = [""] + result
    else:
        # Pad
        while len(result) < num_rooms + 1:
            result.append("")
        result = result[:num_rooms + 1]
    return result  # [label, room1, room2, ..., roomN]


def find_session_blocks(lines):
    """Split text into session blocks."""
    blocks = []
    i = 0
    while i < len(lines):
        m = re.match(
            r"Parallel Session (\d+)\s*\(Day (\d+)\)\s*(\d+:\d+)\s*-\s*(\d+:\d+)",
            lines[i],
        )
        if m:
            snum, dnum, tstart, tend = (
                int(m.group(1)), int(m.group(2)), m.group(3), m.group(4)
            )
            block = []
            i += 1
            while i < len(lines):
                if re.search(r"Rules for the parallel sessions", lines[i], re.IGNORECASE):
                    block.append(lines[i])
                    i += 1
                    break
                if re.match(r"Parallel Session \d+\s*\(Day \d+\)", lines[i]):
                    break
                block.append(lines[i])
                i += 1
            blocks.append((snum, dnum, tstart, tend, block))
        else:
            i += 1
    return blocks


def get_room_list(day_num):
    return ROOMS_DAY1 if day_num == 1 else ROOMS_DAY23


def extract_session_theme(block, num_rooms):
    """
    Extract session theme per room from lines between Session and Talk 1.
    Uses same column splitting approach.
    """
    themes = {}
    in_theme = False
    theme_cols = [[] for _ in range(num_rooms)]

    for line in block:
        stripped = line.strip()
        if stripped.startswith("Session") or stripped.startswith("Session"):
            in_theme = True
        if re.match(r"^\s*Talk\s+1\b", stripped):
            break
        if in_theme:
            cols = split_into_columns(line, num_rooms)
            for ri in range(num_rooms):
                txt = cols[ri + 1] if ri + 1 < len(cols) else ""
                if txt:
                    theme_cols[ri].append(txt)

    for ri, rname in enumerate(get_room_list(
        1 if len(theme_cols) == 4 else 2
    )):
        combined = " ".join(theme_cols[ri])
        combined = re.sub(r"^Session\s+", "", combined).strip()
        themes[rname] = combined

    return themes


def parse_session(snum, dnum, block_lines):
    """Parse a single session block using column splitting."""
    rooms = get_room_list(dnum)
    num_rooms = len(rooms)

    # Extract themes
    themes = {}
    theme_cols = [[] for _ in range(num_rooms)]
    in_theme = False

    for line in block_lines:
        stripped = line.strip()
        if stripped.startswith("Session") or stripped.startswith("Session"):
            in_theme = True
        if re.match(r"^\s*Talk\s+1\b", stripped):
            break
        if in_theme:
            cols = split_into_columns(line, num_rooms)
            for ri in range(num_rooms):
                if ri + 1 < len(cols):
                    txt = cols[ri + 1]
                    if txt:
                        theme_cols[ri].append(txt)

    for ri, rname in enumerate(rooms):
        combined = " ".join(theme_cols[ri])
        combined = re.sub(r"^Session\s+", "", combined).strip()
        themes[rname] = combined

    # Split into talk sections
    talk_sections = []
    current_talk_lines = []
    current_talk_num = None

    for line in block_lines:
        m = re.match(r"^\s*Talk\s+(\d+)\b", line)
        if m:
            if current_talk_num is not None and current_talk_lines:
                talk_sections.append((current_talk_num, current_talk_lines))
            current_talk_num = int(m.group(1))
            current_talk_lines = [line]
        elif current_talk_num is not None:
            if "Rules for the parallel" not in line:
                current_talk_lines.append(line)

    if current_talk_num is not None and current_talk_lines:
        talk_sections.append((current_talk_num, current_talk_lines))

    # Parse talks
    talks = []
    for talk_num, tlines in talk_sections:
        # Accumulate text per room column
        room_cols = [[] for _ in range(num_rooms)]

        for line in tlines:
            cols = split_into_columns(line, num_rooms)
            for ri in range(num_rooms):
                if ri + 1 < len(cols):
                    txt = cols[ri + 1]
                    if txt:
                        room_cols[ri].append(txt)

        talk_entry = {
            "talk_number": talk_num,
            "title": "",  # will be set from first room
            "authors": {},
        }

        for ri, rname in enumerate(rooms):
            full_text = "\n".join(room_cols[ri])

            # Find author split: name line followed by (institution) line
            m = re.search(
                r"\n\s*([A-Z\u00C0-\u024F\u0150\u0151\u0170\u0171][a-zA-Z\u00C0-\u024F.\-'’]*(?:\s+[A-Z\u00C0-\u024F\u0150\u0151\u0170\u0171][a-zA-Z\u00C0-\u024F.\-'’]*)+)"
                r"\s*\n\s*\(",
                full_text,
            )

            title = full_text
            author_name = ""
            author_inst = ""

            if m:
                split_pos = m.start()
                title = full_text[:split_pos].strip()
                author_block = full_text[split_pos:].strip()

                name_match = re.match(r"([^(]+?)\s*\(", author_block, re.DOTALL)
                if name_match:
                    author_name = name_match.group(1).strip()
                    inst_parts = re.findall(r"\(([^)]*)\)", author_block)
                    combined_inst = " ".join(inst_parts)
                    author_inst = re.sub(r"\s+", " ", combined_inst).strip()

            # Clean title
            title = re.sub(r"\s+", " ", title).strip()
            title = title.strip(".,;:")
            title = re.sub(r"^Talk\s+\d+\s*", "", title).strip()

            talk_entry["authors"][rname] = {
                "name": author_name,
                "institution": author_inst,
                "is_presenter": True,
            }

            if not talk_entry["title"] and title:
                talk_entry["title"] = title

        # If still no title, try using the first room's full text
        if not talk_entry["title"] and room_cols:
            first_text = " ".join(room_cols[0])
            talk_entry["title"] = re.sub(r"\s+", " ", first_text).strip()

        if talk_entry["authors"] or talk_entry["title"]:
            talks.append(talk_entry)

    # Build room details
    room_details = []
    for rname in rooms:
        floor = ROOM_FLOORS.get(rname, "")
        for line in block_lines:
            if rname in line and "Floor" in line:
                floor = line.strip()
                break
        room_details.append({
            "name": rname,
            "floor": floor,
            "theme": themes.get(rname, ""),
        })

    return {
        "session_number": snum,
        "day": dnum,
        "date": DAY_DATES[dnum],
        "time_start": SESSION_SLOTS.get(snum, ("", ""))[0],
        "time_end": SESSION_SLOTS.get(snum, ("", ""))[1],
        "rooms": room_details,
        "talks": talks,
    }


SESSION_SLOTS = {
    1: ("9:00", "10:30"), 2: ("10:50", "12:20"),
    3: ("13:20", "14:50"), 4: ("15:10", "16:40"),
    5: ("9:00", "10:30"), 6: ("10:50", "12:20"),
    7: ("13:20", "14:50"), 8: ("15:10", "16:40"),
    9: ("9:00", "10:30"), 10: ("10:50", "12:20"),
}


def extract_keynotes(lines):
    """Extract keynote speakers."""
    keynotes = []
    i = 0
    while i < len(lines):
        if "Keynote Speech" in lines[i]:
            name = ""
            inst = ""
            for j in range(i + 1, min(i + 10, len(lines))):
                nl = lines[j].strip()
                if not nl or nl.startswith("Day") or "Keynote" in nl:
                    continue
                if not name:
                    name = nl
                elif not inst:
                    inst = nl
                else:
                    break
            if name:
                keynotes.append({"name": name, "institution": inst})
            i = j
        i += 1
    if not keynotes:
        keynotes = [
            {"name": "Manuel Arellano", "institution": "CEMFI"},
            {"name": "Giacomo Ponzetto", "institution": "CREI and Universitat Pompeu Fabra"},
        ]
    return keynotes


def extract_iberdrola(lines):
    """Extract Iberdrola session."""
    for i, line in enumerate(lines):
        if "Iberdrola" in line and "session" in line.lower():
            title = ""
            speaker = ""
            for j in range(i, min(i + 15, len(lines))):
                stripped = lines[j].strip()
                if stripped.startswith("“") or stripped.startswith('"'):
                    title = stripped.strip('"“”')
                elif "Speaker:" in stripped:
                    speaker = stripped.replace("Speaker:", "").strip()
                elif "Marcelo Rabinovich" in stripped and not speaker:
                    speaker = stripped.strip()
            if not title:
                title = "Remuneration Frameworks in Energy Networks: Practical Implementation and Consequences"
            if not speaker:
                speaker = "Marcelo Rabinovich - Nera"
            return {
                "session": "Iberdrola Session", "day": 3,
                "date": "2026-05-20", "time": "12:30-13:15",
                "room": "Arriaga", "floor": "2nd Floor",
                "title": title, "speaker": speaker,
            }
    return {
        "session": "Iberdrola Session", "day": 3, "date": "2026-05-20",
        "time": "12:30-13:15", "room": "Arriaga", "floor": "2nd Floor",
        "title": "Remuneration Frameworks in Energy Networks: Practical Implementation and Consequences",
        "speaker": "Marcelo Rabinovich - Nera",
    }


def main():
    print(f"Reading {INPUT_FILE}...")
    lines = read_lines()
    print(f"Read {len(lines)} lines.")

    blocks = find_session_blocks(lines)
    print(f"Found {len(blocks)} session blocks.")

    sessions = []
    all_participants = {}
    all_papers = []

    for snum, dnum, tstart, tend, block in blocks:
        print(f"  Parsing Session {snum} (Day {dnum}, {tstart}-{tend})...")
        try:
            session = parse_session(snum, dnum, block)
            sessions.append(session)

            for talk in session["talks"]:
                for rname, ainfo in talk["authors"].items():
                    name = ainfo["name"].strip()
                    inst = ainfo["institution"].strip()
                    if not name:
                        continue
                    pid = f"{name}|{inst}"
                    if pid not in all_participants:
                        all_participants[pid] = {
                            "name": name, "institution": inst,
                            "role": "Presenter", "is_presenter": True,
                            "papers": [], "paper_titles": [],
                        }
                    title = talk.get("title", "").strip()
                    if title and title not in all_participants[pid]["paper_titles"]:
                        all_participants[pid]["paper_titles"].append(title)

        except Exception as e:
            print(f"  ERROR: {e}")

    # Keynotes
    keynotes = extract_keynotes(lines)
    for kn in keynotes:
        pid = f"{kn['name']}|{kn['institution']}"
        if pid not in all_participants:
            all_participants[pid] = {
                "name": kn["name"], "institution": kn["institution"],
                "role": "Keynote Speaker", "is_presenter": True,
                "papers": [], "paper_titles": [],
            }

    # Iberdrola
    iberdrola = extract_iberdrola(lines)
    print(f"  Iberdrola Session: {iberdrola['speaker']}")

    speaker_full = iberdrola["speaker"]
    if " - " in speaker_full:
        sp_name, sp_inst = speaker_full.split(" - ", 1)
    else:
        sp_name, sp_inst = speaker_full, "Nera"

    pid = f"{sp_name}|{sp_inst}"
    if pid not in all_participants:
        all_participants[pid] = {
            "name": sp_name, "institution": sp_inst,
            "role": "Speaker (Iberdrola Session)", "is_presenter": True,
            "papers": [], "paper_titles": [iberdrola["title"]],
        }

    # Build papers
    paper_id = 1
    for session in sessions:
        for talk in session["talks"]:
            authors_list = []
            for rname, ainfo in talk["authors"].items():
                if ainfo["name"].strip():
                    authors_list.append({
                        "name": ainfo["name"],
                        "institution": ainfo["institution"],
                        "room": rname,
                    })
            if authors_list and talk["title"].strip():
                all_papers.append({
                    "paper_id": f"P{paper_id:04d}",
                    "title": talk["title"],
                    "session": f"Parallel Session {session['session_number']}",
                    "session_number": session["session_number"],
                    "day": session["day"],
                    "date": session["date"],
                    "time_start": session["time_start"],
                    "time_end": session["time_end"],
                    "authors": authors_list,
                })
                paper_id += 1

    # Iberdrola paper
    all_papers.append({
        "paper_id": f"P{paper_id:04d}",
        "title": iberdrola["title"],
        "session": "Iberdrola Session", "session_number": None,
        "day": 3, "date": "2026-05-20",
        "time_start": "12:30", "time_end": "13:15",
        "authors": [{"name": sp_name, "institution": sp_inst, "room": "Arriaga"}],
    })

    # Load existing
    existing = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            pass

    output = OrderedDict()

    conf = OrderedDict()
    conf["name"] = "European Association of Young Economists Annual Meeting 2026"
    conf["short_name"] = "EAYE 2026"
    conf["year"] = 2026
    conf["edition"] = "30th Anniversary Edition"
    conf["start_date"] = "2026-05-18"
    conf["end_date"] = "2026-05-20"
    conf["location"] = "Bilbao, Spain"
    conf["venue"] = "Bizkaia Aretoa"
    conf["city"] = "Bilbao"
    conf["country"] = "Spain"
    conf["website"] = "https://www.eaye.info/"
    conf["program_url"] = "https://www.eaye.info/eayeam/2026-edition/program-2026"
    conf["organizer"] = "European Association of Young Economists (EAYE)"
    conf["description"] = (
        "The European Association of Young Economists (EAYE) Annual Meeting, "
        "formerly called the Spring Meeting of Young Economists (SMYE). "
        "The 2026 edition is hosted by the University of the Basque Country in Bilbao, Spain."
    )
    conf["extras"] = OrderedDict()
    conf["extras"]["former_name"] = "Spring Meeting of Young Economists (SMYE)"
    conf["extras"]["host"] = "University of the Basque Country"
    conf["extras"]["keynote_speakers"] = keynotes
    conf["extras"]["iberdrola_session"] = iberdrola

    if existing and "conference" in existing and "extras" in existing["conference"]:
        for k, v in existing["conference"]["extras"].items():
            if k not in conf["extras"]:
                conf["extras"][k] = v

    output["conference"] = conf
    output["scrape_metadata"] = {
        "scraped_at": "2026-06-13T00:00:00",
        "source_url": "https://www.eaye.info/",
        "program_url": "https://www.eaye.info/eayeam/2026-edition/program-2026",
        "script_name": "scrape_mye.py",
        "program_available": True,
        "program_type": "pdf_extract",
        "notes": "Program parsed from PDF text extract.",
        "errors": [],
    }

    sessions_out = []
    for session in sorted(sessions, key=lambda x: x["session_number"]):
        s = OrderedDict()
        s["session_number"] = session["session_number"]
        s["name"] = f"Parallel Session {session['session_number']}"
        s["day"] = session["day"]
        s["date"] = session["date"]
        s["time_start"] = session["time_start"]
        s["time_end"] = session["time_end"]
        s["rooms"] = []
        for rd in session["rooms"]:
            s["rooms"].append(OrderedDict([
                ("name", rd["name"]), ("floor", rd["floor"]), ("theme", rd["theme"]),
            ]))
        s["talks"] = []
        for talk in session["talks"]:
            t = OrderedDict()
            t["talk_number"] = talk["talk_number"]
            t["title"] = talk["title"]
            t["authors"] = OrderedDict()
            for rname, ainfo in talk["authors"].items():
                t["authors"][rname] = OrderedDict([
                    ("name", ainfo["name"]),
                    ("institution", ainfo["institution"]),
                    ("is_presenter", ainfo["is_presenter"]),
                ])
            s["talks"].append(t)
        sessions_out.append(s)

    output["sessions"] = sessions_out
    output["participants"] = sorted(
        [v for v in all_participants.values()],
        key=lambda x: x["name"],
    )
    all_papers.sort(key=lambda x: (x["session_number"] or 99, x["paper_id"]))
    output["papers"] = all_papers
    output["total_sessions"] = len(sessions_out)
    output["total_papers"] = len(all_papers)
    output["total_participants"] = len(all_participants)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Written {OUTPUT_FILE}")
    print(f"   Sessions: {output['total_sessions']}")
    print(f"   Papers:   {output['total_papers']}")
    print(f"   Participants: {output['total_participants']}")


if __name__ == "__main__":
    main()
