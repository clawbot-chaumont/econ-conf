"""
Parse the AEA 2026 ASSA program PDF into structured JSON.
V5: Fixed multi-line paper titles (concatenate consecutive non-author lines).
"""
import re
import json

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
    'Sveriges Riksbank', 'Norges Bank', 'Deutsche Bundesbank',
    'Banque de France', 'Bank of England', 'Bank of Japan',
    'Reserve Bank', 'Central Bank', 'Monetary Authority',
    'Inter-American Development Bank', 'Asian Development Bank',
    'African Development Bank', 'European Commission',
    'Congressional Budget Office', 'Government Accountability Office',
    'National Bureau of Economic Research',
    'Institute for', 'Institut', 'Istituto', 'Instituto',
    'School of', 'Faculty of', 'Department of', 'Division of',
    'World Bank Group', 'International Monetary Fund',
]


def is_standalone_time(line):
    return bool(re.match(r'^\d{1,2}:\d{2}\s+(AM|PM)$', line.strip()))


def is_association_abbrev(line):
    s = line.strip()
    if not s:
        return False
    known = ['AEA', 'AFA', 'AFEA', 'AFEE', 'AREUEA', 'ASSA', 'ASHEA', 'ASA',
             'CSWEP', 'CSMGEP', 'NEA', 'ACE', 'SGE', 'URPE', 'IAFFE', 'NAASE',
             'ADA', 'APSA', 'CEANA', 'EAST', 'EHA', 'FCS', 'ICE', 'MEA',
             'MENA', 'NAFE', 'OMG', 'UEA', 'WEA',
             'IMF', 'World Bank', 'NBER', 'AFA/AFFECT', 'CSWEP/CSMGEP',
             'ASHE', 'CSEA', 'EBHS', 'EHA', 'EHBS', 'HES', 'MEEA',
             'NAA', 'NTA', 'OSPE', 'PEPA', 'SABE', 'SGE', 'SIE', 'SOLE',
             'Tsinghua University PBCSF', 'Tsinghua University',
             'AFFECT']
    if s in known:
        return True
    if len(s) <= 12 and re.match(r'^[A-Z0-9 /]+$', s):
        return True
    return False


def is_jel_code(line):
    return bool(re.match(r'^[A-Z]\d+\s*[-–—]', line.strip()))


def is_time_range(line):
    return bool(re.search(r'\d{1,2}:\d{2}\s+(AM|PM)\s*[-–]\s*\d{1,2}:\d{2}\s+(AM|PM)', line))


def is_date_line(line):
    return bool(re.match(r'^(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday),\s*(Jan\.?\s*\d+,\s*\d{4})', line.strip()))


def parse_program_pdf(filepath):
    with open(filepath, 'r') as f:
        text = f.read()
    
    text = re.sub(r'---PAGE BREAK---\n?', '\n', text)
    lines = text.split('\n')
    lines = [l.rstrip() for l in lines]
    
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
    
    sessions = []
    for idx, (type_line, stype) in enumerate(session_markers):
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
    title_parts = []
    assoc = ''
    time_marker = ''
    
    i = type_line_idx - 1
    while i >= 0 and lines[i].strip() == '':
        i -= 1
    
    title_end = i
    
    while i >= 0:
        s = lines[i].strip()
        if not s:
            break
        if s.startswith('---PAGE'):
            break
        if is_standalone_time(s):
            time_marker = s
            break
        if s.startswith('Discussant'):
            break
        if s == 'Speaker(s)':
            break
        if s == 'Invitation Only':
            break
        if is_association_abbrev(s):
            assoc = s
            break
        if s.endswith('.') and len(s) > 50:
            break
        if is_date_line(s):
            break
        if is_time_range(s):
            break
        if s.startswith('Philadelphia') or s.startswith('Loews'):
            break
        # Stop at metadata lines that belong to previous session
        if s.startswith('Hosted By:') or s.startswith('Chair:') or s.startswith('Presiding:'):
            break
        if s.startswith('Moderator') or s.startswith('Moderators:'):
            break
        if s.startswith('JEL'):
            break
        # Stop at author/discussant lines (Name, Institution pattern)
        author_check = re.match(r'^(.+),\s+(.+)$', s)
        if author_check:
            potential_inst = author_check.group(2).strip()
            has_inst_keyword = any(kw.lower() in potential_inst.lower() for kw in INST_KEYWORDS)
            if has_inst_keyword:
                break
        i -= 1
    
    for j in range(i + 1, title_end + 1):
        s = lines[j].strip()
        if s and not is_association_abbrev(s) and not is_standalone_time(s) \
           and s != 'Invitation Only' and not s.startswith('---PAGE') \
           and not s.startswith('Hosted By:') and not s.startswith('Chair:') \
           and not s.startswith('Presiding:') and not s.startswith('JEL') \
           and not s.startswith('Moderator'):
            title_parts.append(s)
    
    title = ' '.join(title_parts)
    
    # Clean up: if title has descriptive text before it (ending with period)
    if '. ' in title:
        parts = title.split('. ')
        last_part = parts[-1].strip()
        if last_part and not last_part.startswith('with') and not last_part.startswith('and'):
            title = last_part
    
    return title, i, assoc, time_marker


