"""
Parse the AEA 2026 ASSA program PDF into structured JSON.
V3: Session-type-marker-based approach with backwards title scanning.
"""
import re
import json

# Institution keywords for author detection
INST_KEYWORDS = [
    'University', 'Institute', 'School', 'College', 'Bank', 'Department',
    'Laboratory', 'Center', 'Centre', 'Foundation', 'Association',
    'Corporation', 'Company', 'Federal', 'National', 'International',
    'World', 'Brookings', 'Hoover', 'NBER', 'IMF', 'World Bank',
    'Federal Reserve', 'AEA', 'AFA', 'CESifo', 'IZA', 'RAND',
    'Urban Institute', 'CBO', 'USDA', 'Treasury', 'Ministry',
    'Office', 'Agency', 'Commission', 'Council', 'Board', 'Authority',
    'Fund', 'Program', 'Project', 'Press', 'Institution',
    'Hospital', 'Clinic', 'Advisory', 'Partners', 'LLC', 'Inc',
    'Labs', 'Ltd', 'LP', 'Corp', 'Pte', 'GmbH', 'AG',
    'Bureau of Economic Analysis', 'Census Bureau', 'Bureau of Labor Statistics',
    'Federal Reserve Bank', 'European Central Bank', 'Bank of',
    'BIS', 'OECD', 'WTO', 'UN', 'UNDP', 'USAID', 'NSF', 'NIH',
    'Organisation', 'Organization', 'Peterson Institute',
    'International Food Policy Research Institute',
]


def is_standalone_time(line):
    """Check if a line is a standalone time marker like '8:00 AM'"""
    return bool(re.match(r'^\d{1,2}:\d{2}\s+(AM|PM)$', line.strip()))


def is_association_abbrev(line):
    """Check if a line looks like an association abbreviation"""
    s = line.strip()
    # Short uppercase string, possibly with slashes
    if not s:
        return False
    # Known associations
    known = ['AEA', 'AFA', 'AFEA', 'AFEE', 'AREUEA', 'ASSA', 'ASHEA', 'ASA',
             'CSWEP', 'CSMGEP', 'NEA', 'ACE', 'SGE', 'URPE', 'IAFFE', 'NAASE',
             'ACE', 'ADA', 'APSA', 'ASSA', 'CEANA', 'EAST', 'EHA', 'FCS',
             'ICE', 'MEA', 'MENA', 'NAFE', 'OMG', 'SGE', 'UEA', 'WEA',
             'IMF', 'World Bank', 'NBER', 'AFA/AFFECT', 'CSWEP/CSMGEP']
    if s in known:
        return True
    if len(s) <= 10 and (s.isupper() or s.count('/') <= 2):
        # Check if it contains only uppercase letters, digits, slashes, and spaces
        if re.match(r'^[A-Z0-9 /]+$', s):
            return True
    return False


def is_jel_code(line):
    """Check if line is a JEL classification code"""
    return bool(re.match(r'^[A-Z]\d+\s*[-–—]\s*', line.strip()))


def clean_text(text):
    """Clean up common PDF extraction artifacts"""
    text = text.replace('■', '').replace('□', '')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_program_pdf(filepath):
    with open(filepath, 'r') as f:
        text = f.read()
    
    # Remove page break markers
    text = re.sub(r'---PAGE BREAK---\n?', '\n', text)
    
    lines = text.split('\n')
    lines = [l.rstrip() for l in lines]
    
    # Find all session type markers
    session_types = [
        'Paper Session', 'Poster Session', 'Panel Session',
        'Lightning Round Session', 'Lecture', 'Event',
        'Event (Invitation Only)'
    ]
    
    session_markers = []
    for i, line in enumerate(lines):
        s = line.strip()
        if s in session_types:
            session_markers.append((i, s))
    
    print(f"Found {len(session_markers)} session markers")
    
    # Parse each session
    sessions = []
    
    for idx, (type_line, stype) in enumerate(session_markers):
        # Determine end: next session marker or end
        if idx + 1 < len(session_markers):
            end_line = session_markers[idx + 1][0]
        else:
            end_line = len(lines)
        
        session = parse_one_session(lines, type_line, stype, end_line)
        if session:
            sessions.append(session)
        
        if (idx + 1) % 100 == 0:
            print(f"  Parsed {idx + 1}/{len(session_markers)} sessions...")
    
    return sessions


