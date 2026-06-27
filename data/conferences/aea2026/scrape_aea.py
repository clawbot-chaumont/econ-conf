#!/usr/bin/env python3
"""
Scrape the AEA 2026 Annual Meeting program.
Uses Playwright for JS-rendered listing pages, then direct HTTP for detail pages.
Updated to capture institutions and output v2 schema directly.
"""
import json
import os
import time
import requests
from collections import defaultdict
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://www.aeaweb.org"
OUTPUT_DIR = os.path.expanduser("~/economics-conferences/aea2026")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def scrape_listing_page(browser, page_num):
    """Scrape a single listing page for session metadata."""
    url = f"{BASE_URL}/conference/2026/program?page={page_num}&per-page=50"
    
    page = browser.new_page()
    sessions = []
    try:
        page.goto(url, timeout=30000, wait_until='networkidle')
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        articles = soup.find_all('article', class_='session-item')
        
        for art in articles:
            session_id = art.get('id', '')
            
            h3 = art.find('h3', class_='title')
            title_link = h3.find('a') if h3 else None
            session_title = title_link.get_text(strip=True) if title_link else ''
            session_href = title_link.get('href', '') if title_link else ''
            
            # Build absolute URL
            if session_href.startswith('/'):
                session_url = BASE_URL + session_href
            elif session_href.startswith('http'):
                session_url = session_href
            elif session_href:
                session_url = BASE_URL + '/conference/2026/' + session_href
            else:
                session_url = ''
            
            # Session type
            location_span = art.find('span', class_='location')
            session_type = location_span.get_text(strip=True) if location_span else ''
            
            # Chair(s)
            chairs = []
            presiding_items = art.find_all('li', class_='presiding')
            for item in presiding_items:
                name_span = item.find('span', class_='name')
                org_span = item.find('span', class_='organization')
                name = name_span.get_text(strip=True).rstrip(',') if name_span else ''
                org = org_span.get_text(strip=True) if org_span else ''
                if name:
                    chairs.append({'name': name, 'institution': org})
            
            sessions.append({
                'id': session_id,
                'title': session_title,
                'url': session_url,
                'type': session_type,
                'chairs': chairs,
            })
    except Exception as e:
        print(f"    Error on page {page_num}: {e}")
    finally:
        page.close()
    
    return sessions