def parse_one_session(lines, type_line_idx, stype, end_line):
    title, title_start, assoc, time_marker = find_title_backwards(lines, type_line_idx)
    
    if not title:
        return None
    
    body_lines = lines[type_line_idx:end_line]
    body_text = '\n'.join(body_lines)
    
    result = {
        'session_title': title,
        'session_type': stype,
        'association': assoc,
        'time_marker': time_marker,
    }
    
    date_match = re.search(r'(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday),\s*(Jan\.?\s*\d+,\s*\d{4})', body_text)
    if date_match:
        result['date'] = date_match.group(0).strip()
    
    time_match = re.search(r'(\d{1,2}:\d{2}\s*(AM|PM))\s*[-–]\s*(\d{1,2}:\d{2}\s*(AM|PM))\s*\((\w+)\)', body_text)
    if time_match:
        result['time_range'] = time_match.group(0).strip()
    
    loc_match = re.search(r'(Philadelphia\s+(?:Convention Center|Marriott Downtown|Mariott Downtown)[^,\n]*[^,\n]*(?:,\s*[^,\n]*)?)', body_text)
    if loc_match:
        result['location'] = loc_match.group(1).strip()
    else:
        loc_match = re.search(r'(Loews\s+Philadelphia\s+Hotel[^,\n]*(?:,\s*[^,\n]*)?)', body_text)
        if loc_match:
            result['location'] = loc_match.group(1).strip()
    
    hosted_match = re.search(r'Hosted By:\s*(.+?)$', body_text, re.MULTILINE)
    if hosted_match:
        result['hosted_by'] = hosted_match.group(1).strip()
    
    chair_match = re.search(r'Chair:\s*(.+?)$', body_text, re.MULTILINE)
    if chair_match:
        result['chair'] = chair_match.group(1).strip()
    else:
        presiding_match = re.search(r'Presiding:\s*(.+?)$', body_text, re.MULTILINE)
        if presiding_match:
            result['chair'] = presiding_match.group(1).strip()
    
    if stype in ('Paper Session', 'Poster Session', 'Panel Session', 'Lightning Round Session'):
        papers = extract_papers_from_body(body_lines)
        result['papers'] = papers
        result['num_papers'] = len(papers)
    
    return result


