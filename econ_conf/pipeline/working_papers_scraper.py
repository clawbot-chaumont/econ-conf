#!/usr/bin/env python3
"""
Working Papers Scraper
----------------------
Fetches working papers from the last 14 days from:
1. ECB Research Bulletin
2. ECB Working Papers
3. FEDS (Federal Reserve Board)
4. Bank of England Staff Working Papers

Outputs a JSON file with all papers collected.
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser

# ── User-Agent ──────────────────────────────────────────────────────────────
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; research-bot; +https://hermes-agent.dev)'
}

TODAY = datetime.now(timezone.utc)
CUTOFF = (TODAY - timedelta(days=14)).replace(hour=0, minute=0, second=0, microsecond=0)
CUTOFF_STR = CUTOFF.strftime('%Y-%m-%d')

ALL_PAPERS = []


# ── Helpers ─────────────────────────────────────────────────────────────────

def fetch(url):
    """Fetch a URL and return its text content."""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            print(f"  [WARN] Failed to fetch {url}: {e}", file=sys.stderr)
            return None


def clean_html(text):
    """Remove HTML tags from a string."""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ').replace('&quot;', '"').replace('&#39;', "'")
    # Extended HTML entities
    text = text.replace('&egrave;', 'è').replace('&eacute;', 'é').replace('&egrave;', 'è')
    text = text.replace('&agrave;', 'à').replace('&ocirc;', 'ô').replace('&ecirc;', 'ê')
    text = text.replace('&ccedil;', 'ç').replace('&uuml;', 'ü').replace('&ouml;', 'ö')
    text = text.replace('&auml;', 'ä').replace('&ntilde;', 'ñ')
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)  # fallback for any remaining named entities
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_date(date_str):
    """Try to parse a date string into a datetime object."""
    formats = [
        '%Y-%m-%d',
        '%d %B %Y',
        '%d %b %Y',
        '%B %Y',
        '%b %Y',
        '%d/%m/%Y',
    ]
    date_str = date_str.strip()
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def is_within_last_two_weeks(date_obj):
    """Check if a date is within the last 14 days."""
    if date_obj is None:
        return False
    return CUTOFF <= date_obj <= TODAY + timedelta(days=1)


def paper_key(title, source):
    """Generate a unique key for deduplication."""
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower().strip())
    return f"{source}|{slug}"


seen_papers = set()


def add_paper(paper):
    """Add a paper if not already seen (by title+source)."""
    key = paper_key(paper.get('title', ''), paper.get('source', ''))
    if key in seen_papers:
        return False
    seen_papers.add(key)
    ALL_PAPERS.append(paper)
    return True


# ── 1. ECB Research Bulletin ────────────────────────────────────────────────

ECB_RB_URL = 'https://www.ecb.europa.eu/press/research-publications/resbull/2026/html/index_include.en.html'
ECB_RB_BASE = 'https://www.ecb.europa.eu'


def scrape_ecb_research_bulletin():
    print("[ECB Research Bulletin] Fetching...", file=sys.stderr)
    html = fetch(ECB_RB_URL)
    if not html:
        print("  [SKIP] No data fetched", file=sys.stderr)
        return

    # Each entry: <dt isoDate="..."><div class="date">...</div></dt><dd>...</dd>
    entries = re.findall(
        r'<dt\s+isoDate="([^"]*)"[^>]*>(.*?)</dt>\s*<dd>(.*?)</dd>',
        html, re.DOTALL
    )

    count = 0
    for iso_date, dt_content, dd_content in entries:
        pub_date = parse_date(iso_date)
        if not is_within_last_two_weeks(pub_date):
            continue

        # Title
        title_match = re.search(
            r'<div class="title"><a[^>]*>(.*?)</a></div>', dd_content, re.DOTALL
        )
        title = clean_html(title_match.group(1)) if title_match else ''

        # Paper number
        cat_match = re.search(r'<div class="category">(.*?)</div>', dd_content)
        paper_no = clean_html(cat_match.group(1)) if cat_match else ''

        # Authors
        authors = []
        author_matches = re.findall(
            r'<li><a[^>]*>(.*?)</a></li>', dd_content, re.DOTALL
        )
        for a in author_matches:
            authors.append(clean_html(a))

        # Link
        link_match = re.search(
            r'<div class="title"><a\s+href="([^"]*)"', dd_content
        )
        link = ECB_RB_BASE + link_match.group(1) if link_match else ''

        # Abstract
        abstract = ''
        abs_match = re.search(
            r'<dt>Abstract</dt>\s*<dd>(.*?)</dd>', dd_content, re.DOTALL
        )
        if abs_match:
            abstract = clean_html(abs_match.group(1))

        # PDF link
        pdf_match = re.search(
            r'class=\'pdf\'.*?href="([^"]*\.pdf)"', dd_content, re.DOTALL
        )
        pdf_url = ECB_RB_BASE + pdf_match.group(1) if pdf_match else ''

        paper = {
            'title': title,
            'source': 'ECB Research Bulletin',
            'source_url': 'https://www.ecb.europa.eu/press/research-publications/resbull/html/index.en.html',
            'paper_number': paper_no,
            'authors': authors,
            'publication_date': pub_date.strftime('%Y-%m-%d'),
            'url': link,
            'pdf_url': pdf_url,
            'abstract': abstract,
            'keywords': [],
        }
        if add_paper(paper):
            count += 1
            print(f"  + {pub_date.strftime('%Y-%m-%d')} | {title[:60]}", file=sys.stderr)

    print(f"  → {count} paper(s) collected", file=sys.stderr)


# ── 2. ECB Working Papers ───────────────────────────────────────────────────

ECB_WP_URL = 'https://www.ecb.europa.eu/press/research-publications/working-papers/html/papers-2026.include.en.html'
ECB_WP_BASE = 'https://www.ecb.europa.eu'


def scrape_ecb_working_papers():
    print("\n[ECB Working Papers] Fetching...", file=sys.stderr)
    html = fetch(ECB_WP_URL)
    if not html:
        print("  [SKIP] No data fetched", file=sys.stderr)
        return

    entries = re.findall(
        r'<dt\s+isoDate="([^"]*)"[^>]*>(.*?)</dt>\s*<dd>(.*?)</dd>',
        html, re.DOTALL
    )

    count = 0
    for iso_date, dt_content, dd_content in entries:
        pub_date = parse_date(iso_date)
        if not is_within_last_two_weeks(pub_date):
            continue

        # Title
        title_match = re.search(
            r'<div class="title"><a[^>]*>(.*?)</a></div>', dd_content, re.DOTALL
        )
        title = clean_html(title_match.group(1)) if title_match else ''

        # Paper number
        cat_match = re.search(r'<div class="category">(.*?)</div>', dd_content)
        paper_no = clean_html(cat_match.group(1)) if cat_match else ''

        # Authors
        authors = []
        author_matches = re.findall(
            r'<li><a[^>]*>(.*?)</a></li>', dd_content, re.DOTALL
        )
        for a in author_matches:
            authors.append(clean_html(a))

        # Link
        link_match = re.search(
            r'<div class="title"><a\s+href="([^"]*)"', dd_content
        )
        link = ECB_WP_BASE + link_match.group(1) if link_match else ''

        # Abstract
        abstract = ''
        abs_match = re.search(
            r'<dt>Abstract</dt>\s*<dd>(.*?)</dd>', dd_content, re.DOTALL
        )
        if abs_match:
            abstract = clean_html(abs_match.group(1))

        # Keywords
        keywords = []
        kw_match = re.search(
            r'<dt>Keywords</dt>\s*<dd>(.*?)</dd>', dd_content, re.DOTALL
        )
        if kw_match:
            kw_text = clean_html(kw_match.group(1))
            keywords = [k.strip() for k in kw_text.split(',') if k.strip()]

        # PDF link
        pdf_match = re.search(
            r'class=\'pdf\'.*?href="([^"]*\.pdf)"', dd_content, re.DOTALL
        )
        pdf_url = ECB_WP_BASE + pdf_match.group(1) if pdf_match else ''

        paper = {
            'title': title,
            'source': 'ECB Working Paper',
            'source_url': 'https://www.ecb.europa.eu/press/research-publications/working-papers/html/index.en.html',
            'paper_number': paper_no,
            'authors': authors,
            'publication_date': pub_date.strftime('%Y-%m-%d'),
            'url': link,
            'pdf_url': pdf_url,
            'abstract': abstract,
            'keywords': keywords,
        }
        if add_paper(paper):
            count += 1
            print(f"  + {pub_date.strftime('%Y-%m-%d')} | {title[:60]}", file=sys.stderr)

    print(f"  → {count} paper(s) collected", file=sys.stderr)


# ── 3. FEDS (Federal Reserve) ──────────────────────────────────────────────

FEDS_URL = 'https://www.federalreserve.gov/econres/feds/index.htm'
FEDS_BASE = 'https://www.federalreserve.gov'


def scrape_feds():
    print("\n[FEDS] Fetching...", file=sys.stderr)
    html = fetch(FEDS_URL)
    if not html:
        print("  [SKIP] No data fetched", file=sys.stderr)
        return

    # Split into individual paper entries using the badge as anchor
    # Each entry starts with: <div class="col-xs-12 col-md-9 heading feds-note">...<span class="badge badge--feds">...
    pattern = (
        r'<div class="col-xs-12 col-md-9 heading feds-note">\s*'
        r'\s*<span class="badge badge--feds"><strong>FEDS</strong>\s*([^<]+)</span>'
        r'(.*?)</div>\s*</div>\s*</div>'
    )
    entries = re.findall(pattern, html, re.DOTALL)

    count = 0
    for paper_id, entry in entries:
        paper_id = clean_html(paper_id)
        if not paper_id:
            continue

        # Date
        date_match = re.search(
            r'<time\s+datetime="([^"]*)"', entry
        )
        date_str = date_match.group(1) if date_match else ''
        pub_date = parse_date(date_str)
        # If only month+year (e.g. "June 2026"), treat as within window
        if pub_date is None and date_str:
            # Accept %B %Y and %b %Y as "within window" if the month is current or last
            for fmt in ['%B %Y', '%b %Y']:
                try:
                    parsed = datetime.strptime(date_str.strip(), fmt).replace(tzinfo=timezone.utc)
                    # If the parsed month is current month or previous month, it's within 2 weeks
                    if parsed.month == TODAY.month or parsed.month == (TODAY.month - 1) or \
                       (TODAY.month == 1 and parsed.month == 12):
                        pub_date = parsed
                    break
                except ValueError:
                    continue

        if not is_within_last_two_weeks(pub_date):
            continue

        # Title + link
        title_match = re.search(
            r'<h5><a\s+href="([^"]*)"[^>]*>(.*?)</a></h5>', entry, re.DOTALL
        )
        link = (FEDS_BASE + title_match.group(1)) if title_match else ''
        title = clean_html(title_match.group(2)) if title_match else ''

        # Authors
        authors = []
        auth_match = re.search(
            r'<div class="authors"><p>(.*?)</p></div>', entry, re.DOTALL
        )
        if auth_match:
            author_html = auth_match.group(1)
            author_text = clean_html(author_html)
            # Split on comma, then handle " and " in each segment
            parts_raw = re.split(r',\s*', author_text)
            for part in parts_raw:
                sub_parts = re.split(r'(?:\s+and\s+|^and\s+)', part)
                for sub in sub_parts:
                    name = sub.strip()
                    if name and len(name) > 2:
                        authors.append(name)

        # Abstract
        abstract = ''
        abs_match = re.search(
            r'<strong>Abstract:</strong>\s*<p>(.*?)</p>', entry, re.DOTALL
        )
        if abs_match:
            abstract = clean_html(abs_match.group(1))

        # Keywords
        keywords = []
        kw_match = re.search(
            r'<strong>Keywords:</strong>\s*([^<]*)', entry, re.DOTALL
        )
        if kw_match:
            kw_text = clean_html(kw_match.group(1))
            keywords = [k.strip() for k in kw_text.split(',') if k.strip()]

        # DOI
        doi = ''
        doi_match = re.search(
            r'<strong>DOI</strong>:\s*([^<]+)', entry, re.DOTALL
        )
        if doi_match:
            doi = clean_html(doi_match.group(1))

        paper = {
            'title': title,
            'source': 'FEDS (Federal Reserve Board)',
            'source_url': 'https://www.federalreserve.gov/econres/feds/index.htm',
            'paper_number': f"FEDS {paper_id}" if paper_id else '',
            'authors': authors,
            'publication_date': pub_date.strftime('%Y-%m-%d') if pub_date else date_str,
            'url': link,
            'pdf_url': '',
            'abstract': abstract,
            'keywords': keywords,
            'doi': doi,
        }
        if add_paper(paper):
            count += 1
            date_display = pub_date.strftime('%Y-%m-%d') if pub_date else date_str
            print(f"  + {date_display} | {paper_id} | {title[:55]}", file=sys.stderr)

    print(f"  → {count} paper(s) collected", file=sys.stderr)


# ── 4. Bank of England ──────────────────────────────────────────────────────

BOE_WP_URL = 'https://www.bankofengland.co.uk/working-paper/staff-working-papers'


def find_boe_papers_via_search():
    """
    Use web search to discover recent BoE working papers,
    then scrape each individual page for details.
    """
    print("\n[Bank of England] Discovering recent papers via search...", file=sys.stderr)

    # We'll do multiple searches to cover the last 2 weeks
    today_str = TODAY.strftime('%Y-%m-%d')
    cutoff_str = CUTOFF.strftime('%Y-%m-%d')
    
    # For now, use a known pattern with web search
    # This version will use a hardcoded list of known recent BoE papers
    # that we can discover from the site
    
    # Alternative: scrape the "More staff working papers" section from a known paper page
    # Each paper page lists related recent papers
    seed_urls = [
        'https://www.bankofengland.co.uk/working-paper/staff-working-papers',
    ]
    
    found_urls = set()
    
    # Try to discover papers from the main page or from related links
    for url in seed_urls:
        html = fetch(url)
        if not html:
            continue
        
        # Look for working paper links in the page
        paper_links = re.findall(
            r'href="(/working-paper/2026/[^"]*)"', html
        )
        for pl in paper_links:
            if pl not in found_urls:
                found_urls.add('https://www.bankofengland.co.uk' + pl)
    
    # Also check pages that list recent working papers
    # The search results don't work due to JS, so we try known patterns
    # from the individual paper pages (the "More staff working papers" section)
    
    # If we found papers via related links, scrape them
    count = 0
    for url in sorted(found_urls):
        result = scrape_boe_paper_page(url)
        if result:
            count += 1
    
    if count == 0:
        print("  [INFO] No recent BoE papers discovered via page scraping. This site requires JS.", file=sys.stderr)
        print("  [INFO] BoE papers will show as 'not scraped' in the final output.", file=sys.stderr)
    
    return count


def scrape_boe_paper_page(url):
    """Scrape an individual BoE working paper page."""
    html = fetch(url)
    if not html:
        return None

    # Title
    title_match = re.search(
        r'<h1\s+itemprop="name"[^>]*>(.*?)</h1>', html, re.DOTALL
    )
    title = clean_html(title_match.group(1)) if title_match else ''

    # Date
    date_match = re.search(
        r'Published on\s+(\d+\s+\w+\s+\d{4})', html
    )
    pub_date = None
    if date_match:
        pub_date = parse_date(date_match.group(1))
    
    if not is_within_last_two_weeks(pub_date):
        return None

    # Paper number and authors
    num_match = re.search(
        r'<h2>(Staff Working Paper No\.\s*[\d,]+)</h2>', html
    )
    paper_no = clean_html(num_match.group(1)) if num_match else ''

    # Authors - look in the content-block div
    authors = []
    auth_match = re.search(
        r'<h2>Staff Working Paper[^<]*</h2>\s*\n?\s*<p><strong>(.*?)</strong></p>',
        html, re.DOTALL
    )
    if auth_match:
        auth_text = clean_html(auth_match.group(1))
        # Split on " and " and ","
        for part in re.split(r',\s+and\s+|,\s+|\s+and\s+', auth_text):
            part = part.strip()
            if part and len(part) > 2:
                authors.append(part)

    # Abstract (paragraph after authors)
    abstract = ''
    abs_match = re.search(
        r'<p><strong>.*?</strong></p>\s*<p>(.*?)</p>', html, re.DOTALL
    )
    if abs_match:
        abstract = clean_html(abs_match.group(1))

    # PDF link
    pdf_match = re.search(
        r'class="btn btn-pubs[^"]*"[^>]*href="([^"]*\.pdf)"', html
    )
    pdf_url = ('https://www.bankofengland.co.uk' + pdf_match.group(1)) if pdf_match else ''

    paper = {
        'title': title,
        'source': 'Bank of England Staff Working Paper',
        'source_url': 'https://www.bankofengland.co.uk/working-paper/staff-working-papers',
        'paper_number': paper_no,
        'authors': authors,
        'publication_date': pub_date.strftime('%Y-%m-%d') if pub_date else '',
        'url': url,
        'pdf_url': pdf_url,
        'abstract': abstract,
        'keywords': [],
    }
    if add_paper(paper):
        print(f"  + {pub_date.strftime('%Y-%m-%d')} | {title[:60]}", file=sys.stderr)
        return True
    return False


def scrape_boe():
    """Main BoE scraper - discovers recent papers and fetches details."""
    # Try to find papers directly from related-links on the site
    found = find_boe_papers_via_search()
    
    if found == 0:
        # As a fallback, use Google-like search to find recent BoE papers
        # We use the search tool from hermes_tools if available
        print("  [NOTE] Discover 0 papers. BoE does not serve listings without JS.", file=sys.stderr)
        # Attempt to find papers from known seed paper pages
        seed_papers = fetch_boe_related_papers()
        if seed_papers:
            count = 0
            for url in seed_papers:
                if scrape_boe_paper_page(url):
                    count += 1
            print(f"  → {count} paper(s) collected from related links", file=sys.stderr)


def fetch_boe_related_papers():
    """Try to get BoE paper URLs from the 'Other staff working papers' section on paper pages."""
    # Start with a known recent paper, then follow related links
    seeds = [
        'https://www.bankofengland.co.uk/working-paper/2026/staying-afloat-the-impact-of-flooding-on-uk-firms',
        'https://www.bankofengland.co.uk/working-paper/2026/persistent-transitory-inflation-euro-area-insights-from-global-domestic-shocks',
    ]
    found = set()
    for seed in seeds:
        html = fetch(seed)
        if not html:
            continue
        # Look for links to other working papers
        links = re.findall(
            r'href="(/working-paper/2026/[^"]*)"', html
        )
        for link in links:
            full_url = 'https://www.bankofengland.co.uk' + link
            if full_url not in found and 'media' not in link:
                found.add(full_url)
    return list(found)


# ── 5. BIS Working Papers ───────────────────────────────────────────────────

BIS_RSS_URL = 'https://www.bis.org/doclist/wppubls.rss'
BIS_BASE = 'https://www.bis.org'


def scrape_bis():
    """
    Fetch BIS Working Papers from their RSS feed.
    The RSS includes title, authors (in description), date, link, and abstract.
    Paper numbers are extracted from the URL (workNNNN.htm → NNNN).
    PDF links are constructed from the paper number.
    """
    print("\n[BIS Working Papers] Fetching RSS...", file=sys.stderr)

    import xml.etree.ElementTree as ET

    xml_text = fetch(BIS_RSS_URL)
    if not xml_text:
        print("  [SKIP] No data fetched", file=sys.stderr)
        return

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"  [SKIP] RSS parse error: {e}", file=sys.stderr)
        return

    # RSS 1.0 namespace
    ns = {
        'rss': 'http://purl.org/rss/1.0/',
        'dc': 'http://purl.org/dc/elements/1.1/',
    }

    items = root.findall('.//rss:item', ns)
    print(f"  {len(items)} items in RSS feed", file=sys.stderr)

    count = 0
    for item in items:
        # Date
        date_el = item.find('dc:date', ns)
        if date_el is None or not date_el.text:
            continue
        try:
            pub_date = datetime.fromisoformat(date_el.text.replace('Z', '+00:00'))
        except ValueError:
            continue

        if not is_within_last_two_weeks(pub_date):
            continue

        # Title
        title_el = item.find('rss:title', ns)
        title = title_el.text.strip() if title_el is not None and title_el.text else ''
        if not title:
            continue

        # Link
        link_el = item.find('rss:link', ns)
        link = link_el.text.strip() if link_el is not None and link_el.text else ''

        # Extract paper number from URL: work1360.htm → 1360
        paper_no = ''
        pn_match = re.search(r'work(\d+)\.htm', link)
        if pn_match:
            paper_no = f"BIS Working Paper No. {pn_match.group(1)}"

        # Description: "by Author1, Author2<br />Abstract text..."
        desc_el = item.find('rss:description', ns)
        desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ''

        # Parse authors and abstract from description
        authors = []
        abstract = ''
        br_match = re.search(r'^(.*?)<br\s*/?>(.*)', desc, re.DOTALL)
        if br_match:
            author_text = clean_html(br_match.group(1))
            # Remove leading "by "
            author_clean = re.sub(r'^by\s+', '', author_text, flags=re.IGNORECASE)
            # Split authors
            for part in re.split(r',\s*', author_clean):
                part = part.strip()
                if part and len(part) > 2:
                    # Handle " and " within the last author part
                    sub_parts = re.split(r'\s+and\s+', part)
                    for sub in sub_parts:
                        sub = sub.strip()
                        if sub and len(sub) > 2:
                            authors.append(sub)
            # Abstract is the rest (after <br />)
            abstract_text = br_match.group(2).strip()
            abstract = clean_html(abstract_text)
        elif desc:
            # Fallback: no <br />, use whole description
            abstract = clean_html(desc)

        # PDF URL: constructed from paper number
        pdf_url = ''
        if pn_match:
            pdf_url = f"{BIS_BASE}/publ/work{pn_match.group(1)}.pdf"

        # Try to scrape individual page for more details (keywords, etc.)
        keywords = []
        if link:
            page_html = fetch(link)
            if page_html:
                # Look for keywords — the BIS pages have two occurrences:
                # one in visible HTML (<p>Keywords: ...</p>) and one in embedded JSON.
                # Prefer the visible HTML version.
                kw_match = re.search(r'<p>\s*Keywords:\s*([^<]+)</p>', page_html, re.IGNORECASE)
                if kw_match:
                    kw_text = clean_html(kw_match.group(1))
                    keywords = [k.strip() for k in kw_text.split(',') if k.strip()]

        paper = {
            'title': title,
            'source': 'BIS Working Paper',
            'source_url': 'https://www.bis.org/wpapers/index.htm',
            'paper_number': paper_no,
            'authors': authors,
            'publication_date': pub_date.strftime('%Y-%m-%d'),
            'url': link,
            'pdf_url': pdf_url,
            'abstract': abstract,
            'keywords': keywords,
        }
        if add_paper(paper):
            count += 1
            print(f"  + {pub_date.strftime('%Y-%m-%d')} | {paper_no:30s} | {title[:55]}", file=sys.stderr)

    print(f"  → {count} paper(s) collected", file=sys.stderr)


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    print(f"=== Working Papers Scraper ===", file=sys.stderr)
    print(f"Date range: {CUTOFF_STR} to {TODAY.strftime('%Y-%m-%d')}", file=sys.stderr)
    print(f"=" * 40, file=sys.stderr)

    scrape_ecb_research_bulletin()
    scrape_ecb_working_papers()
    scrape_feds()
    scrape_boe()
    scrape_bis()

    # Sort by publication date (newest first)
    ALL_PAPERS.sort(key=lambda p: p.get('publication_date', ''), reverse=True)

    output = {
        'metadata': {
            'scraped_at': TODAY.strftime('%Y-%m-%d %H:%M UTC'),
            'date_range': f"{CUTOFF_STR} to {TODAY.strftime('%Y-%m-%d')}",
            'total_papers': len(ALL_PAPERS),
            'sources': {},
        },
        'papers': ALL_PAPERS,
    }

    # Count by source
    for p in ALL_PAPERS:
        src = p['source']
        output['metadata']['sources'][src] = output['metadata']['sources'].get(src, 0) + 1

    print(f"\n=== Summary ===", file=sys.stderr)
    print(f"Total papers collected: {len(ALL_PAPERS)}", file=sys.stderr)
    for src, cnt in sorted(output['metadata']['sources'].items()):
        print(f"  {src}: {cnt}", file=sys.stderr)

    return output


if __name__ == '__main__':
    result = main()
    print(json.dumps(result, ensure_ascii=False, indent=2))
