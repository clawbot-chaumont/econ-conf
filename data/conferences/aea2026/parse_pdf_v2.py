"""
Parse the AEA 2026 ASSA program PDF into structured JSON.
V2: More robust parser using time+association markers as session boundaries.
"""
import re
import json

def parse_program_pdf(filepath):
    with open(filepath, 'r') as f:
        text = f.read()
    
    # Remove page break markers
    text = re.sub(r'---PAGE BREAK---\n?', '', text)
    
    lines = text.split('\n')
    # Strip trailing whitespace but keep structure
    lines = [l.rstrip() for l in lines]
    
    # Day headers
    day_pattern = re.compile(r'^(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday),\s*(January|February|March)\s+\d+(rd|st|nd|th)?$', re.IGNORECASE)
    
    # Time marker: "X:XX AM" or "X:XX PM" at start of line (standalone)
    time_marker = re.compile(r'^(\d{1,2}:\d{2})\s+(AM|PM)$')
    
    # Find all session boundaries - a session starts with a time marker
    # followed by an association abbreviation and then session title
    
    # First, let me find time markers and what follows them
    sessions_raw = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        tm = time_marker.match(line)
        if tm:
            time_str = line
            # Next line should be association abbreviation
            if i + 1 < len(lines):
                assoc = lines[i+1].strip()
                # Association abbreviations are short (2-5 chars typically)
                if assoc and len(assoc) < 20 and assoc.isupper() or assoc in ['AFA/AFFECT', 'CSWEP']:
                    # Session title starts at i+2
                    session_start = i + 2
                    sessions_raw.append({
                        'time': time_str,
                        'association': assoc,
                        'start_line': session_start
                    })
                    i = session_start
                    continue
        i += 1
    
    print(f"Found {len(sessions_raw)} potential session starts (time markers)")
    
    # Now for each session, find its end (next time marker or end of file)
    for idx, s in enumerate(sessions_raw):
        if idx + 1 < len(sessions_raw):
            s['end_line'] = sessions_raw[idx + 1]['start_line'] - 2  # Go back to before next time marker
        else:
            s['end_line'] = len(lines)
    
    # Parse each session
    sessions = []
    for idx, s in enumerate(sessions_raw):
        session_lines = lines[s['start_line']:s['end_line']]
        session = parse_session_block(session_lines, s)
        if session:
            sessions.append(session)
        
        if (idx + 1) % 100 == 0:
            print(f"  Parsed {idx + 1}/{len(sessions_raw)} sessions...")
    
    # Filter to only Paper/Poster/Panel/Lightning Round sessions
    relevant_types = ('Paper Session', 'Poster Session', 'Panel Session', 'Lightning Round Session')
    paper_sessions = [s for s in sessions if s.get('session_type') in relevant_types]
    print(f"\nTotal sessions: {len(sessions)}, Paper sessions: {len(paper_sessions)}")
    
    return sessions


