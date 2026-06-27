#!/usr/bin/env python3
"""
MYE/EAYE 2026 program parser — column-based approach.
Parses the PDF-extracted text from /tmp/mye_program.txt using column splitting.
"""
import json, os, re

INPUT = "/tmp/mye_program.txt"
OUTPUT = os.path.expanduser("~/economics-conferences/mye2026/data.json")

with open(INPUT) as f:
    content = f.read()

content = content.replace('\f', '\n')
lines = content.split('\n')

DAY_DATES = {1: "2026-05-18", 2: "2026-05-19", 3: "2026-05-20"}
ROOM_FLOORS = {
    "Oteiza": "1st Floor", "Etxepare": "1st Floor",
    "Arriaga": "2nd Floor", "Laboa": "2nd Floor",
    "Elhuyar": "Ground Floor",
}

def split_columns(line, num_cols):
    """Split a line into N columns by 3+ spaces. Returns list of length num_cols."""
    parts = re.split(r'  {3,}', line)
    result = [p.strip() for p in parts]
    # Pad or trim to num_cols
    while len(result) < num_cols:
        result.append('')
    return result[:num_cols]

# Find all session blocks
# Session starts with "Parallel Session N (Day D) HH:MM - HH:MM"
session_pattern = re.compile(r'^Parallel Session (\d+) \(Day (\d+)\)\s+(\d+:\d+)\s*[-–]\s*(\d+:\d+)\s*$')
session_breaks = []

for i, line in enumerate(lines):
    m = session_pattern.match(line.strip())
    if m:
        session_breaks.append((i, int(m.group(1)), int(m.group(2)), m.group(3), m.group(4)))

print(f"Found {len(session_breaks)} sessions")

sessions_data = []
participants_dict = {}

