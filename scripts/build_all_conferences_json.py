#!/usr/bin/env python3
"""
Build ALL_CONFERENCES_2026.json — one entry per (name × conference).

Each entry has institutions as an array, handling:
  - "X and NBER" → ["X", "NBER"]
  - "X; Y; Z" → ["X", "Y", "Z"]
  - Federal Reserve Board of Governors / System → "Federal Reserve Bank"
  - All abbreviation expansion + normalization from normalize_institutions.py
"""

import csv
import json
import os
import re
import unicodedata

# ── Paths ──────────────────────────────────────────────────────────────────
DATA_DIR   = os.path.expanduser("~/economics-conferences")
INPUT_CSV  = os.path.join(DATA_DIR, "ALL_CONFERENCES_2026.csv")
OUTPUT_JSON = os.path.join(DATA_DIR, "ALL_CONFERENCES_2026.json")

# ── Unicode ────────────────────────────────────────────────────────────────
def strip_diacritics(s):
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')

# ── Abbreviation expansion ────────────────────────────────────────────────
ABBREVIATIONS = {
    r'\bECB\b':               'European Central Bank',
    r'\bBIS\b':               'Bank for International Settlements',
    r'\bIMF\b':               'International Monetary Fund',
    r'\bOECD\b':              'OECD',
    r'\bEBRD\b':              'European Bank for Reconstruction and Development',
    r'\bEIB\b':               'European Investment Bank',
    r'\bFRB\b':               'Federal Reserve Bank',
    r'\bBundesbank\b':        'Deutsche Bundesbank',
    r'\bMIT\b':               'Massachusetts Institute of Technology',
    r'\bNYU\b':               'New York University',
    r'\bUCLA\b':              'University of California, Los Angeles',
    r'\bUCSD\b':              'University of California, San Diego',
    r'\bUIUC\b':              'University of Illinois Urbana-Champaign',
    r'\bUNC\b':               'University of North Carolina',
    r'\bLSU\b':               'Louisiana State University',
    r'\bMSU\b':               'Michigan State University',
    r'\bASU\b':               'Arizona State University',
    r'\bHBS\b':               'Harvard Business School',
    r'\bCUNY\b':              'City University of New York',
    r'\bLSE\b':               'London School of Economics and Political Science (LSE)',
    r'\bUCL\b':               'University College London',
    r'\bQMUL\b':              'Queen Mary University of London',
    r'\bKIT\b':               'Karlsruhe Institute of Technology',
    r'\bTUM\b':               'Technical University of Munich',
    r'\bNHH\b':               'NHH Norwegian School of Economics',
    r'\bNTU\b':               'Nanyang Technological University',
    r'\bNUS\b':               'National University of Singapore',
    r'\bCEMFI\b':             'CEMFI',
    r'\bCREST\b(?!\s+\()':    'CREST',
    r'\bCREI\b':              'Centre de Recerca en Economia Internacional',
    r'\bEIEF\b':              'Einaudi Institute for Economics and Finance',
    r'\bINSEAD\b':            'INSEAD',
    r'\bIAB\b':               'Institute for Employment Research (IAB)',
    r'\bIFN\b':              'Research Institute of Industrial Economics',
    r'\bPSE\b':               'Paris School of Economics',
    r'\bZEW\b':               'ZEW - Leibniz Centre for European Economic Research',
    r'\bDIW\b':               'DIW Berlin',
    r'\bHKU\b':               'The University of Hong Kong',
    r'\bHKUST\b':             'Hong Kong University of Science and Technology',
    r'\bCUHK\b':              'The Chinese University of Hong Kong',
    r'\bITAM\b':              'Instituto Tecnologico Autonomo de Mexico (ITAM)',
    r'\bUQAM\b':              'Universite du Quebec a Montreal',
    r'\bUBC\b':               'University of British Columbia',
    r'\bVIVE\b':              'The Danish Center for Social Science Research (VIVE)',
    r'\bEPFL\b':              'Ecole Polytechnique Federale de Lausanne',
    r'\bEUI\b':               'European University Institute',
    r'\bLUISS\b':             'LUISS University',
    r'\bPUC\b':               'Pontificia Universidad Catolica de Chile',
}

# ── Pattern cleaning ──────────────────────────────────────────────────────
PATTERN_RULES = [
    (r'[,.;:\s]+$',              ''),
    (r'\s{2,}',                   ' '),
    (r'^The\s+',                  ''),
    (r'[–—]',                     '-'),
    (r'\.\s*,?\s*$',              ''),
    (r'\s+\)',                    ')'),
]