def find_title_backwards(lines, type_line_idx):
    """Scan backwards from type_line_idx to find the session title.
    Returns (title, title_start_line, association, time_marker)
    """
    title_parts = []
    assoc = ''
    time_marker = ''
    
    i = type_line_idx - 1
    # Skip empty lines
    while i >= 0 and lines[i].strip() == '':
        i -= 1
    
    # Now collect title lines
    title_end = i
    while i >= 0:
        s = lines[i].strip()
        if not s:
            break
        # Stop at page breaks
        if s.startswith('---PAGE'):
            break
        # Stop at time markers
        if is_standalone_time(s):
            time_marker = s
            break
        # Stop at known ending patterns
        if s.startswith('Discussant') or s.startswith('Topic:'):
            break
        if s == 'Speaker(s)':
            break
        # Stop at invitation only notice
        if s == 'Invitation Only':
            break
        # Check if this is an association abbrev
        if is_association_abbrev(s):
            assoc = s
            break
        i -= 1
    
    # Collect title from i+1 to title_end
    for j in range(i + 1, title_end + 1):
        s = lines[j].strip()
        if s and not is_association_abbrev(s) and not is_standalone_time(s) and s != 'Invitation Only':
            title_parts.append(s)
    
    title = ' '.join(title_parts)
    return title, i, assoc, time_marker


def parse_one_session(lines, type_line_idx, stype, end_line):
    """Parse one session from its type marker."""
    
    # Find title backwards
    title, title_start, assoc, time_marker = find_title_backwards(lines, type_line_idx)
    
    if not title:
        return None
    
    # Get the session body (from type line to end)
    body_lines = lines[type_line_idx:end_line]
    body_text = '\n'.join(body_lines)
    
    result = {
        'session_title': title,
        'session_type': stype,
        'association': assoc,
        'time_marker': time_marker,
    }
    
    # Extract date
    date_match = re.search(r'(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday),\s*(Jan\.?\s*\d+,\s*\d{4})', body_text)
    if date_match:
        result['date'] = date_match.group(0).strip()
    
    # Extract time range
    time_match = re.search(r'(\d{1,2}:\d{2}\s*(AM|PM))\s*[-–]\s*(\d{1,2}:\d{2}\s*(AM|PM))\s*\((\w+)\)', body_text)
    if time_match:
        result['time_range'] = time_match.group(0).strip()
    
    # Extract location
    loc_match = re.search(r'(Philadelphia\s+(?:Convention Center|Marriott Downtown|Mariott Downtown)[^,\n]*[^,\n]*(?:,\s*[^,\n]*)?)', body_text)
    if loc_match:
        result['location'] = loc_match.group(1).strip()
    else:
        loc_match = re.search(r'(Loews\s+Philadelphia\s+Hotel[^,\n]*(?:,\s*[^,\n]*)?)', body_text)
        if loc_match:
            result['location'] = loc_match.group(1).strip()
        else:
            loc_match = re.search(r'((?:Sheraton|DoubleTree|Courtyard|Hampton|Holiday\s+Inn)[^,\n]*(?:,\s*[^,\n]*)?)', body_text)
            if loc_match:
                result['location'] = loc_match.group(1).strip()
    
    # Extract hosted by
    hosted_match = re.search(r'Hosted By:\s*(.+?)$', body_text, re.MULTILINE)
    if hosted_match:
        result['hosted_by'] = hosted_match.group(1).strip()
    
    # Extract chair
    chair_match = re.search(r'Chair:\s*(.+?)$', body_text, re.MULTILINE)
    if chair_match:
        result['chair'] = chair_match.group(1).strip()
    else:
        presiding_match = re.search(r'Presiding:\s*(.+?)$', body_text, re.MULTILINE)
        if presiding_match:
            result['chair'] = presiding_match.group(1).strip()
    
    # Extract papers for relevant session types
    if stype in ('Paper Session', 'Poster Session', 'Panel Session', 'Lightning Round Session'):
        papers = extract_papers_from_body(body_lines)
        result['papers'] = papers
        result['num_papers'] = len(papers)
    
    return result


