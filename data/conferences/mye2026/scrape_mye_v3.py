#!/usr/bin/env python3
"""
MYE/EAYE 2026 program parser — PyMuPDF position-based approach v2.
Uses first room's Talk N positions to find corresponding titles in other rooms.
"""
import json, os, re
import fitz

PDF_PATH = "/tmp/mye_program.pdf"
OUTPUT = os.path.expanduser("~/economics-conferences/mye2026/data.json")

# Room column x-ranges (calibrated from PDF text positions)
ROOM_X_RANGES_D1 = {
    "Oteiza": (55, 248), "Etxepare": (248, 345),
    "Arriaga": (345, 440), "Laboa": (440, 550),
}
ROOM_X_RANGES_D23 = {
    "Elhuyar": (100, 224), "Oteiza": (224, 300),
    "Etxepare": (300, 383), "Arriaga": (383, 462),
    "Laboa": (462, 550),
}
DAY_DATES = {1: "2026-05-18", 2: "2026-05-19", 3: "2026-05-20"}
ROOM_FLOORS = {
    "Oteiza": "1st Floor", "Etxepare": "1st Floor",
    "Arriaga": "2nd Floor", "Laboa": "2nd Floor",
    "Elhuyar": "Ground Floor",
}

def extract_text(block):
    if block['type'] != 0:
        return ''
    return ' '.join(
        ' '.join(s['text'] for s in line['spans'])
        for line in block['lines']
    )

def get_room_ranges(day):
    return ROOM_X_RANGES_D23 if day in [2, 3] else ROOM_X_RANGES_D1

def assign_blocks_to_rooms(blocks, day):
    ranges = get_room_ranges(day)
    rooms = {r: [] for r in ranges}
    for b in blocks:
        if b['type'] != 0:
            continue
        bbox = b['bbox']
        x_center = (bbox[0] + bbox[2]) / 2
        for room, (xmin, xmax) in ranges.items():
            if xmin <= x_center <= xmax:
                rooms[room].append({
                    'text': extract_text(b),
                    'y': bbox[1],
                    'y_bottom': bbox[3],
                })
                break
    for r in rooms:
        rooms[r].sort(key=lambda x: x['y'])
    return rooms

def parse_page(page, day, date_str, time_str, sess_num):
    blocks = page.get_text('dict')['blocks']
    rooms = assign_blocks_to_rooms(blocks, day)
    room_names = list(get_room_ranges(day).keys())
    
    # From the first room (index 0), find Talk N positions
    first_room_name = room_names[0]
    first_room = rooms[first_room_name]
    
    talk_y_positions = {}  # talk_num -> y
    for b in first_room:
        m = re.match(r'^Talk\s+(\d+)', b['text'].strip())
        if m:
            talk_y_positions[int(m.group(1))] = b['y']
    
    if not talk_y_positions:
        print(f"  Session {sess_num}: No Talk markers found in first room!")
        return []
    
    # For each room, extract session theme and papers
    sessions_out = []
    
    for room_name in room_names:
        room = rooms[room_name]
        if len(room) < 3:
            continue
        
        # Session theme: blocks between room info and Talk 1 (from first room)
        first_talk_y = min(talk_y_positions.values())
        theme_parts = []
        for b in room:
            t = b['text'].strip()
            if not t:
                continue
            # Skip room name/floor lines
            if any(r in t for r in ['Room,', 'Floor']) and len(t) < 20:
                continue
            if t.startswith('Rules'):
                continue
            # Theme is between floor info and first talk title
            if b['y'] < first_talk_y and b['y'] > 95:
                theme_parts.append(t)
        
        theme = re.sub(r'\s+', ' ', ' '.join(theme_parts)).strip()
        theme = re.sub(r'^Session\s*:?\s*', '', theme).strip()
        
        # Extract papers by matching talk y-positions
        papers = []
        for talk_num in sorted(talk_y_positions.keys()):
            talk_y = talk_y_positions[talk_num]
            
            # Find the title block(s) for this talk in this room
            title_blocks = [b for b in room if abs(b['y'] - talk_y) < 15]
            title_text = ''
            if title_blocks:
                title_text = title_blocks[0]['text'].strip()
            
            if not title_text:
                continue
            
            # For first room, remove "Talk N " prefix
            if room_name == first_room_name:
                title_text = re.sub(r'^Talk\s+\d+\s*:?\s*', '', title_text).strip()
            
            # Find author+institution block (between this talk and next talk)
            next_talk_y = float('inf')
            for tn in sorted(talk_y_positions.keys()):
                if talk_y_positions[tn] > talk_y:
                    next_talk_y = talk_y_positions[tn]
                    break
            
            author_blocks = [b for b in room if b['y'] > talk_y + 15 and b['y'] < next_talk_y - 10]
            
            author_name = ''
            author_inst = ''
            for ab in author_blocks:
                t = ab['text'].strip()
                # Find institution in parentheses
                inst_m = re.search(r'\(([^)]+)\)', t)
                if inst_m and len(t) < 80:
                    # Check it's an institution (not a location reference)
                    inst_text = inst_m.group(1)
                    inst_indicators = ['University', 'School', 'College', 'Institute', 'Bank', 
                                       'Fund', 'CEMFI', 'EIEF', 'CREST', 'CERGE', 'Centre',
                                       'Center', 'Laboratory', 'Federal', 'National', 'Bocconi',
                                       'Pompeu', 'Carlos', 'Paris-Saclay', 'London', 'Bonn',
                                       'St. Gallen', 'CREST']
                    if any(ind in inst_text for ind in inst_indicators):
                        author_name = t[:inst_m.start()].strip().rstrip(',').strip()
                        author_inst = inst_text
                        break
            
            # Fallback: author might be on the very next line after a multi-line title
            if not author_name:
                for ab in author_blocks[:2]:
                    t = ab['text'].strip()
                    inst_m = re.search(r'\(([^)]+)\)', t)
                    if inst_m:
                        author_name = t[:inst_m.start()].strip().rstrip(',').strip()
                        author_inst = inst_m.group(1)
                        break
            
            if title_text and author_name:
                author_name = re.sub(r'\s+', ' ', author_name).strip()
                # Sometimes author name is on multiple consecutive blocks
                # Join multi-part names
                if len(author_name) < 3 and len(author_blocks) > 1:
                    for extra in author_blocks[1:3]:
                        extra_t = extra['text'].strip()
                        if not re.search(r'\(', extra_t):
                            author_name += ' ' + extra_t
                        else:
                            break
                    author_name = re.sub(r'\s+', ' ', author_name).strip()
                
                papers.append({
                    'title': re.sub(r'\s+', ' ', title_text).strip(),
                    'author': author_name,
                    'institution': author_inst,
                })
        
        if papers:
            session_title = f"Parallel Session {sess_num}: {room_name}"
            if theme:
                session_title += f" — {theme[:120]}"
            
            sessions_out.append({
                'session_title': session_title,
                'date': date_str,
                'time': time_str,
                'room': f"{room_name} ({ROOM_FLOORS.get(room_name, '')})",
                'papers': [{'title': p['title'], 'authors': [p['author']], 'presenter': p['author']} for p in papers],
                '_authors': [(p['author'], p['institution'], p['title']) for p in papers],
            })
    
    return sessions_out

