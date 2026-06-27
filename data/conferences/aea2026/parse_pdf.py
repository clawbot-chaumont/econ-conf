"""
Parse the AEA 2026 ASSA program PDF into structured JSON.
"""
import re
import json

def parse_program_pdf(filepath):
    with open(filepath, 'r') as f:
        text = f.read()
    
    # Remove page breaks
    text = text.replace('---PAGE BREAK---\n', '')
    text = text.replace('---PAGE BREAK---', '')
    
    lines = text.split('\n')
    
    # First, find all lines that indicate session types
    session_type_pattern = re.compile(
        r'^(Paper Session|Poster Session|Panel Session|Lightning Round Session|Lecture|Event|Event \(Invitation Only\))\s*$'
    )
    
    # Find all session start positions
    sessions_raw = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = session_type_pattern.match(line)
        if m:
            session_type = m.group(1)
            # Session title is before this line
            # Could be 1 or 2 lines
            title_lines = []
            j = i - 1
            # Skip empty lines backwards
            while j >= 0 and lines[j].strip() == '':
                j -= 1
            # Get title - check if previous non-empty lines are part of title
            if j >= 0:
                # Look at the lines before the type marker
                k = j
                title_part = lines[k].strip()
                # Check if line before that is also part of title (not a time/date marker)
                if k > 0:
                    prev_line = lines[k-1].strip()
                    # Title continuation: previous line doesn't match time pattern or other markers
                    time_pattern = re.compile(r'^\d{1,2}:\d{2}\s*(AM|PM)')
                    date_pattern = re.compile(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)')
                    if not time_pattern.match(prev_line) and not date_pattern.match(prev_line) \
                        and not prev_line.startswith('Hosted By:') and not prev_line.startswith('Chair:') \
                        and not prev_line.startswith('Presiding:') and not prev_line.startswith('JEL') \
                        and prev_line not in ('', ' ', '-') and len(prev_line) > 3:
                        title_part = prev_line + ' ' + title_part
                        k -= 1
                
                title = title_part
                start_line = k
            else:
                title = ''
                start_line = j
            
            sessions_raw.append({
                'title': title,
                'type': session_type,
                'start_line': start_line,
                'type_line': i,
            })
        i += 1
    
    print(f"Found {len(sessions_raw)} sessions")
    
    # Now parse each session's details
    sessions = []
    for idx, s in enumerate(sessions_raw):
        # Determine end line (next session start or end of file)
        if idx + 1 < len(sessions_raw):
            end_line = sessions_raw[idx + 1]['start_line']
        else:
            end_line = len(lines)
        
        session_lines = lines[s['start_line']:end_line]
        session = parse_session_block(session_lines, s['title'], s['type'])
        if session:
            sessions.append(session)
        
        if (idx + 1) % 50 == 0:
            print(f"  Parsed {idx + 1}/{len(sessions_raw)} sessions...")
    
    return sessions


def parse_session_block(lines, title, session_type):
    """Parse a block of lines representing one session."""
    
    text = '\n'.join(lines)
    
    result = {
        'session_title': title,
        'session_type': session_type,
    }
    
    # Extract date
    date_match = re.search(r'(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday),\s*(Jan\.?\s*\d+,\s*\d{4})', text)
    if date_match:
        result['date'] = date_match.group(0).strip()
    
    # Extract time range
    time_match = re.search(r'(\d{1,2}:\d{2}\s*(AM|PM))\s*-\s*(\d{1,2}:\d{2}\s*(AM|PM))\s*\((\w+)\)', text)
    if time_match:
        result['time'] = time_match.group(0).strip()
    
    # Extract location
    location_patterns = [
        r'Philadelphia (?:Convention Center|Marriott Downtown|Mariott Downtown),?\s*.+',
        r'Loews Philadelphia Hotel,?\s*.+',
    ]
    for pat in location_patterns:
        loc_match = re.search(pat, text)
        if loc_match:
            result['location'] = loc_match.group(0).strip()
            break
    
    # Extract hosted by
    hosted_match = re.search(r'Hosted By:\s*(.+?)(?:\n|$)', text)
    if hosted_match:
        result['hosted_by'] = hosted_match.group(1).strip()
    
    # Extract chair
    chair_match = re.search(r'Chair:\s*(.+?)(?:\n|$)', text)
    if chair_match:
        result['chair'] = chair_match.group(1).strip()
    
    # Extract presiding (alternative to chair)
    if 'chair' not in result:
        presiding_match = re.search(r'Presiding:\s*(.+?)(?:\n|$)', text)
        if presiding_match:
            result['chair'] = presiding_match.group(1).strip()
    
    # Extract papers only for relevant session types
    if session_type in ('Paper Session', 'Poster Session', 'Panel Session', 'Lightning Round Session'):
        papers = extract_papers_from_block(lines, session_type)
        result['papers'] = papers
    
    return result