# ── Canonical institution names ────────────────────────────────────────────
CANONICAL_MAP = {
    # Fed: Board / System → just "Federal Reserve Bank"
    'Board of Governors of the Federal Reserve System':  'Federal Reserve Bank',
    'Board of Governors of the Federal Reserv':           'Federal Reserve Bank',
    'Federal Reserve Board':                              'Federal Reserve Bank',
    'Federal Reserve Board of Governors':                 'Federal Reserve Bank',
    'Federal Reserve Board, USA':                          'Federal Reserve Bank',
    'Federal Reserve Board of Governors, USA':             'Federal Reserve Bank',
    'Federal Reserve System':                             'Federal Reserve Bank',
    'federal reserve bank of saint louis':                'Federal Reserve Bank of St. Louis',
    'Federal reserve Bank of Philadelphia':               'Federal Reserve Bank of Philadelphia',
    'Federal Reserve Bank of Saint Louis':                'Federal Reserve Bank of St. Louis',
    'Federal Reserve Bank of Minneapolis and NBER':       'Federal Reserve Bank of Minneapolis',
    'Federal Reserve New York':                           'Federal Reserve Bank of New York',

    # Bank of Canada
    'Bank of Canada / Banque du Canada': 'Bank of Canada',

    # Chicago
    'University of Chicago Booth School of':                 'University of Chicago Booth School of Business',
    'Booth School of Business, University of Chicago':       'University of Chicago Booth School of Business',

    # Wharton
    'The Wharton School, University of Pennsylvania':         'Wharton School, University of Pennsylvania',
    'The Wharton School at University of Pennsylvania':       'Wharton School, University of Pennsylvania',
    'The Wharton School of the University of Pennsylvania':   'Wharton School, University of Pennsylvania',
    'University of Pennsylvania - The Wharton School':        'Wharton School, University of Pennsylvania',
    'Wharton School, University of Pennsylvania; NBER':       'Wharton School, University of Pennsylvania',

    # Paris Dauphine
    'Universite Paris Dauphine-PSL':     'Universite Paris Dauphine-PSL',
    'Universite Paris Dauphine - PSL':   'Universite Paris Dauphine-PSL',
    'Universite Paris Dauphine':         'Universite Paris Dauphine-PSL',
    'University Paris Dauphine-PSL':     'Universite Paris Dauphine-PSL',
    'Paris Dauphine University':         'Universite Paris Dauphine-PSL',
    'Paris Dauphine-PSL University':     'Universite Paris Dauphine-PSL',
    'Paris Dauphine - Psl':              'Universite Paris Dauphine-PSL',
    'Paris Dauphine PSL':                'Universite Paris Dauphine-PSL',
    'Dauphine-PSL':                      'Universite Paris Dauphine-PSL',
    'Universite Paris Dauphine - PSL, DRM- Finance': 'Universite Paris Dauphine-PSL',
    'Laboratoire d\'Economie de Dauphine, Chaire Economie du Climat': 'Universite Paris Dauphine-PSL',
    'university paris-dauphine-PSL':     'Universite Paris Dauphine-PSL',

    # Paris-Saclay
    'Universite Paris-Saclay':           'Universite Paris-Saclay',
    'University Paris-Saclay':           'Universite Paris-Saclay',
    'Universite Evry Paris-Saclay':      'Universite Paris-Saclay',
    'University of Evry Paris-Saclay':   'Universite Paris-Saclay',
    'ENS Paris-Saclay':                  'Universite Paris-Saclay',
    'CentraleSupelec/Universite Paris-Saclay': 'Universite Paris-Saclay',
    'University Evry Paris-':            'Universite Paris-Saclay',
    'University Paris-Est':              'Universite Paris-Est Creteil',
    'Universite Paris-Est Creteil':      'Universite Paris-Est Creteil',

    # Paris 1 Pantheon-Sorbonne
    'Universite Paris 1 Pantheon-Sorbonne':                                 'Universite Paris 1 Pantheon-Sorbonne',
    'Universite Paris 1 - Pantheon Sorbonne':                               'Universite Paris 1 Pantheon-Sorbonne',
    'Universite Paris 1 Pantheon Sorbonne':                                 'Universite Paris 1 Pantheon-Sorbonne',
    'Paris 1 Pantheon-Sorbonne':                                            'Universite Paris 1 Pantheon-Sorbonne',
    'Paris 1, Pantheon-Sorbonne':                                           'Universite Paris 1 Pantheon-Sorbonne',
    'CES - Universite Paris 1 Pantheon-Sorbonne':                           'Universite Paris 1 Pantheon-Sorbonne',
    'Universite Paris 1 Pantheon-Sorbonne - Ecole d\'economie de la Sorbonne': 'Universite Paris 1 Pantheon-Sorbonne',
    'Sorbonne Economics Center (Pantheon-Sorbonne Paris 1 University)':     'Universite Paris 1 Pantheon-Sorbonne',
    "Centre d'Economie de la Sorbonne":                                     'Universite Paris 1 Pantheon-Sorbonne',
    "Centre d'economie de la Sorbonne":                                     'Universite Paris 1 Pantheon-Sorbonne',
    "Centre d'economie de la Sorbonne, Paris-Jourdan Sciences Economiques, Universite Paris 1, Pantheon-Sorbonne, Centre interuniversitaire de recherche en analyse des organisations": 'Universite Paris 1 Pantheon-Sorbonne',
    'IAE Paris - Sorbonne Business School':                                 'Universite Paris 1 Pantheon-Sorbonne',
    'IAE Paris - Sorbonne Business School, France':                        'Universite Paris 1 Pantheon-Sorbonne',

    # Paris-Pantheon-Assas
    'Universite Paris-Pantheon-Assas':     'Universite Paris-Pantheon-Assas',
    'Universite Paris Pantheon-Assas':     'Universite Paris-Pantheon-Assas',

    # Paris Nanterre
    'Universite Paris Nanterre':                      'Universite Paris Nanterre',
    'Universite Paris Nanterre - EconomiX':           'Universite Paris Nanterre',
    'Climate Economics Chair, Universite Paris Nanterre, EDF Recherche et Developpement': 'Universite Paris Nanterre',

    # Paris School of Economics
    'Paris School of Economics/INSEE':              'Paris School of Economics',
    'Paris School of Economics-CNRS':               'Paris School of Economics',
    'Paris School of Economics / Banque de France': 'Paris School of Economics',
    'Paris School of Economics, College de France': 'Paris School of Economics',
    'PSE, College de France':                       'Paris School of Economics',
    'Paris School of  Economics':                   'Paris School of Economics',
    'Professor of Economics at the Paris School of Economics, EHESS': 'Paris School of Economics',

    # HEC Paris
    'HEC - Paris':                   'HEC Paris',
    'HEC School of Management':      'HEC Paris',

    # HEC Montreal
    'HEC - Montréal':                'HEC Montreal',
    'HEC - MontrA©al':              'HEC Montreal',
    'HEC montreal':                  'HEC Montreal',
    'HEC Montreal, Canada CMSG: Macroeconomic Policy / Politique macroeconomique': 'HEC Montreal',
    'HEC Montreal, Canada Urban, Regional, and Spatial Economics: Media, Attention, and Digital Technology': 'HEC Montreal',

    # HEC Lausanne
    'HEC - Lausanne':                'HEC Lausanne',
    'HEC- University of Lausanne':   'HEC Lausanne',

    # EDHEC
    'Edhec Business School':         'EDHEC Business School',
    'EDHEC':                         'EDHEC Business School',
    'Scientific Portfolio an EDHEC venture': 'EDHEC Business School',

    # Sorbonne straggler
    'Sorbonne Economics Center (Pantheon-Sorbonne Paris 1 University), France CFEN: Asset Pricing II': 'Universite Paris 1 Pantheon-Sorbonne',

    # CY Cergy
    'CY Cergy Paris Universite - Thema':         'CY Cergy Paris Universite',
    'CY Cergy Paris University THEMA (France)':  'CY Cergy Paris Universite',
    'Cergy Paris Universite':                    'CY Cergy Paris Universite',

    # ENSAE = CREST - IP Paris
    'Ensae':                            'CREST - IP Paris',
    'ENSAE':                            'CREST - IP Paris',

    # Other French
    'Sciences Po, Paris':                         'Sciences Po',
    'CREST - Institut Polytechnique de Paris':    'CREST - IP Paris',
    'BNP Parisbas':                               'BNP Paribas',

    # St. Gallen
    'University of St. Gallen, Switzerland': 'University of St. Gallen',

    # Aix-Marseille
    'Aix-Marseille Universite': 'Aix-Marseille University',

    # European
    'Pompeu Fabra University':      'Universitat Pompeu Fabra',
    'Warsaw School of Economics':   'SGH Warsaw School of Economics',
    'University of Maastricht':     'Maastricht University',
    'Universitat Leipzig':          'Leipzig University',
    'University of Leipzig':        'Leipzig University',
    "Universite d'Orleans":         "Universite d'Orleans",
    "Universite D'orleans":         "Universite d'Orleans",
    "Universite d'Orleans":         "Universite d'Orleans",

    # LSE
    'London School of Economics and Political Science': 'London School of Economics and Political Science (LSE)',
    'London School of Economics':                       'London School of Economics and Political Science (LSE)',

    # Swiss Finance
    'Swiss Finance Institute - EPFL': 'Swiss Finance Institute',

    # CEMFI
    'Center For Monetary And Financial Studies (CEMFI)': 'CEMFI',
    'Center for Monetary and Financial Studies':          'CEMFI',

    # Hyphenation
    'Bar Ilan University':             'Bar-Ilan University',
    'Ben Gurion University':           'Ben-Gurion University',
    'Carnegie-Mellon University':      'Carnegie Mellon University',

    # Orphan case
    'banque de france':        'Banque de France',
    'banco do portugal':       'Banco de Portugal',
    'IESE Business School; University of Navarra': 'IESE Business School',

    # Names with common typos
    'Simon Fraser Univeristy, Canada': 'Simon Fraser University',
    'Saint Mary\'s Universtiy, Canada': 'Saint Mary\'s University, Canada',
    'University of Amstedam':          'University of Amsterdam',
    'Massachusetts Institute of Techonology': 'Massachusetts Institute of Technology',
    'Deustche Bundesbank':              'Deutsche Bundesbank',
    'Deutsche Budesbank':              'Deutsche Bundesbank',
    'Univeristy College Dublin':        'University College Dublin',
    'University College ublin':        'University College Dublin',
    'Universita Bocconi':              'Bocconi University',
    'John Hopkins University':         'Johns Hopkins University',
    'Univerity of Oxford':             'University of Oxford',
    'Tel Aviv Univesity':              'Tel Aviv University',
    'Darmouth College and NBER':       'Dartmouth College and NBER',
    'ifo Insitute':                    'ifo Institute',
    'Binghampton University':          'Binghamton University',
    'Institute for Employment Reserach': 'Institute for Employment Research (IAB)',
    'CUNY-Graduate Center':             'City University of New York Graduate Center',
    'CUNY Graduate Center':             'City University of New York Graduate Center',
    'The Graduate Center, CUNY':        'City University of New York Graduate Center',
}


