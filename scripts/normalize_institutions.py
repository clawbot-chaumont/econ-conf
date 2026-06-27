#!/usr/bin/env python3
"""
Normalize all institution names in ALL_CONFERENCES_2026.csv using:
  1. Unicode normalization (diacritics, special chars)
  2. Abbreviation expansion (ECB → European Central Bank, etc.)
  3. Pattern-based cleaning (trailing punctuation, double spaces, country suffixes)
  4. Manual canonical mapping (curated from data)
  5. Fuzzy clustering with rapidfuzz for edge cases

Produces:
  - ALL_CONFERENCES_2026_CLEAN.csv  — full CSV with clean institution names
  - institution_mapping_report.txt  — log of all transformations applied
  - remaining_unsure.txt            — low-confidence clusters for manual review
"""

import csv
import os
import re
import sys
import unicodedata
from collections import Counter

# ── Paths ──────────────────────────────────────────────────────────────────
DATA_DIR   = os.path.expanduser("~/economics-conferences")
INPUT_CSV  = os.path.join(DATA_DIR, "ALL_CONFERENCES_2026.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "ALL_CONFERENCES_2026_CLEAN.csv")
REPORT_TXT = os.path.join(DATA_DIR, "institution_mapping_report.txt")
UNSURE_TXT = os.path.join(DATA_DIR, "remaining_unsure.txt")

# ── Phase 0: Unicode normalisation ─────────────────────────────────────────
def strip_diacritics(s):
    """é → e, ü → u, ñ → n, etc."""
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')

# ── Phase 1: Hard-coded abbreviation expansion ─────────────────────────────
ABBREVIATIONS = {
    # Central banks & international orgs
    r'\bECB\b':               'European Central Bank',
    r'\bBIS\b':               'Bank for International Settlements',
    r'\bIMF\b':               'International Monetary Fund',
    r'\bOECD\b':              'OECD',
    r'\bEBRD\b':              'European Bank for Reconstruction and Development',
    r'\bEIB\b':               'European Investment Bank',
    r'\bFRB\b':               'Federal Reserve Board',
    r'\bBundesbank\b':        'Deutsche Bundesbank',

    # US universities
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
    r'\bUSC\b\b':             'University of Southern California',

    # UK / Europe universities
    r'\bLSE\b':               'London School of Economics and Political Science',
    r'\bUCL\b':               'University College London',
    r'\bQMUL\b':              'Queen Mary University of London',
    r'\bKIT\b':               'Karlsruhe Institute of Technology',
    r'\bTUM\b':               'Technical University of Munich',
    r'\bNHH\b':               'NHH Norwegian School of Economics',
    r'\bNTU\b':               'Nanyang Technological University',
    r'\bNUS\b':               'National University of Singapore',

    # Research institutes
    r'\bCEMFI\b':             'CEMFI',
    r'\bCREST\b(?!\s+\()':    'CREST',
    r'\bCREI\b':              'Centre de Recerca en Economia Internacional',
    r'\bEIEF\b':              'Einaudi Institute for Economics and Finance',
    r'\bINSEAD\b':            'INSEAD',
    r'\bIAB\b':               'Institute for Employment Research (IAB)',
    r'\bIFN\b':               'Research Institute of Industrial Economics',
    r'\bIWH\b\b':             'Halle Institute for Economic Research (IWH)',
    r'\bWIFO\b':              'Austrian Institute of Economic Research',
    r'\bWZB\b':               'Berlin Social Science Center (WZB)',
    r'\bPSE\b':               'Paris School of Economics',
    r'\bZEW\b':               'ZEW - Leibniz Centre for European Economic Research',
    r'\bDIW\b':               'DIW Berlin',

    # Asia
    r'\bHKU\b':               'The University of Hong Kong',
    r'\bHKUST\b':             'Hong Kong University of Science and Technology',
    r'\bCUHK\b':              'The Chinese University of Hong Kong',
    r'\bITAM\b':              'Instituto Tecnológico Autónomo de México (ITAM)',

    # Canada
    r'\bUQAM\b':              'Université du Québec à Montréal',
    r'\bUBC\b':               'University of British Columbia',

    # Other
    r'\bCNA\b':               'CNA',
    r'\bVIVE\b':              'The Danish Center for Social Science Research (VIVE)',
    r'\bEPFL\b':              'École Polytechnique Fédérale de Lausanne',
    r'\bEUI\b':               'European University Institute',
    r'\bLUISS\b':             'LUISS University',
    r'\bPUC\b':               'Pontificia Universidad Católica de Chile',
}

# ── Phase 2: Pattern-based cleaning rules ──────────────────────────────────
PATTERN_RULES = [
    # Strip trailing punctuation (commas, periods, semicolons)
    (r'[,.;:\s]+$',          ''),
    # Strip leading/trailing whitespace + collapse multiple spaces
    (r'\s{2,}',               ' '),
    # Strip leading "The " for English universities (but keep for others)
    (r'^The\s+',              ''),
    # Unify en-dash/em-dash to hyphen
    (r'[–—]',                 '-'),
    # "University of X and NBER" → keep as is (meaningful)
    # Just clean country suffixes after dash: ", USA" after comma
    (r',\s*(USA|United States|U\.S\.A\.|Canada|France|Germany|Italy|Spain|UK|United Kingdom|China|Japan|Switzerland|Netherlands|Sweden|Denmark|Norway|Austria|Belgium|Finland|Ireland|Portugal|Australia|New Zealand|Singapore|Brazil|India|Chile|Mexico|Taiwan|Poland|Turkey|Greece|Russia|South Korea|Israel|Czech Republic|Hungary|Romania|Argentina|Colombia|Peru|South Africa|Thailand|Indonesia|Malaysia|Philippines|Vietnam|Egypt|Nigeria|Kenya|Morocco|Tunisia|Algeria|Pakistan|Bangladesh|Sri Lanka|Hong Kong|Macau)(?:\s*\([^)]*\))?\s*$', ''),
    # Remove trailing ".," or ". " artifacts
    (r'\.\s*,?\s*$',          ''),
    # Remove trailing space before closing paren
    (r'\s+\)',                ')'),
]

# ── Phase 3: Canonical mapping (hand-curated from data analysis) ───────────
# Key = raw input, Value = canonical form
CANONICAL_MAP = {
    # FRB variations
    'Board of Governors of the Federal Reserve System': 'Federal Reserve Board of Governors',
    'Board of Governors of the Federal Reserv':          'Federal Reserve Board of Governors',
    'Federal Reserve Board':                             'Federal Reserve Board of Governors',

    # Bank of Canada
    'Bank of Canada / Banque du Canada': 'Bank of Canada',

    # University Chicago
    'University of Chicago Booth School of':               'University of Chicago Booth School of Business',
    'Booth School of Business, University of Chicago':     'University of Chicago Booth School of Business',

    # The University of X → University of X
    'The University of Chicago':         'University of Chicago',
    'The University of Texas at Austin': 'University of Texas-Austin',
    'The Wharton School, University of Pennsylvania': 'Wharton School, University of Pennsylvania',
    'The Wharton School at University of Pennsylvania': 'Wharton School, University of Pennsylvania',
    'The Wharton School of the University of Pennsylvania': 'Wharton School, University of Pennsylvania',
    'University of Pennsylvania - The Wharton School': 'Wharton School, University of Pennsylvania',
    'The Wharton School, University of Pennsylvania and NBER': 'Wharton School, University of Pennsylvania and NBER',
    'Wharton School, University of Pennsylvania; NBER': 'Wharton School, University of Pennsylvania and NBER',

    # Names of themselves
    'Universidade de São Paulo': 'University of São Paulo',
    'Universidad de los Andes':  'Universidad de los Andes',
    'Universidad de Los Andes':  'Universidad de los Andes',

    # Paris Dauphine
    'Universite Paris Dauphine-PSL': 'Université Paris Dauphine-PSL',
    'Université Paris Dauphine':     'Université Paris Dauphine-PSL',
    'University Paris Dauphine-PSL': 'Université Paris Dauphine-PSL',
    'Paris Dauphine University':     'Université Paris Dauphine-PSL',
    'Paris Dauphine-PSL University': 'Université Paris Dauphine-PSL',
    'Universite Paris Dauphine - PSL': 'Université Paris Dauphine-PSL',

    # HSG / St. Gallen
    'University of St. Gallen': 'University of St. Gallen',
    'University of St. Gallen, Switzerland': 'University of St. Gallen',

    # Aix-Marseille
    'Aix-Marseille Universite': 'Aix-Marseille University',
    'Aix-Marseille University': 'Aix-Marseille University',

    # Various European
    'Pompeu Fabra University':     'Universitat Pompeu Fabra',
    'Warsaw School of Economics':  'SGH Warsaw School of Economics',
    'University of Maastricht':    'Maastricht University',
    'Universität Leipzig':         'Leipzig University',
    'University of Leipzig':       'Leipzig University',
    'Université d\'Orléans':       'Université d\'Orléans',
    'Universite D\'orleans':       'Université d\'Orléans',
    'Universite d\'Orleans':       'Université d\'Orléans',

    # University of California system
    'University of California, Davis and NBER': 'University of California, Davis and NBER',
    'University of California, Irvine and NBER': 'University of California, Irvine and NBER',

    # London School of Economics
    'London School of Economics and Political Science': 'London School of Economics and Political Science (LSE)',
    'London School of Economics':                       'London School of Economics and Political Science (LSE)',

    # Banque de France
    'banque de france': 'Banque de France',

    # Swiss Finance
    'Swiss Finance Institute - EPFL': 'Swiss Finance Institute',
    'Swiss Finance Institute': 'Swiss Finance Institute',

    # Center for Studies
    'Center For Monetary And Financial Studies (CEMFI)': 'CEMFI',
    'Center for Monetary and Financial Studies': 'CEMFI',

    # Banco central
    'banco do portugal': 'Banco de Portugal',

    # IESE / ESCP / HEC
    'IESE Business School; University of Navarra': 'IESE Business School',

    # BDF/CEPR
    'Bank of England and European Research University': 'Bank of England',
    # Canadian bank
    'Bank of Canada / Banque du Canada': 'Bank of Canada',

    # Hyphenation variants
    'Bar Ilan University': 'Bar-Ilan University',
    'Ben Gurion University': 'Ben-Gurion University',
    'Carnegie Mellon University': 'Carnegie Mellon University',
    'Carnegie-Mellon University': 'Carnegie Mellon University',
}


def expand_abbreviations(name):
    """Expand known abbreviations in-place, avoiding double-apply."""
    for pattern, replacement in ABBREVIATIONS.items():
        # Guard: don't expand if the full form is already present
        if replacement.lower() in name.lower():
            continue
        name = re.sub(pattern, replacement, name)
    return name


def apply_pattern_rules(name):
    """Apply deterministic cleaning patterns."""
    for pattern, replacement in PATTERN_RULES:
        name = re.sub(pattern, replacement, name)
    return name.strip()


def apply_canonical_map(name):
    """Manual curated overrides. Tries exact match first, then case-insensitive."""
    if name in CANONICAL_MAP:
        return CANONICAL_MAP[name]
    # Case-insensitive fallback
    for raw, canon in CANONICAL_MAP.items():
        if name.lower() == raw.lower():
            return canon
    return name


def normalize_name(name):
    """Full normalization pipeline."""
    if not name:
        return name
    original = name
    # Step 0: Strip diacritics for comparison, but keep originals when possible
    # Actually no — strip them entirely for clean output
    name = strip_diacritics(name)
    # Step 1: Expand abbreviations
    name = expand_abbreviations(name)
    # Step 2: Apply pattern rules
    name = apply_pattern_rules(name)
    # Step 3: Apply canonical map
    name = apply_canonical_map(name)
    # Step 4: Deduplicate consecutive repeated words (e.g. "DIW Berlin Berlin" → "DIW Berlin")
    parts = name.split()
    deduped = []
    for p in parts:
        if not deduped or p.lower() != deduped[-1].lower():
            deduped.append(p)
    name = ' '.join(deduped)
    # Step 5: Final trim
    name = name.strip()
    return name


# ── Fuzzy clustering (high confidence only) ─────────────────────────────────
def fuzzy_cluster(remaining_unique, threshold=90):
    """
    For names that didn't match any rule, use rapidfuzz to group likely duplicates.
    Returns: list of (canonical, [(variant, count), ...]) groups
    """
    from rapidfuzz import fuzz

    keys = sorted(remaining_unique.keys())
    matched = set()
    clusters = []

    for k in keys:
        if k in matched:
            continue
        group = [k]
        matched.add(k)
        for other in keys:
            if other in matched:
                continue
            # token_sort_ratio handles word reordering well
            if fuzz.token_sort_ratio(k, other) >= threshold:
                group.append(other)
                matched.add(other)
        if len(group) > 1:
            # Pick the most common variant as canonical
            best = max(group, key=lambda x: remaining_unique[x])
            variants = [(v, remaining_unique[v]) for v in group if v != best]
            clusters.append((best, remaining_unique[best], variants))
    return clusters


# ── Main ──────────────────────────────────────────────────────────────────
def main():
    try:
        from rapidfuzz import fuzz
        has_rapidfuzz = True
    except ImportError:
        has_rapidfuzz = False
        print("⚠️  rapidfuzz not installed — fuzzy clustering skipped")
        print("   Install: pip install rapidfuzz")

    # Read CSV
    rows = []
    with open(INPUT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"Read {len(rows)} rows, {len(fieldnames)} columns")

    # Track changes
    changes = Counter()
    mapping_log = {}  # raw → clean

    # Process each row
    for row in rows:
        raw = row.get('participant_institution', '').strip()
        if not raw:
            continue
        clean = normalize_name(raw)
        if clean != raw:
            changes['changed'] += 1
            mapping_log[raw] = clean
        row['participant_institution'] = clean

    # Collect remaining unique names for fuzzy clustering
    remaining = Counter()
    for row in rows:
        inst = row.get('participant_institution', '')
        if inst:
            remaining[inst] += 1

    changes['unique_before'] = sum(1 for r in rows if r.get('participant_institution',''))
    changes['unique_after']  = len(remaining)

    # Fuzzy clustering on what's left
    auto_merged = []
    for_review = []

    if has_rapidfuzz and len(remaining) > 1:
        auto_clusters = fuzzy_cluster(remaining, threshold=92)
        for best, best_count, variants in auto_clusters:
            auto_merged.append((best, best_count, variants))
            changes['auto_clusters'] += 1
            for var, cnt in variants:
                changes['auto_merged'] += cnt
                mapping_log[var] = best

        # Apply auto-merges to rows
        fuzzy_map = {}
        for best, best_count, variants in auto_clusters:
            for var, cnt in variants:
                fuzzy_map[var] = best
        for row in rows:
            inst = row.get('participant_institution', '')
            if inst in fuzzy_map:
                row['participant_institution'] = fuzzy_map[inst]

        # Re-collect after auto-merges for review
        remaining_after = Counter()
        for row in rows:
            inst = row.get('participant_institution', '')
            if inst:
                remaining_after[inst] += 1

        # Review clusters (borderline: 80-91)
        review_clusters = fuzzy_cluster(remaining_after, threshold=80)
        # Filter to only those below auto threshold
        for best, best_count, variants in review_clusters:
            # Verify these are NOT in auto cluster range
            true_variants = []
            for var, cnt in variants:
                from rapidfuzz import fuzz
                score = fuzz.token_sort_ratio(best, var)
                if score < 92:  # Below auto-threshold
                    true_variants.append((var, cnt))
            if true_variants:
                for_review.append((best, best_count, true_variants))
                changes['review_clusters'] += 1

    # Write clean CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Write mapping report
    with open(REPORT_TXT, 'w', encoding='utf-8') as f:
        f.write("INSTITUTION NORMALIZATION REPORT\n")
        f.write("=" * 70)
        f.write(f"\n\nTotal rows processed: {len(rows)}")
        f.write(f"\nUnique names before: {changes.get('unique_before', 0)}")
        f.write(f"\nUnique names after:  {changes.get('unique_after', 0)}")
        f.write(f"\nNames changed:       {changes.get('changed', 0)}")
        f.write(f"\nAuto-merged clusters: {changes.get('auto_clusters', 0)}")
        f.write(f"\nRows auto-merged:     {changes.get('auto_merged', 0)}")
        f.write(f"\nReview clusters:       {changes.get('review_clusters', 0)}")
        f.write(f"\n")
        f.write("\n\n── TRANSFORMATIONS (rule-based) ──\n\n")
        for raw, clean in sorted(mapping_log.items()):
            if clean != raw:
                f.write(f"  {raw:80s} → {clean}\n")

    # Write review clusters (borderline cases, not auto-merged)
    if for_review:
        with open(UNSURE_TXT, 'w', encoding='utf-8') as f:
            f.write("BORDERLINE FUZZY CLUSTERS — review manually!\n")
            f.write("=" * 70)
            f.write("\n\n")
            for best, best_count, variants in for_review:
                f.write(f"\n✓ CANONICAL:  {best}  ({best_count}x)\n")
                for var, cnt in sorted(variants, key=lambda x: -x[1]):
                    f.write(f"  ? {var:70s} ({cnt}x)\n")
                f.write("\n")

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Clean CSV:   {OUTPUT_CSV}")
    print(f"📄 Report:      {REPORT_TXT}")
    if for_review:
        print(f"⚠️  Review:      {UNSURE_TXT} ({len(for_review)} clusters to review)")
        print()
        print("Top review clusters:")
        for best, best_count, variants in for_review[:10]:
            var_str = ", ".join(f"'{v}' ({c}x)" for v, c in variants[:3])
            print(f"  → {best} ({best_count}x)")
            print(f"    variants: {var_str}")
    else:
        print(f"\nNo low-confidence clusters found.")
    print()
    print(f"Unique names (rows with inst): {changes.get('unique_before', 0)} → {len(remaining)} (after rules)")
    print(f"Auto-merged:  {changes.get('auto_clusters', 0)} clusters ({changes.get('auto_merged', 0)} rows)")
    print(f"For review:   {changes.get('review_clusters', 0)} clusters")


if __name__ == '__main__':
    main()