def extract_papers_from_block(lines, session_type):
    """Extract paper titles and authors from session lines."""
    
    # Find the relevant section - after JEL/Chair and before Discussant(s)
    start_found = False
    paper_lines = []
    in_discussant = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            continue
        
        # Detect start: after JEL Classifications or after Chair line
        if stripped.startswith('JEL Classifications'):
            start_found = True
            continue
        
        if stripped.startswith('Discussant'):
            break
        
        # Skip JEL code lines (they start with letter-digit pattern)
        if re.match(r'^[A-Z]\d\s*-\s*', stripped):
            continue
        
        if start_found and stripped:
            paper_lines.append(stripped)
    
    # If no JEL section, try finding papers after chair
    if not start_found:
        in_papers = False
        paper_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('Chair:') or stripped.startswith('Presiding:'):
                in_papers = True
                continue
            if stripped == 'Speaker(s)':
                in_papers = True
                continue
            if stripped.startswith('Discussant'):
                break
            if stripped.startswith('JEL Classifications'):
                in_papers = True
                continue
            if re.match(r'^[A-Z]\d\s*-\s*', stripped):
                continue
            if in_papers and stripped:
                paper_lines.append(stripped)
    
    # Now parse paper_lines into papers
    papers = []
    current_title = None
    current_authors = []
    
    # Pattern for author line: "Name, Institution" 
    # Paper title line: no comma followed by an institution (or no comma at all, or different pattern)
    author_pattern = re.compile(r'^(.+?),\s+(.+)$')
    
    for pl in paper_lines:
        author_match = author_pattern.match(pl)
        
        if author_match:
            # This is an author line
            name = author_match.group(1).strip()
            institution = author_match.group(2).strip()
            current_authors.append({'name': name, 'institution': institution})
        else:
            # This is a paper title (could be continuation)
            if current_title and current_authors:
                # Save previous paper
                papers.append({
                    'title': current_title,
                    'authors': list(current_authors)
                })
                current_authors = []
            
            if current_title:
                # Could be title continuation - but paper titles shouldn't be this complex
                # Actually, PDF wraps lines, so check if it's a continuation
                if pl[0].islower() or (len(pl) > 5 and not pl[0].isupper() and not re.match(r'^[A-Z][a-z]+\b', pl)):
                    current_title += ' ' + pl
                else:
                    current_title = pl
            else:
                current_title = pl
    
    # Don't forget the last paper
    if current_title and current_authors:
        papers.append({
            'title': current_title,
            'authors': list(current_authors)
        })
    
    return papers


def build_final_json(sessions):
    """Build the final JSON structure."""
    
    conference_data = {
        'conference': 'AEA 2026',
        'total_papers': 0,
        'total_participants': 0,
        'sessions': [],
        'participants': []
    }
    
    # Track all participants
    participant_map = {}  # name -> {institution, papers[]}
    all_paper_titles = set()
    
    for s in sessions:
        session_entry = {
            'session_title': s.get('session_title', ''),
            'session_type': s.get('session_type', ''),
            'chair': s.get('chair', ''),
            'date': s.get('date', ''),
            'time': s.get('time', ''),
            'location': s.get('location', ''),
            'hosted_by': s.get('hosted_by', ''),
            'papers': []
        }
        
        papers = s.get('papers', [])
        for p in papers:
            title = p.get('title', '')
            if title:
                all_paper_titles.add(title)
            
            paper_entry = {
                'title': title,
                'authors': []
            }
            
            for author in p.get('authors', []):
                name = author.get('name', '')
                institution = author.get('institution', '')
                
                paper_entry['authors'].append({
                    'name': name,
                    'institution': institution
                })
                
                # Track participant
                if name:
                    if name not in participant_map:
                        participant_map[name] = {
                            'institution': institution,
                            'papers': []
                        }
                    participant_map[name]['papers'].append(title)
                    if institution and not participant_map[name]['institution']:
                        participant_map[name]['institution'] = institution
            
            session_entry['papers'].append(paper_entry)
        
        conference_data['sessions'].append(session_entry)
    
    conference_data['total_papers'] = len(all_paper_titles)
    conference_data['total_participants'] = len(participant_map)
    
    # Build participants list
    for name, info in participant_map.items():
        conference_data['participants'].append({
            'name': name,
            'institution': info['institution'],
            'papers': info['papers']
        })
    
    return conference_data


if __name__ == '__main__':
    print("Parsing AEA 2026 program PDF...")
    sessions = parse_program_pdf('program_full_text.txt')
    print(f"\nTotal sessions parsed: {len(sessions)}")
    
    # Count sessions with papers and total papers
    paper_sessions = [s for s in sessions if s.get('papers')]
    total_papers = sum(len(s.get('papers', [])) for s in sessions)
    print(f"Sessions with papers: {len(paper_sessions)}")
    print(f"Total paper entries: {total_papers}")
    
    # Build final JSON
    result = build_final_json(sessions)
    
    # Save
    output_path = '/root/economics-conferences/aea2026/data.json'
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to {output_path}")
    print(f"Total papers: {result['total_papers']}")
    print(f"Total participants: {result['total_participants']}")
    print(f"Total sessions: {len(result['sessions'])}")
    
    # Print first session as sample
    if result['sessions']:
        print(f"\n=== Sample Session ===")
        s = result['sessions'][0]
        print(f"Title: {s['session_title']}")
        print(f"Type: {s['session_type']}")
        print(f"Chair: {s['chair']}")
        print(f"Date: {s['date']}")
        print(f"Papers: {len(s.get('papers', []))}")
        for p in s.get('papers', [])[:3]:
            print(f"  - {p['title'][:60]}")
            for a in p.get('authors', [])[:2]:
                print(f"      {a['name']} ({a['institution']})")
