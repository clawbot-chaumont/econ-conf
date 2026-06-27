#!/usr/bin/env python3
"""
Custom parser for AFFI 2026 program PDF.
Uses precise line-level extraction from PyMuPDF get_text("dict").
"""

import json, os, re, sys
from collections import Counter, defaultdict

# Column boundaries
TITLE_MAX_X = 210
SPEAKER_MAX_X = 268
AUTHOR_MIN_X = 265
DISCUSSANT_MIN_X = 498

def get_lines(page):
    """Extract lines with spans from a page."""
    lines = []
    for block in page.get_text("dict")['blocks']:
        if block['type'] != 0:
            continue
        for line in block['lines']:
            spans = [(s['bbox'][0], s['text']) for s in line['spans'] if s['text'].strip()]
            if spans:
                lines.append({
                    'y': line['bbox'][1],
                    'x0': min(s[0] for s in spans),
                    'x1': max(s[0] + len(s[1]) * 5 for s in spans),  # approx
                    'spans': spans,
                    'text': ' '.join(s[1] for s in spans)
                })
    lines.sort(key=lambda l: (l['y'], l['x0']))
    return lines

def is_letter_spaced(text):
    """Detect letter-spaced text (each char is separate span)."""
    words = text.split()
    if len(words) < 3:
        return False
    singles = sum(1 for w in words if len(w) == 1 and w.isalpha())
    return singles > len(words) * 0.25

def classify_line(line):
    """Classify a line based on its x-position of spans."""
    x0 = line['x0']
    text = line['text']
    
    if x0 < TITLE_MAX_X:
        return 'title'
    elif x0 < AUTHOR_MIN_X:
        return 'speaker'
    elif x0 < DISCUSSANT_MIN_X:
        return 'author'
    else:
        return 'discussant'

def parse_affi_pdf(pdf_path):
    """Parse the AFFI 2026 PDF program."""
    import fitz
    
    doc = fitz.open(pdf_path)
    all_sessions = []
    current_session = None
    
    # Pages 5-21 contain program content (0-indexed 4-20)
    # Skip: page 7 (keynote), pages 14-15 (restaurant info + keynote 2)
    skip_pages = {6, 13, 14}  # 0-indexed
    for pnum in range(4, min(21, len(doc))):
        if pnum in skip_pages:
            continue
        page = doc[pnum]
        lines = get_lines(page)
        
        i = 0
        while i < len(lines):
            line = lines[i]
            text = line['text'].strip()
            x0 = line['x0']
            
            # Skip letter-spaced header lines (day, time, "Parallel sessions")
            if is_letter_spaced(text):
                i += 1
                continue
            
            # Skip empty/short lines
            if len(text) < 4:
                i += 1
                continue
            
            # Skip table headers
            if text in ['Title', 'Speaker', 'Authors', 'Discussant']:
                i += 1
                continue
            
            # Skip day/time info lines
            if re.match(r'^(Monday|Tuesday|Wednesday|Thursday|Friday)', text):
                i += 1
                continue
            if re.match(r'^\d{1,2}:\d{2}\s*[ap]\.?m', text):
                i += 1
                continue
            
            # Skip keynote/LECTURE lines
            if re.match(r'^(LECTURE|PROF\.|KEYNOTE)', text):
                i += 1
                continue
            if 'ICREA' in text or 'Professor' in text or 'European University' in text:
                i += 1
                continue
            if 'Adjunct Professor' in text or 'Norwegian School' in text:
                i += 1
                continue
            
            # Skip "PhD Workshop" and "Keynote speakers" headers
            if text in ['PhD Workshop', 'Keynote speakers'] or text.startswith('PhD\n'):
                i += 1
                continue
            
            # CHECK: Is this a session header?
            if is_letter_spaced(text):
                i += 1
                continue
            
            if '|' in text and 'Chairman' in text:
                # Found a session header
                if current_session and current_session.get('papers'):
                    all_sessions.append(current_session)
                
                # Extract session info
                parts = text.split('|')
                session_name = parts[0].strip()
                rest = parts[1] if len(parts) > 1 else ''
                
                room_m = re.search(r'Room\s*(\d+[A-Za-z]*)', rest)
                room = f"Room {room_m.group(1)}" if room_m else ''
                
                chair_m = re.search(r'Chairman:\s*(.+)$', rest)
                chair = chair_m.group(1).strip() if chair_m else ''
                
                current_session = {
                    'session_title': session_name,
                    'room': room,
                    'chair': chair,
                    'papers': []
                }
                i += 1
                continue
            
            # At this point, we're in paper content territory
            if not current_session:
                i += 1
                continue
            
            # Classify this line
            cat = classify_line(line)
            
            if cat == 'title':
                # New paper starts
                # First, collect the title (may span multiple lines)
                title_parts = [text]
                speaker = ''
                author_text = ''
                discussant = ''
                
                j = i + 1
                # Collect continuation title lines
                while j < len(lines):
                    nxt = lines[j]
                    nxt_cat = classify_line(nxt)
                    nxt_text = nxt['text'].strip()
                    
                    # If next line is also a title and close in y, it's continuation
                    if nxt_cat == 'title' and (nxt['y'] - lines[j-1]['y']) < 30:
                        title_parts.append(nxt_text)
                        j += 1
                    else:
                        break
                
                title = ' '.join(t for t in title_parts if t)
                
                # Now collect speaker, author, discussant from subsequent lines
                paper_lines = []
                while j < len(lines):
                    nxt = lines[j]
                    nxt_cat = classify_line(nxt)
                    nxt_text = nxt['text'].strip()
                    
                    # Skip if it's a letter-spaced line  
                    if is_letter_spaced(nxt_text):
                        j += 1
                        continue
                    
                    # Stop if we hit a new session header or a new paper (title-only line)
                    if '|' in nxt_text and 'Chairman' in nxt_text:
                        break
                    
                    # A new paper starts with a title-only line far from current position
                    if nxt_cat == 'title' and (nxt['y'] - lines[i]['y']) > 20 and not paper_lines:
                        # This is part of the same paper's title
                        title_parts.append(nxt_text)
                        title = ' '.join(t for t in title_parts if t)
                        j += 1
                        continue
                    
                    if nxt_cat == 'title' and paper_lines and (nxt['y'] - lines[i]['y']) > 30:
                        # This is a new paper - save current and break
                        break
                    
                    # Collect spans from this line
                    for span_x, span_text in nxt['spans']:
                        if span_x < TITLE_MAX_X:
                            # Could be title continuation
                            if not paper_lines:
                                title_parts.append(span_text)
                                title = ' '.join(t for t in title_parts if t)
                        elif span_x < SPEAKER_MAX_X:
                            if speaker:
                                speaker += ' ' + span_text
                            else:
                                speaker = span_text
                        elif span_x < DISCUSSANT_MIN_X:
                            if author_text:
                                author_text += ' ' + span_text
                            else:
                                author_text = span_text
                        else:
                            if discussant:
                                discussant += ' ' + span_text
                            else:
                                discussant = span_text
                    
                    paper_lines.append(nxt)
                    j += 1
                
                # Extract author and institution from author_text
                final_author = ''
                final_institution = ''
                
                # Find "Name (Institution)" patterns
                people = re.findall(r'([A-Za-z\-\'À-ÿ\s.]+?)\s*\(([^)]+)\)', author_text)
                if people:
                    # Clean up first person's name
                    first_name = people[0][0].strip()
                    # Remove duplicate name parts
                    parts_list = first_name.split()
                    if len(parts_list) >= 3:
                        unique = []
                        for p in parts_list:
                            if p not in unique:
                                unique.append(p)
                        first_name = ' '.join(unique)
                    
                    final_author = first_name
                    final_institution = people[0][1].strip()
                elif speaker:
                    final_author = speaker
                
                if title and len(title) > 5:
                    current_session['papers'].append({
                        'author': final_author,
                        'institution': final_institution,
                        'title': title
                    })
                
                i = j
                continue
            
            i += 1
    
    # Save last session
    if current_session and current_session.get('papers'):
        all_sessions.append(current_session)
    
    doc.close()
    return all_sessions