def parse_session_block(lines, marker):
    """Parse a block of lines representing one session."""
    
    text = '\n'.join(lines)
    text_stripped = text.strip()
    
    if not text_stripped:
        return None
    
    result = {
        'time': marker['time'],
        'association': marker['association'],
    }
    
    # Find session type
    session_type_patterns = [
        r'^(Paper Session)\s*$',
        r'^(Poster Session)\s*$',
        r'^(Panel Session)\s*$',
        r'^(Lightning Round Session)\s*$',
        r'^(Lecture)\s*$',
        r'^(Event)\s*$',
        r'^(Event \(Invitation Only\))\s*$',
        r'^(Lecture \(Invitation Only\))\s*$',
    ]
    
    session_type = None
    type_line_idx = None
    title_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        
        for pat in session_type_patterns:
            m = re.match(pat, stripped)
            if m:
                session_type = m.group(1)
                type_line_idx = i
                break
        
        if session_type:
            break
    
    if session_type is None:
        # Couldn't find session type - skip
        return None
    
    result['session_type'] = session_type
    
    # Session title is everything between the association line and the type line
    # (skipping empty lines)
    title_start = 0
    # Skip leading empty lines
    while title_start < type_line_idx and lines[title_start].strip() == '':
        title_start += 1
    
    title_parts = []
    for j in range(title_start, type_line_idx):
        l = lines[j].strip()
        if l:
            title_parts.append(l)
    
    # Only include the last line(s) as the actual title if there are associations before
    # Sometimes the association abbreviation appears on the line before the title
    # In the PDF: after time marker, there's association abbrev + title
    # But we already extracted association from marker, so title is what's on the next lines
    result['session_title'] = ' '.join(title_parts)
    
    # Now parse metadata after the type line
    metadata_lines = lines[type_line_idx + 1:]
    
    # Extract date
    date_match = re.search(r'(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday),\s*(Jan\.?\s*\d+,\s*\d{4})', text)
    if date_match:
        result['date'] = date_match.group(0).strip()
    
    # Extract time range
    time_match = re.search(r'(\d{1,2}:\d{2}\s*(AM|PM))\s*-\s*(\d{1,2}:\d{2}\s*(AM|PM))\s*\((\w+)\)', text)
    if time_match:
        result['time_range'] = time_match.group(0).strip()
    
    # Extract location
    loc_match = re.search(r'(Philadelphia\s+(?:Convention Center|Marriott Downtown|Mariott Downtown)[^,\n]*[^,\n]*(?:,\s*[^,\n]*)?)', text)
    if loc_match:
        result['location'] = loc_match.group(1).strip()
    else:
        loc_match = re.search(r'(Loews\s+Philadelphia\s+Hotel[^,\n]*(?:,\s*[^,\n]*)?)', text)
        if loc_match:
            result['location'] = loc_match.group(1).strip()
        else:
            loc_match = re.search(r'((?:Sheraton|DoubleTree|Courtyard|Hampton|Holiday Inn)[^,\n]*(?:,\s*[^,\n]*)?)', text)
            if loc_match:
                result['location'] = loc_match.group(1).strip()
    
    # Extract hosted by
    hosted_match = re.search(r'Hosted By:\s*(.+?)$', text, re.MULTILINE)
    if hosted_match:
        result['hosted_by'] = hosted_match.group(1).strip()
    
    # Extract chair
    chair_match = re.search(r'Chair:\s*(.+?)$', text, re.MULTILINE)
    if chair_match:
        result['chair'] = chair_match.group(1).strip()
    else:
        presiding_match = re.search(r'Presiding:\s*(.+?)$', text, re.MULTILINE)
        if presiding_match:
            result['chair'] = presiding_match.group(1).strip()
    
    # Extract papers for relevant session types
    if session_type in ('Paper Session', 'Poster Session', 'Panel Session', 'Lightning Round Session'):
        papers = extract_papers(lines, type_line_idx)
        result['papers'] = papers
        result['num_papers'] = len(papers)
    
    return result