def extract_papers_from_body(body_lines):
    """Extract papers from session body lines."""
    
    # Find start of paper content: after JEL codes or after Chair line
    content_start = None
    
    for i, line in enumerate(body_lines):
        s = line.strip()
        if s == 'JEL Classifications':
            content_start = i + 1
            break
    
    if content_start is None:
        for i, line in enumerate(body_lines):
            s = line.strip()
            if s.startswith('Chair:') or s.startswith('Presiding:') or s == 'Speaker(s)':
                content_start = i + 1
                if s == 'Speaker(s)':
                    # Skip topic lines
                    for j in range(i+1, min(i+15, len(body_lines))):
                        ls = body_lines[j].strip()
                        if ls.startswith('Topic:'):
                            content_start = j + 1
                        elif ls and not ls.startswith('Topic:'):
                            break
                break
    
    if content_start is None:
        return []
    
    # Find end: Discussant(s) or Topic:
    content_end = len(body_lines)
    for i in range(content_start, len(body_lines)):
        s = body_lines[i].strip()
        if s.startswith('Discussant') or s.startswith('Topic:'):
            content_end = i
            break
        # Also stop at standalone time markers (next session)
        if is_standalone_time(s):
            content_end = i
            break
        # Stop at "Invitation Only"
        if s == 'Invitation Only':
            content_end = i
            break
    
    # Collect paper content lines
    paper_lines = []
    for i in range(content_start, content_end):
        s = body_lines[i].strip()
        if not s:
            continue
        if is_jel_code(s):
            continue
        if s.startswith('Hosted By:'):
            continue
        if s.startswith('Chair:') or s.startswith('Presiding:'):
            continue
        if s == 'Speaker(s)':
            continue
        if s.startswith('Topic:'):
            continue
        if s in ('Pre registration is required.',):
            continue
        if s.startswith('Register now'):
            continue
        paper_lines.append(s)
    
    # Now parse paper_lines into papers
    papers = []
    current_title_parts = []
    current_authors = []
    
    def save_paper():
        if current_title_parts:
            title = ' '.join(current_title_parts).strip()
            if title and current_authors:
                papers.append({'title': title, 'authors': list(current_authors)})
            elif title and not current_authors and current_title_parts:
                # Possibly a single-line poster entry
                pass
        current_title_parts.clear()
        current_authors.clear()
    
    for pl in paper_lines:
        # Check if this is an author line: "Name, Institution"
        author_match = re.match(r'^(.+),\s+(.+)$', pl)
        is_author = False
        
        if author_match:
            potential_name = author_match.group(1).strip()
            potential_inst = author_match.group(2).strip()
            
            has_inst_keyword = any(kw.lower() in potential_inst.lower() for kw in INST_KEYWORDS)
            
            # Name should not be too long and should look like a person's name
            name_ok = (len(potential_name) < 80 and 
                      not potential_name.endswith(('?', '.', ':')) and
                      not potential_name.startswith('(') and
                      not re.match(r'^[A-Z\s/]+$', potential_name))  # not all-caps (assoc names)
            
            # The institution part should be substantial
            inst_ok = len(potential_inst) > 3
            
            if has_inst_keyword and inst_ok:
                is_author = True
        
        if is_author:
            current_authors.append({
                'name': author_match.group(1).strip(),
                'institution': author_match.group(2).strip()
            })
        else:
            save_paper()
            current_title_parts.append(pl)
    
    save_paper()
    
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
    print("Parsing AEA 2026 program PDF (V3)...")
    sessions = parse_program_pdf('program_full_text.txt')
    
    relevant_types = ('Paper Session', 'Poster Session', 'Panel Session', 'Lightning Round Session')
    paper_sessions = [s for s in sessions if s.get('session_type') in relevant_types]
    
    print(f"\nTotal sessions: {len(sessions)}")
    print(f"Paper/Poster/Panel/Lightning sessions: {len(paper_sessions)}")
    total_papers = sum(s.get('num_papers', 0) for s in paper_sessions)
    print(f"Total paper entries: {total_papers}")
    
    # Build and save
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
        if 'Agricultural and Food Policy' in s['session_title']:
            print(f"Found: '{s['session_title']}'")
            print(f"  Chair: {s['chair']}")
            print(f"  Papers: {len(s['papers'])}")
            for p in s['papers']:
                print(f"  Title: {p['title'][:80]}")
                for a in p['authors']:
                    print(f"    {a['name']} ({a['institution']})")
            break
    
    for s in result['sessions']:
        if 'Digital Money' in s['session_title'] or s['session_title'] == 'Digital Money':
            print(f"\nFound: '{s['session_title']}'")
            print(f"  Chair: {s['chair']}")
            print(f"  Papers: {len(s['papers'])}")
            for p in s['papers']:
                print(f"  Title: {p['title'][:80]}")
                for a in p['authors']:
                    print(f"    {a['name']} ({a['institution']})")
            break
    
    # Show a few sample sessions
    print(f"\n=== Sample sessions ===")
    for s in paper_sessions[:3]:
        print(f"  {s['session_title'][:60]} | {s['session_type']} | {len(s.get('papers', []))} papers")