def scrape_session_detail_http(session_url):
    """Scrape a session detail page with direct HTTP request.
    Captures paper titles, authors, and their institutions."""
    if not session_url:
        return []
    
    papers = []
    try:
        resp = requests.get(session_url, timeout=15, 
                           headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        paper_articles = soup.find_all('article', class_='paper')
        
        for paper_art in paper_articles:
            title_el = paper_art.find('h3', class_='paper-title')
            paper_title = title_el.get_text(strip=True) if title_el else ''
            if not paper_title:
                continue
            
            authors_list = []
            author_divs = paper_art.find_all('div', class_='author')
            for auth_div in author_divs:
                name_div = auth_div.find('div', class_='name')
                org_div = auth_div.find('div', class_='organization')
                
                name = name_div.get_text(strip=True) if name_div else ''
                org = org_div.get_text(strip=True) if org_div else ''
                
                if name:
                    authors_list.append({
                        'name': name.rstrip(',').strip(),
                        'institution': org
                    })
            
            if paper_title and authors_list:
                papers.append({
                    'title': paper_title,
                    'authors': authors_list
                })
    
    except Exception as e:
        pass
    
    return papers


def main():
    print("=== AEA 2026 Program Scraper (v2 — with institutions) ===")
    start_time = time.time()
    
    all_sessions = []
    
    # Step 1: Scrape listing pages with Playwright
    print("\n[Step 1] Scraping session listings (11 pages)...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for page_num in range(1, 12):
            print(f"  Page {page_num}/11...")
            sessions = scrape_listing_page(browser, page_num)
            all_sessions.extend(sessions)
            print(f"    Found {len(sessions)} sessions (total: {len(all_sessions)})")
        
        browser.close()
    
    # Deduplicate by session ID (AEA pagination returns same 50 sessions on every page)
    seen_ids = set()
    unique_sessions = []
    for s in all_sessions:
        sid = s.get('id', '')
        if sid and sid not in seen_ids:
            seen_ids.add(sid)
            unique_sessions.append(s)
    dupes_removed = len(all_sessions) - len(unique_sessions)
    all_sessions = unique_sessions
    
    # Save listing
    meta_path = os.path.join(OUTPUT_DIR, 'sessions_meta.json')
    with open(meta_path, 'w') as f:
        json.dump(all_sessions, f, indent=2)
    
    sessions_with_urls = [s for s in all_sessions if s['url']]
    print(f"\nTotal sessions (after dedup): {len(all_sessions)} (with URLs: {len(sessions_with_urls)}) (removed {dupes_removed} dupes)")
    
    # Step 2: Scrape session detail pages with concurrent HTTP
    print(f"\n[Step 2] Scraping {len(sessions_with_urls)} session detail pages for papers + institutions...")
    
    session_papers = {}
    failed = 0
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_sess = {
            executor.submit(scrape_session_detail_http, s['url']): s 
            for s in sessions_with_urls
        }
        
        completed = 0
        for future in as_completed(future_to_sess):
            sess = future_to_sess[future]
            try:
                papers = future.result()
                session_papers[sess['url']] = papers
                if not papers:
                    failed += 1
            except Exception as e:
                session_papers[sess['url']] = []
                failed += 1
            
            completed += 1
            if completed % 50 == 0:
                print(f"  Progress: {completed}/{len(sessions_with_urls)}")
    
    total_with_papers = sum(1 for v in session_papers.values() if v)
    total_paper_count = sum(len(v) for v in session_papers.values())
    total_author_count = sum(len(p['authors']) for papers in session_papers.values() for p in papers)
    total_inst_count = sum(sum(1 for a in p['authors'] if a.get('institution')) for papers in session_papers.values() for p in papers)
    print(f"  Sessions with papers: {total_with_papers}")
    print(f"  Total paper entries: {total_paper_count}")
    print(f"  Total authors: {total_author_count}")
    print(f"  Authors with institution: {total_inst_count}")
    print(f"  Failed/empty sessions: {failed}")
    
    # Step 3: Build v2 output directly
    print("\n[Step 3] Building final v2 output...")
    
    v2_sessions = []
    participant_data = {}
    
    for sess in all_sessions:
        chair_str = '; '.join([c['name'] for c in sess['chairs']]) if sess['chairs'] else ''
        
        papers_for_session = session_papers.get(sess['url'], [])
        paper_entries = []
        
        for p in papers_for_session:
            # Group: unique paper title → list of authors (strings) + presenter
            author_names = [a['name'] for a in p['authors']]
            presenter = author_names[0] if author_names else ''
            
            paper_entries.append({
                'title': p['title'],
                'authors': author_names,
                'presenter': presenter
            })
            
            # Build participant index with institutions
            for author in p['authors']:
                name = author['name']
                inst = author['institution']
                if name not in participant_data:
                    participant_data[name] = {
                        'name': name,
                        'institution': inst if inst else '',
                        'is_presenter': False,
                        'papers': []
                    }
                if p['title'] not in participant_data[name]['papers']:
                    participant_data[name]['papers'].append(p['title'])
                # Only set institution if not already set (keep first known)
                if inst and not participant_data[name]['institution']:
                    participant_data[name]['institution'] = inst
        
        v2_session = {
            'session_title': sess['title'],
            'session_type': sess.get('type', ''),
        }
        if chair_str:
            v2_session['chair'] = chair_str
        v2_session['papers'] = paper_entries
        
        v2_sessions.append(v2_session)
    
    # Mark presenters: first author of each paper is the presenter
    for s in v2_sessions:
        for p in s['papers']:
            presenter = p.get('presenter', '')
            if presenter and presenter in participant_data:
                participant_data[presenter]['is_presenter'] = True
    
    participants_list = sorted(participant_data.values(), key=lambda x: x['name'])
    
    # Count institutions
    inst_counts = defaultdict(int)
    for p in participants_list:
        if p.get('institution'):
            inst_counts[p['institution']] += 1
    top_insts = sorted(inst_counts.items(), key=lambda x: -x[1])[:5]
    
    output = {
        'conference': {
            'name': 'American Economic Association Annual Meeting',
            'short_name': 'AEA',
            'year': 2026,
            'start_date': '2026-01-03',
            'end_date': '2026-01-05',
            'location': 'San Francisco, USA',
        },
        'scrape_metadata': {
            'scraped_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'source_url': 'https://www.aeaweb.org/conference/2026/program',
            'program_available': True,
            'program_type': 'web',
            'errors': [],
        },
        'sessions': v2_sessions,
        'participants': participants_list,
    }
    
    output_path = os.path.join(OUTPUT_DIR, 'data.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    elapsed = time.time() - start_time
    print(f"\n=== Done in {elapsed:.1f}s ===")
    print(f"Sessions: {len(v2_sessions)}")
    print(f"Papers: {sum(len(s['papers']) for s in v2_sessions)}")
    print(f"Unique participants: {len(participants_list)}")
    print(f"Participants with institution: {sum(1 for p in participants_list if p.get('institution'))}")
    print(f"Output: {output_path}")
    print(f"\nTop institutions:")
    for inst, count in top_insts:
        print(f"  {inst}: {count}")


if __name__ == '__main__':
    main()