def extract_papers(lines, type_line_idx):
    """Extract papers from session lines after the type line."""
    
    # Find the start of paper content - after JEL codes and before Discussant(s)
    content_start = None
    content_end = None
    
    for i in range(type_line_idx + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith('JEL Classifications'):
            content_start = i + 1
            break
    
    if content_start is None:
        # Try starting after Chair line
        for i in range(type_line_idx + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith('Chair:') or stripped.startswith('Presiding:') or stripped.startswith('Speaker(s)'):
                content_start = i + 1
                # Skip speaker(s) section
                if stripped.startswith('Speaker(s)'):
                    # Find where speaker section ends
                    for j in range(i+1, min(i+20, len(lines))):
                        ls = lines[j].strip()
                        if ls.startswith('Topic:'):
                            content_start = j + 1
                            break
                break
    
    if content_start is None:
        return []
    
    # Find end: Discussant(s) or Topic: or next section
    for i in range(content_start, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith('Discussant') or stripped.startswith('Topic:') or stripped.startswith('Invitation Only'):
            content_end = i
            break
    
    if content_end is None:
        content_end = len(lines)
    
    # Extract paper lines, skipping JEL codes and empty lines
    paper_content = []
    for i in range(content_start, content_end):
        stripped = lines[i].strip()
        if not stripped:
            continue
        # Skip JEL code lines
        if re.match(r'^[A-Z]\d\s*-\s*', stripped):
            continue
        # Skip "Hosted By:" lines
        if stripped.startswith('Hosted By:'):
            continue
        paper_content.append(stripped)
    
    # Now parse into papers
    # A paper title is a line that does NOT contain a comma followed by an institution
    # An author line has format: "Name, Institution"
    # BUT: some paper titles contain commas too!
    # Better heuristic: author lines end with a known institution keyword
    
    # Actually, the most reliable approach:
    # - Lines with ", " followed by known institution words are author lines
    # - Everything else is a paper title (possibly continued from previous line)
    
    institution_keywords = [
        'University', 'Institute', 'School', 'College', 'Bank', 'Department',
        'Laboratory', 'Center', 'Centre', 'Foundation', 'Association',
        'Corporation', 'Company', 'Federal', 'National', 'International',
        'World', 'Brookings', 'Hoover', 'NBER', 'IMF', 'World Bank',
        'Federal Reserve', 'AEA', 'AFA', 'NBER', 'CESifo', 'IZA',
        'RAND', 'Urban Institute', 'CBO', 'USDA', 'Treasury',
        'Board of Governors', 'Bureau', 'Agency', 'Ministry',
    ]
    
    papers = []
    current_title_parts = []
    current_authors = []
    
    def save_current_paper():
        if current_title_parts or current_authors:
            title = ' '.join(current_title_parts).strip()
            # Merge duplicate adjacent same-institution authors
            if title and current_authors:
                papers.append({
                    'title': title,
                    'authors': list(current_authors)
                })
            current_title_parts.clear()
            current_authors.clear()
    
    for pl in paper_content:
        # Check if this is an author line
        # An author line has format: "Name, Institution" where Institution contains a known keyword
        is_author = False
        author_name = None
        author_inst = None
        
        # Pattern for author line
        author_match = re.match(r'^(.+),\s+(.+)$', pl)
        if author_match:
            potential_name = author_match.group(1).strip()
            potential_inst = author_match.group(2).strip()
            
            # Check if the "institution" part looks like an institution
            has_inst_keyword = any(kw.lower() in potential_inst.lower() for kw in institution_keywords)
            # Check if the name part doesn't look like a paper title (not too long, not ending with ? or .)
            is_likely_name = (len(potential_name) < 60 and 
                             not potential_name.endswith('?') and
                             not potential_name.endswith('.') and
                             not potential_name.startswith('('))
            
            if has_inst_keyword and is_likely_name:
                is_author = True
                author_name = potential_name
                author_inst = potential_inst
            elif potential_inst.startswith(('University of', 'The ')) or potential_inst.endswith(('University', 'College', 'Institute', 'School', 'Bank')):
                is_author = True
                author_name = potential_name
                author_inst = potential_inst
        
        if is_author:
            current_authors.append({'name': author_name, 'institution': author_inst})
        else:
            # It's a paper title (or continuation)
            save_current_paper()
            current_title_parts.append(pl)
    
    # Save last paper
    save_current_paper()
    
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
    
    participant_map = {}
    all_paper_titles = set()
    
    for s in sessions:
        session_entry = {
            'session_title': s.get('session_title', ''),
            'session_type': s.get('session_type', ''),
            'chair': s.get('chair', ''),
            'date': s.get('date', ''),
            'time': s.get('time_range', ''),
            'location': s.get('location', ''),
            'hosted_by': s.get('hosted_by', ''),
            'papers': []
        }
        
        for p in s.get('papers', []):
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
    
    for name, info in participant_map.items():
        conference_data['participants'].append({
            'name': name,
            'institution': info['institution'],
            'papers': info['papers']
        })
    
    return conference_data


if __name__ == '__main__':
    print("Parsing AEA 2026 program PDF (V2)...")
    sessions = parse_program_pdf('program_full_text.txt')
    
    # Count stats
    relevant_types = ('Paper Session', 'Poster Session', 'Panel Session', 'Lightning Round Session')
    paper_sessions = [s for s in sessions if s.get('session_type') in relevant_types]
    total_papers = sum(s.get('num_papers', 0) for s in paper_sessions)
    print(f"Total sessions: {len(sessions)}")
    print(f"Paper/Poster/Panel/Lightning sessions: {len(paper_sessions)}")
    print(f"Total papers: {total_papers}")
    
    # Build final JSON
    result = build_final_json(paper_sessions)
    
    output_path = '/root/economics-conferences/aea2026/data.json'
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to {output_path}")
    print(f"Total unique papers: {result['total_papers']}")
    print(f"Total participants: {result['total_participants']}")
    print(f"Total sessions: {len(result['sessions'])}")
    
    # Verify known sessions
    print(f"\n=== Verifying known sessions ===")
    for s in result['sessions']:
        if 'Agricultural and Food Policy' == s['session_title']:
            print(f"Found: {s['session_title']}")
            print(f"  Chair: {s['chair']}")
            print(f"  Papers: {len(s['papers'])}")
            for p in s['papers']:
                print(f"  Title: {p['title'][:80]}")
                for a in p['authors']:
                    print(f"    {a['name']} ({a['institution']})")
        elif 'Digital Money' == s['session_title']:
            print(f"\nFound: {s['session_title']}")
            print(f"  Chair: {s['chair']}")
            print(f"  Papers: {len(s['papers'])}")
            for p in s['papers']:
                print(f"  Title: {p['title'][:80]}")
                for a in p['authors']:
                    print(f"    {a['name']} ({a['institution']})")