def expand_abbreviations(name):
    for pattern, replacement in ABBREVIATIONS.items():
        if replacement.lower() in name.lower():
            continue
        name = re.sub(pattern, replacement, name)
    return name

def apply_pattern_rules(name):
    for pattern, replacement in PATTERN_RULES:
        name = re.sub(pattern, replacement, name)
    return name.strip()

def apply_canonical_map(name):
    if name in CANONICAL_MAP:
        return CANONICAL_MAP[name]
    for raw, canon in CANONICAL_MAP.items():
        if name.lower() == raw.lower():
            return canon
    return name


def normalize_institution(name):
    """Normalize a single institution name (after splitting)."""
    if not name:
        return name
    name = strip_diacritics(name)
    name = expand_abbreviations(name)
    name = apply_pattern_rules(name)
    # Remove trailing country suffix before canonical mapping
    name = re.sub(r',\s*(USA|United States|Canada|France|Germany|Italy|Spain|UK|United Kingdom|China|Japan|Switzerland|Netherlands|Sweden|Denmark|Norway|Austria|Belgium|Finland|Ireland|Portugal|Australia|New Zealand|Singapore|Brazil|India|Chile|Mexico|Taiwan|Poland|Turkey|Greece|Russia|South Korea|Israel|Czech Republic|Hungary|Romania|Argentina|Colombia|Peru|South Africa|Thailand|Indonesia|Malaysia|Philippines|Vietnam|Egypt|Nigeria|Kenya|Morocco|Tunisia|Algeria|Pakistan|Bangladesh|Sri Lanka|Hong Kong|Macau)\s*$', '', name)
    name = apply_canonical_map(name)
    # Deduplicate consecutive words
    parts = name.split()
    deduped = []
    for p in parts:
        if not deduped or p.lower() != deduped[-1].lower():
            deduped.append(p)
    name = ' '.join(deduped)
    # Final trim
    return name.strip()


