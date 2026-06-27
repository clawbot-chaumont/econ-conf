#!/usr/bin/env python3
"""
SciencesConf Conference Scraper — extracts sessions, papers, authors, and
institutions from SciencesConf.org conference programs (PDF or HTML).

Usage:
    python3 sciencesconf_scraper.py <url> [output_dir]

Examples:
    # From conference home page (auto-detect PDF)
    python3 sciencesconf_scraper.py "https://afse2026.sciencesconf.org" ~/data/afse2026

    # Direct PDF URL
    python3 sciencesconf_scraper.py "/path/to/program.pdf" ~/data/afse2026
"""
import re, json, sys, os, urllib.request, urllib.error
from collections import Counter, defaultdict

# ── Shared normalization (import from conftool_scraper) ──────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
try:
    from conftool_scraper import clean_institution_name, SAFE_MERGES
except ImportError:
    # Fallback: minimal inline version
    import unicodedata
    def clean_institution_name(name):
        if not name: return ""
        import unicodedata
        s = name.replace('&amp;', '&').replace('&amp', '&')
        s = re.sub(r'^\d+\s*', '', s)
        countries = '|'.join(['united states of america','united states','usa','united kingdom','uk',
            'france','germany','spain','italy','switzerland','netherlands','china','singapore',
            'australia','sweden','denmark','belgium','austria','norway','finland','portugal',
            'ireland','japan','india','brazil','israel','turkey','poland','mexico','canada'])
        s = re.sub(r',\s*(' + countries + r')\s*$', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\s+', ' ', s).strip()
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
        return s
    SAFE_MERGES = {}


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as e:
            if attempt < retries - 1:
                import time; time.sleep(1.5)
                continue
            raise


# ── PDF parsing (PyMuPDF) ─────────────────────────────────────
def parse_pdf(pdf_path):
    """Parse a SciencesConf PDF program using PyMuPDF.
    Returns list of session dicts."""
    try:
        import fitz
    except ImportError:
        print("ERROR: PyMuPDF (fitz) required. Install with: pip install pymupdf")
        sys.exit(1)

    doc = fitz.open(pdf_path)

    COLUMNS = [
        (22, 130), (135, 242), (248, 362), (365, 478),
        (478, 597), (598, 710), (712, 820),
    ]

    def col_for_block(x0, x1):
        cx = (x0 + x1) / 2
        for i, (c0, c1) in enumerate(COLUMNS):
            if c0 <= cx <= c1: return i
        return -1

    def parse_block(text):
        lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
        if len(lines) < 3: return None
        # Fix hyphenated line breaks
        merged = []
        for l in lines:
            if merged and (merged[-1].endswith('-') or len(l) < 12):
                merged[-1] = merged[-1].rstrip('-') + ' ' + l
            else:
                merged.append(l)
        return {"author": merged[0] if len(merged) > 0 else "",
                "institution": merged[1] if len(merged) > 1 else "",
                "title": ' '.join(merged[2:]).strip() if len(merged) > 2 else ""}

    all_sessions = []
    for pnum in range(len(doc)):
        page = doc[pnum]
        blocks = page.get_text("blocks")
        text_blocks = [(b[0], b[1], b[2], b[3], b[4]) for b in blocks
                       if b[6] == 0 and len(b[4].strip()) > 3]
        if len(text_blocks) < 15: continue

        col_groups = {i: [] for i in range(7)}
        for b in text_blocks:
            c = col_for_block(b[0], b[2])
            if c >= 0: col_groups[c].append(b)
        for c in col_groups:
            col_groups[c].sort(key=lambda b: b[1])

        for col_idx in range(7):
            blocks = col_groups[col_idx]
            if len(blocks) < 3: continue

            # Find Chair
            chair_idx = -1
            for i, b in enumerate(blocks):
                if 'Chair' in b[4]: chair_idx = i; break
            if chair_idx < 0: continue

            # Title
            title_parts = []
            for b in blocks[:chair_idx]:
                t = b[4].strip()
                if len(t) > 4 and 'Room' not in t and 'Agora' not in t:
                    title_parts.append(t)
            title = re.sub(r'\s+', ' ', ' '.join(title_parts)).strip()

            skip = ['coffee','lunch','break','lecture','round table','cocktail',
                    'gala','welcome','registration','opening','presidential',
                    'general meeting','wednesday','thursday','friday','parallel sessions',
                    'inaugural','keynote','08h30','09h00','10h30','11h00',
                    '12h30','13h30','14h00','15h30','16h00','17h30']
            if len(title) < 8 or any(s in title.lower() for s in skip): continue

            # Room & Chair
            room = ""
            for b in blocks[:chair_idx]:
                t = b[4].strip()
                m = re.search(r'Room\s+(\d+)', t)
                if m: room = f"Room {m.group(1)}"; break
                if 'Agora' in t: room = 'Agora'; break
            chair = re.sub(r'Chair\s*:?\s*', '', blocks[chair_idx][4].strip()).strip()

            # Papers
            papers = []
            for b in blocks[chair_idx + 1:]:
                p = parse_block(b[4])
                if p and p['title'] and len(p['title']) > 5:
                    papers.append(p)

            if papers:
                all_sessions.append({
                    "session_title": title, "room": room,
                    "chair": chair, "papers": papers
                })

    doc.close()
    return all_sessions


# ── HTML-based fallback ────────────────────────────────────────
def find_pdf_url(conference_url):
    """Find PDF program URL from a SciencesConf conference page."""
    html = fetch(conference_url).decode('utf-8', errors='replace')

    # Method 1: Look for PDF links on the page
    pdf_links = re.findall(r'href=["\']([^"\']*\.pdf)["\']', html, re.IGNORECASE)
    if pdf_links:
        for link in pdf_links:
            if 'program' in link.lower():
                if link.startswith('http'):
                    return link
                return conference_url.rstrip('/') + '/' + link.lstrip('/')
    
    # Method 1b: Also check the detailed program page
    detail_url = conference_url.rstrip('/') + '/page/detailedprogram_page?lang=en'
    try:
        detail_html = fetch(detail_url).decode('utf-8', errors='replace')
        pdf_links = re.findall(r'href=["\']([^"\']*\.pdf)["\']', detail_html, re.IGNORECASE)
        if pdf_links:
            for link in pdf_links:
                if 'program' in link.lower() or 'programme' in link.lower():
                    if link.startswith('http'):
                        return link
                    return conference_url.rstrip('/') + '/' + link.lstrip('/')
    except:
        pass

    # Method 2: Try common SciencesConf PDF patterns
    base = conference_url.rstrip('/').replace('/?lang=en', '').replace('?lang=en', '')
    patterns = [
        "/data/pages/Programme_{name}_1.pdf",
        "/data/pages/Programme_{name}_2.pdf",
        "/data/pages/Programme_{name}_3.pdf",
        "/data/pages/Programme_{name}_4.pdf",
        "/data/pages/programme_{name}.pdf",
        "/data/pages/program_{name}.pdf",
    ]
    # Extract conference name from URL
    conf_name_match = re.search(r'https://([^.]+)\.sciencesconf', base)
    conf_name = conf_name_match.group(1) if conf_name_match else ""

    for pattern in patterns:
        url = base + pattern.format(name=conf_name.capitalize())
        try:
            resp = urllib.request.urlopen(urllib.request.Request(url, method='HEAD'))
            if resp.status == 200:
                return url
        except:
            pass

    return None


def normalize_data(sessions):
    """Apply institution name normalization."""
    for s in sessions:
        for p in s['papers']:
            p['institution_clean'] = clean_institution_name(p.get('institution', '') or '')
            # Apply safe merges
            if p['institution_clean'] in SAFE_MERGES:
                p['institution_clean'] = SAFE_MERGES[p['institution_clean']]

    # Build participant index
    participants = {}
    for s in sessions:
        for p in s['papers']:
            name = p.get('author', '').strip()
            if not name: continue
            if name not in participants:
                participants[name] = {
                    'name': name,
                    'institution_raw': p.get('institution', ''),
                    'institution_clean': p.get('institution_clean', ''),
                    'papers': [],
                    'is_presenter': True
                }
            participants[name]['papers'].append({
                'title': p.get('title', ''),
                'session': s['session_title']
            })

    for name, pdata in participants.items():
        insts = [pp['institution_clean'] for s in sessions
                 for pp in s['papers'] if pp.get('author') == name and pp.get('institution_clean')]
        if insts:
            pdata['institution_clean'] = Counter(insts).most_common(1)[0][0]

    return sessions, participants


# ── Main ────────────────────────────────────────────────────────
def scrape(conference_url, output_dir):
    """Main entry point: scrape a SciencesConf conference."""
    os.makedirs(output_dir, exist_ok=True)

    # Determine if URL is a PDF or a conference page
    is_pdf = conference_url.lower().endswith('.pdf')

    if is_pdf:
        print(f"📄 Téléchargement du PDF: {conference_url}")
        pdf_data = fetch(conference_url)
        pdf_path = os.path.join(output_dir, "program.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf_data)
        print(f"   Sauvegardé dans {pdf_path}")
    else:
        print(f"🔍 Recherche du programme sur {conference_url}...")
        pdf_url = find_pdf_url(conference_url)
        if pdf_url:
            print(f"📄 PDF trouvé: {pdf_url}")
            pdf_data = fetch(pdf_url)
            pdf_path = os.path.join(output_dir, "program.pdf")
            with open(pdf_path, 'wb') as f:
                f.write(pdf_data)
            print(f"   Téléchargé dans {pdf_path}")
        else:
            print("❌ Aucun PDF trouvé.")
            print("   Le programme est peut-être chargé dynamiquement en JavaScript.")
            print("   Essayez de fournir directement l'URL du PDF.")
            return None

    # Parse PDF
    print("🔎 Analyse du PDF...")
    sessions = parse_pdf(pdf_path)
    print(f"   {len(sessions)} sessions trouvées")

    # Normalize
    print("🧹 Normalisation des institutions...")
    sessions, participants = normalize_data(sessions)

    total_papers = sum(len(s['papers']) for s in sessions)
    output = {
        "conference": f"SciencesConf: {os.path.basename(conference_url.rstrip('/'))}",
        "source": conference_url,
        "total_papers": total_papers,
        "total_participants": len(participants),
        "sessions": sessions,
        "participants": sorted(participants.values(), key=lambda x: x['name'])
    }

    # Save
    with open(os.path.join(output_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Données sauvegardées dans {output_dir}/data.json")
    print(f"   {total_papers} papiers, {len(participants)} participants")

    # Show institutions ranking
    inst_counts = Counter()
    for s in sessions:
        for p in s['papers']:
            inst = p.get('institution_clean', '')
            if len(inst) > 5:
                inst_counts[inst] += 1

    print(f"\n🏛️  TOP 10 INSTITUTIONS :")
    for i, (inst, count) in enumerate(inst_counts.most_common(10), 1):
        print(f"  {i:2d}. {inst:55s} {count:2d}")

    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    url = sys.argv[1]
    conf_name = re.sub(r'[^a-zA-Z0-9]+', '-', os.path.basename(url.rstrip('/')).replace('.pdf', ''))
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser(f"~/economics-conferences/{conf_name}")

    scrape(url, outdir)