for si in range(len(session_breaks)):
    start, sess_num, day, t_start, t_end = session_breaks[si]
    end = session_breaks[si + 1][0] if si + 1 < len(session_breaks) else len(lines)
    
    block = lines[start:end]
    date_str = DAY_DATES[day]
    time_str = f"{t_start} - {t_end}"
    
    # Determine rooms: Day 1 = 4 rooms, Day 2-3 = 5 rooms
    room_names = ["Oteiza", "Etxepare", "Arriaga", "Laboa"]
    if day in [2, 3]:
        room_names = ["Elhuyar", "Oteiza", "Etxepare", "Arriaga", "Laboa"]
    num_rooms = len(room_names)
    
    # Extract column text for each room
    # Each column is the text under that room's header
    room_texts = {r: [] for r in room_names}
    room_themes = {r: "" for r in room_names}
    current_theme_line = True  # First line after header is session theme
    
    # Find room header line to determine column boundaries
    room_header_line = None
    theme_done = False
    
    for line in block:
        stripped = line.rstrip()
        
        # Check if this line has the room names
        if any(rn in stripped for rn in room_names) and 'Floor' in stripped:
            cols = split_columns(stripped, num_rooms)
            for ri, rn in enumerate(room_names):
                if ri < len(cols) and rn in cols[ri]:
                    room_header_line = True
            continue
        
        # If we have room names in previous line, this might be floor info
        if room_header_line and all(rd in stripped for rd in ['Floor'] if 'Floor' in stripped):
            room_header_line = False
            theme_done = False
            continue
        
        # Check if line has data already split into columns
        cols = split_columns(stripped, num_rooms)
        has_content = any(c.strip() for c in cols)
        
        if not has_content:
            continue
        
        # Skip rules lines
        if 'Rules for the parallel' in stripped:
            continue
        
        # Detect Talk markers
        has_talk = any(re.match(r'^Talk\s+\d+', c.strip()) for c in cols)
        
        if not theme_done and not has_talk:
            # These are session theme lines
            for ri, rn in enumerate(room_names):
                if ri < len(cols):
                    room_themes[rn] += ' ' + cols[ri].strip()
            continue
        
        if has_talk:
            theme_done = True
        
        # Add to room texts
        for ri, rn in enumerate(room_names):
            if ri < len(cols) and cols[ri].strip():
                room_texts[rn].append(cols[ri].strip())
    
    # Clean up room themes
    for rn in room_names:
        room_themes[rn] = re.sub(r'\s+', ' ', room_themes[rn]).strip()
        # Remove leading "Session" if present
        room_themes[rn] = re.sub(r'^Session\s*:?\s*', '', room_themes[rn]).strip()
    
    # Now parse each room's text for Talk 1/2/3
    for ri, rn in enumerate(room_names):
        texts = room_texts[rn]
        theme = room_themes[rn]
        
        # Combine theme into session title
        session_title = f"Parallel Session {sess_num}: {rn}"
        if theme:
            session_title += f" — {theme[:100]}"
        
        # Extract talks: patterns are Talk N: title, then author, then institution
        talks = []
        current_talk = None
        talk_buffer = []
        
        for t in texts:
            talk_m = re.match(r'^Talk\s+(\d+)\s*:?\s*(.*)', t)
            if talk_m:
                if current_talk is not None and talk_buffer:
                    talks.append((current_talk, talk_buffer))
                current_talk = int(talk_m.group(1))
                rest = talk_m.group(2).strip()
                talk_buffer = [rest] if rest else []
                continue
            
            # Check if this line contains a potential author (has institution in parentheses)
            if talk_buffer is not None:
                talk_buffer.append(t)
        
        if current_talk is not None and talk_buffer:
            talks.append((current_talk, talk_buffer))
        
        # Now parse each talk into paper title, author, institution
        session_papers = []
        
        for talk_num, talk_lines in talks:
            # Join and split on institution markers
            full_text = ' '.join(talk_lines)
            full_text = re.sub(r'\s+', ' ', full_text).strip()
            
            # Try to extract author + institution pattern
            # Author: "Name (Institution)" or "Name (Institution1) (Institution2)"
            name_inst_pairs = re.findall(r'([A-Z][a-zéèêëàâîïôùûüñçÉÈÊËÀÂÎÏÔÙÛÜÑÇ\-]+(?:\s+[A-Z][a-zéèêëàâîïôùûüñçÉÈÊËÀÂÎÏÔÙÛÜÑÇ\-]+)*)\s*\(([^)]+)\)', full_text)
            
            # Heuristic: author name followed by institution in parentheses
            # But titles also contain parentheses! So we need smarter detection
            
            # Split the text into segments separated by institution-parentheses
            # Everything before the first author-line segment is the paper title
            
            # Find lines that look like author lines: have institution in parentheses,
            # are relatively short (not a paper title)
            
            # Actually simpler: in the data, paper titles are long, author+inst lines are shorter
            # and have institution in parentheses
            
            title_parts = []
            author_name = ''
            author_inst = ''
            
            for tl in talk_lines:
                tl_stripped = tl.strip()
                # Skip if too short
                if len(tl_stripped) < 3:
                    continue
                
                # Check for institution pattern
                inst_match = re.search(r'\(([A-Za-z].*?)\)', tl_stripped)
                
                if inst_match:
                    # Could be author line or title with parenthetical
                    # Author lines have the institution as the MAIN content
                    # Title parentheticals are usually short like "(Day 1)" or contain specific terms
                    
                    # Heuristic: if the line starts with/contains a name pattern before the parens
                    # AND the parens contain an institution, it's an author line
                    before_paren = tl_stripped[:inst_match.start()].strip()
                    inst_text = inst_match.group(1)
                    
                    # Institution indicators: University, School, College, Institute, Bank, etc.
                    inst_indicators = ['University', 'School', 'College', 'Institute', 'Bank', 'Fund',
                                       'CEMFI', 'EIEF', 'CREST', 'CERGE', 'EI', 'NUS', 'UPF', 'BSE',
                                       'Centre', 'Center', 'Laboratory', 'Laboratoire',
                                       'Department', 'Faculty', 'Federal', 'National']
                    
                    is_institution = any(ind in inst_text for ind in inst_indicators)
                    
                    if is_institution and len(before_paren) > 0 and len(before_paren) < 60:
                        # This is an author line
                        if not author_name:
                            author_name = before_paren
                            author_inst = inst_text
                            # The title is everything accumulated so far
                            if not title_parts:
                                # Title may be in the remaining text
                                pass
                    else:
                        # This might be a title with parenthetical (e.g., "Event Study (Day 1)")
                        title_parts.append(tl_stripped)
                else:
                    title_parts.append(tl_stripped)
            
            if not title_parts and not author_name:
                # Fallback: try splitting differently
                # The first two long lines are title, last two are author + inst
                non_empty = [t for t in talk_lines if len(t.strip()) > 5]
                if len(non_empty) >= 3:
                    title_parts = [non_empty[0], non_empty[1]] if len(non_empty) >= 2 else [non_empty[0]]
                    author_line = non_empty[-1]
                    # Check if author line has institution
                    inst_m = re.search(r'\(([^)]+)\)', author_line)
                    if inst_m:
                        author_name = author_line[:inst_m.start()].strip()
                        author_inst = inst_m.group(1)
                    else:
                        author_name = author_line
                elif len(non_empty) >= 2:
                    title_parts = [non_empty[0]]
                    author_line = non_empty[-1]
                    inst_m = re.search(r'\(([^)]+)\)', author_line)
                    if inst_m:
                        author_name = author_line[:inst_m.start()].strip()
                        author_inst = inst_m.group(1)
                    else:
                        author_name = author_line
                elif len(non_empty) == 1:
                    title_parts = [non_empty[0]]
            
            # Clean up
            paper_title = ' '.join(tp for tp in title_parts if tp).strip()
            paper_title = re.sub(r'\s+', ' ', paper_title).strip()
            # Remove trailing "|" or other artifacts
            paper_title = paper_title.rstrip('|')
            
            author_name = author_name.strip().rstrip(',').strip()
            # Clean author name (remove leading/trailing non-alpha)
            author_name = re.sub(r'^[^A-Za-zÀ-ÖØ-öø-ÿ]+', '', author_name)
            author_name = re.sub(r'[^A-Za-zÀ-ÖØ-öø-ÿ\s\-\.\']+$', '', author_name).strip()
            author_inst = re.sub(r'\s+', ' ', author_inst).strip()
            
            if paper_title and author_name:
                paper = {
                    'title': paper_title,
                    'authors': [author_name],
                    'presenter': author_name,
                }
                session_papers.append(paper)
                
                # Track participant
                key = author_name.lower()
                if key not in participants_dict:
                    participants_dict[key] = {
                        'name': author_name,
                        'institution': author_inst,
                        'is_presenter': True,
                        'papers': [],
                    }
                participants_dict[key]['papers'].append(paper_title)
        
        if session_papers:
            sessions_data.append({
                'session_title': session_title,
                'date': date_str,
                'time': time_str,
                'room': f"{rn} ({ROOM_FLOORS.get(rn, '')})",
                'papers': session_papers,
            })
        
        print(f"  Room {rn}: {len(session_papers)} papers")

print(f"\nTotal sessions: {len(sessions_data)}")
print(f"Total participants: {len(participants_dict)}")
total_papers = sum(len(s['papers']) for s in sessions_data)
print(f"Total papers: {total_papers}")

# Build final data.json
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
        "notes": f"Parsed from official program PDF. {len(sessions_data)} sessions, {total_papers} papers, {len(participants_dict)} participants."
    },
    "sessions": sessions_data,
    "participants": list(participants_dict.values()),
}

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved: {OUTPUT}")