def split_affiliations(raw_inst):
    """
    Split a raw institution string into an array of normalized institutions.
    
    Handles:
    - Semicolon-separated: "MIT; NBER" → ["MIT", "NBER"]
    - "X and NBER" → ["X", "NBER"]
    - Multi-and: "X and Y and NBER" → tricky, only split "and NBER" suffix
    - Single: "Stanford University" → ["Stanford University"]
    """
    if not raw_inst:
        return []

    # Step 1: Split on semicolons first
    parts = re.split(r'\s*;\s*', raw_inst)
    
    # Step 2: For each part, split "and NBER" → [base, "NBER"]
    expanded = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Check if ends with " and NBER" (case-insensitive)
        m = re.search(r'\s+and\s+NBER\s*$', part, re.IGNORECASE)
        if m:
            base = part[:m.start()].strip()
            expanded.append(base)
            expanded.append('NBER')
        else:
            expanded.append(part)
    
    # Step 3: Split on " & " (only with spaces, to avoid "A&M" false positive)
    final = []
    for e in expanded:
        sub = re.split(r'\s+&\s+', e)
        final.extend(s.strip() for s in sub if s.strip())
    
    # Step 4: Normalize each institution
    normalized = []
    for inst in final:
        n = normalize_institution(inst)
        if n and n not in normalized:  # deduplicate within entry
            normalized.append(n)
    
    return normalized if normalized else []


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    entries = {}  # {conf_short: {name: {institutions, papers, sessions}}}
    stats = {'total_rows': 0, 'entries': 0, 'multi_inst': 0, 'with_nber': 0}

    with open(INPUT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats['total_rows'] += 1
            name = row.get('participant_name', '').strip()
            conf_short = row.get('conference_short_name', '').strip()
            conf_name = row.get('conference_name', '').strip()
            year = row.get('conference_year', 2026)
            raw_inst = row.get('participant_institution', '').strip()
            papers = row.get('participant_papers', '').strip()
            sessions = row.get('participant_session_titles', '').strip()

            if not name or not conf_short:
                continue

            institutions = split_affiliations(raw_inst)
            if len(institutions) > 1:
                stats['multi_inst'] += 1
            if 'NBER' in institutions:
                stats['with_nber'] += 1

            # Initialize conference entry if needed
            if conf_short not in entries:
                entries[conf_short] = {
                    'conference_name': conf_name,
                    'year': int(year) if year else 2026,
                    'participants': {}
                }
            
            conf = entries[conf_short]
            
            # Initialize participant if needed
            if name not in conf['participants']:
                conf['participants'][name] = {
                    'institutions': [],
                    'papers': [],
                    'sessions': [],
                }
                stats['entries'] += 1
            
            pdata = conf['participants'][name]
            
            # Merge institutions (union, order-preserving)
            for inst in institutions:
                if inst not in pdata['institutions']:
                    pdata['institutions'].append(inst)

            # Merge papers
            if papers:
                for p in re.split(r'\s*;\s*', papers):
                    p = p.strip()
                    if p and p not in pdata['papers']:
                        pdata['papers'].append(p)

            # Merge sessions
            if sessions:
                for s in re.split(r'\s*;\s*', sessions):
                    s = s.strip()
                    if s and s not in pdata['sessions']:
                        pdata['sessions'].append(s)

    # Write JSON — grouped by conference
    # Reorganize: participants dict → sorted list
    output = {}
    for conf_short, conf_data in sorted(entries.items()):
        participants_list = [
            {"name": name, **data}
            for name, data in sorted(conf_data['participants'].items())
        ]
        output[conf_short] = {
            "conference_name": conf_data['conference_name'],
            "year": conf_data['year'],
            "participants": participants_list,
        }

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Stats
    conf_count = len(output)
    part_count = sum(len(c['participants']) for c in output.values())
    print(f"✅ JSON: {OUTPUT_JSON}")
    print(f"   Conferences:  {conf_count:>6,}")
    print(f"   Participants: {part_count:>6,}")
    print(f"   Multi-affiliations:   {stats['multi_inst']:>6,}")
    print(f"   With NBER:            {stats['with_nber']:>6,}")

    # Show sample
    print(f"\nSample — first conference:")
    first_conf = list(output.keys())[0]
    conf_data = output[first_conf]
    print(f"  {first_conf}: {conf_data['conference_name']} ({conf_data['year']})")
    for p in conf_data['participants'][:3]:
        print(f"    • {p['name']:35s} → {p['institutions']}")


if __name__ == '__main__':
    main()