def normalize_data(sessions):
    """Build participant index."""
    participants = {}
    for s in sessions:
        for p in s.get('papers', []):
            name = p.get('author', '').strip()
            if not name:
                continue
            if name not in participants:
                participants[name] = {
                    'name': name,
                    'institution': p.get('institution', ''),
                    'papers': [],
                    'is_presenter': True
                }
            participants[name]['papers'].append({
                'title': p.get('title', ''),
                'session': s.get('session_title', '')
            })
    return sessions, participants


if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/economics-conferences/affi2026/program.pdf")
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/economics-conferences/affi2026")
    
    print(f"Parsing: {pdf_path}")
    sessions = parse_affi_pdf(pdf_path)
    sessions, participants = normalize_data(sessions)
    
    total_papers = sum(len(s.get('papers', [])) for s in sessions)
    
    print(f"\nFound {len(sessions)} sessions, {total_papers} papers, {len(participants)} participants\n")
    
    for i, s in enumerate(sessions, 1):
        print(f"  {i:2d}. {s.get('session_title', '?')[:55]}")
        print(f"      Room: {s.get('room', '')}, Chair: {s.get('chair', '')[:35]}")
        for p in s.get('papers', []):
            auth = p.get('author', '?')[:35]
            print(f"      - {auth:35s} | {p.get('title', '?')[:60]}")
            if p.get('institution'):
                print(f"        {p.get('institution', '')[:60]}")
    
    # Institution stats
    inst_counts = Counter()
    inst_counts_all = Counter()
    for s in sessions:
        for p in s.get('papers', []):
            inst = p.get('institution', '')
            if len(inst) > 5:
                inst_counts[inst] += 1
            inst_counts_all[inst] += 1
    
    print(f"\n\n🏛️  TOP INSTITUTIONS (with at least 2 papers):")
    for i, (inst, count) in enumerate(inst_counts.most_common(20), 1):
        if count >= 2:
            print(f"  {i:2d}. {inst:60s} {count:2d}")
    
    # Save
    output = {
        "conference": "AFFI 2026 - 42nd International Conference of the French Finance Association",
        "source": pdf_path,
        "source_page": "https://affi2026.sciencesconf.org",
        "pdf_download_url": "https://drive.uca.fr/seafhttp/f/af1e47423c0f4c42a1ca/",
        "total_papers": total_papers,
        "total_participants": len(participants),
        "sessions": sessions,
        "participants": sorted(participants.values(), key=lambda x: x['name'])
    }
    
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to {out_path}")