def main():
    doc = fitz.open(PDF_PATH)
    print(f"PDF pages: {len(doc)}")
    
    all_sessions = []
    participants_dict = {}
    
    for page_num in range(4, min(15, len(doc))):
        page = doc[page_num]
        
        first_text = extract_text(page.get_text('dict')['blocks'][0]) if page.get_text('dict')['blocks'] else ''
        m = re.search(r'Parallel Session (\d+)\s*\(Day (\d+)\)\s+(\d+:\d+)\s*[-–]\s+(\d+:\d+)', first_text)
        if not m:
            print(f"  Page {page_num+1}: No session header")
            continue
        
        sess_num, day, t_start, t_end = int(m.group(1)), int(m.group(2)), m.group(3), m.group(4)
        date_str = DAY_DATES[day]
        time_str = f"{t_start} - {t_end}"
        
        print(f"Page {page_num+1}: Session {sess_num} (Day {day})")
        sessions = parse_page(page, day, date_str, time_str, sess_num)
        
        for s in sessions:
            # Extract participants from _authors
            for author, inst, title in s.pop('_authors', []):
                key = author.lower()
                if key not in participants_dict:
                    participants_dict[key] = {
                        'name': author, 'institution': inst,
                        'is_presenter': True, 'papers': [],
                    }
                if title not in participants_dict[key]['papers']:
                    participants_dict[key]['papers'].append(title)
        
        all_sessions.extend(sessions)
        print(f"  → {len(sessions)} rooms with papers")
    
    total_papers = sum(len(s['papers']) for s in all_sessions)
    print(f"\nTotal sessions: {len(all_sessions)}")
    print(f"Total papers: {total_papers}")
    print(f"Total participants: {len(participants_dict)}")
    
    data = {
        "conference": {
            "name": "EAYE Annual Meeting (formerly Spring Meeting of Young Economists)",
            "short_name": "MYE 2026",
            "year": 2026,
            "start_date": "2026-05-18",
            "end_date": "2026-05-20",
            "location": "Bilbao, Spain",
            "extras": {
                "former_name": "Spring Meeting of Young Economists (SMYE)",
                "host": "University of the Basque Country",
                "venue": "Bizkaia Aretoa",
                "keynote_speakers": [
                    {"name": "Manuel Arellano", "institution": "CEMFI"},
                    {"name": "Giacomo Ponzetto", "institution": "CREI and Universitat Pompeu Fabra"}
                ],
                "organizer": "European Association of Young Economists (EAYE)",
            }
        },
        "scrape_metadata": {
            "scraped_at": "2026-06-13",
            "source_url": "https://www.uik.eus/sites/default/files/programa/2717-es-e51-program-eaye-2026-v11052026-redcido.pdf",
            "program_available": True,
            "program_type": "pdf",
            "notes": f"{len(all_sessions)} sessions, {total_papers} papers, {len(participants_dict)} participants"
        },
        "sessions": all_sessions,
        "participants": list(participants_dict.values()),
    }
    
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Saved: {OUTPUT}")
    
    # Show sample
    for s in all_sessions[:3]:
        print(f"\n{s['session_title'][:60]}")
        for p in s['papers'][:2]:
            print(f"  {p['title'][:50]} — {p['authors'][0]}")

if __name__ == '__main__':
    main()