def extract_papers_from_body(body_lines):
    """Extract papers from session body lines. 
    Handles multi-line paper titles correctly.
    """
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
                    for j in range(i+1, min(i+15, len(body_lines))):
                        ls = body_lines[j].strip()
                        if ls.startswith('Topic:'):
                            content_start = j + 1
                        elif ls and not ls.startswith('Topic:'):
                            break
                break
    
    if content_start is None:
        return []
    
    content_end = len(body_lines)
    for i in range(content_start, len(body_lines)):
        s = body_lines[i].strip()
        if s.startswith('Discussant') or s.startswith('Topic:'):
            content_end = i
            break
        if is_standalone_time(s):
            content_end = i
            break
        if s == 'Invitation Only':
            content_end = i
            break
        if is_date_line(s):
            content_end = i
            break
    
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
        if s.startswith('Pre registration'):
            continue
        if s.startswith('Register now'):
            continue
        paper_lines.append(s)
    
    # Parse paper_lines into papers
    # KEY FIX: consecutive non-author lines should be concatenated as one title
    papers = []
    current_title_parts = []
    current_authors = []
    last_was_author = False
    
    def save_paper():
        nonlocal last_was_author
        if current_title_parts:
            title = ' '.join(current_title_parts).strip()
            if title and current_authors:
                papers.append({'title': title, 'authors': list(current_authors)})
        current_title_parts.clear()
        current_authors.clear()
        last_was_author = False
    
    for pl in paper_lines:
        author_match = re.match(r'^(.+),\s+(.+)$', pl)
        is_author = False
        
        if author_match:
            potential_name = author_match.group(1).strip()
            potential_inst = author_match.group(2).strip()
            
            has_inst_keyword = any(kw.lower() in potential_inst.lower() for kw in INST_KEYWORDS)
            name_ok = (len(potential_name) < 80 and 
                      not potential_name.endswith(('?', '.', ':')) and
                      not potential_name.startswith('(') and
                      '  ' not in potential_name and
                      not re.match(r'^[A-Z\s]{4,}$', potential_name))
            
            if has_inst_keyword and name_ok:
                is_author = True
        
        if is_author:
            current_authors.append({
                'name': author_match.group(1).strip(),
                'institution': author_match.group(2).strip()
            })
            last_was_author = True
        else:
            # Non-author line (paper title or continuation)
            if last_was_author:
                # Previous line was author, so this is a NEW paper title
                save_paper()
            
            # Append to current title
            current_title_parts.append(pl)
            last_was_author = False
    
    save_paper()
    
    return papers


def build_final_json(sessions):
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
    print("Parsing AEA 2026 program PDF (V5)...")
    sessions = parse_program_pdf('program_full_text.txt')
    
    relevant_types = ('Paper Session', 'Poster Session', 'Panel Session', 'Lightning Round Session')
    paper_sessions = [s for s in sessions if s.get('session_type') in relevant_types]
    
    print(f"\nTotal sessions: {len(sessions)}")
    print(f"Paper/Poster/Panel/Lightning sessions: {len(paper_sessions)}")
    total_papers = sum(s.get('num_papers', 0) for s in paper_sessions)
    print(f"Total paper entries: {total_papers}")
    
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
            print(f"Found: '{s['session_title']}'")
            print(f"  Chair: {s['chair']}")
            print(f"  Papers: {len(s['papers'])}")
            for p in s['papers']:
                print(f"  Title: {p['title'][:120]}")
                for a in p['authors']:
                    print(f"    {a['name']} ({a['institution']})")
            break
    
    for s in result['sessions']:
        if s['session_title'] == 'Digital Money':
            print(f"\nFound: '{s['session_title']}'")
            print(f"  Chair: {s['chair']}")
            print(f"  Papers: {len(s['papers'])}")
            for p in s['papers']:
                print(f"  Title: {p['title'][:80]}")
                for a in p['authors']:
                    print(f"    {a['name']} ({a['institution']})")
            break
    
    # Show some stats
    print(f"\n=== Stats ===")
    print(f"Avg papers per session: {total_papers/len(paper_sessions):.1f}")
    
    # Check for any obviously truncated titles (ends mid-sentence)
    truncated = [p['title'] for s in result['sessions'] for p in s['papers'] 
                 if p['title'].endswith(('the ', 'and ', 'of ', 'in ', 'to ', 'a ', 'an '))]
    if truncated:
        print(f"\nPotentially truncated titles: {len(truncated)}")
        for t in truncated[:5]:
            print(f"  '{t[:80]}'")
