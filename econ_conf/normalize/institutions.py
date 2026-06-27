"""
Institution name normalization pipeline.

Usage:
    from econ_conf.normalize.institutions import normalize_institution, split_affiliations

    normalized = normalize_institution("Federal Reserve Board, USA")
    # → "Federal Reserve Bank"

    affiliations = split_affiliations("Harvard University and NBER")
    # → ["Harvard University", "NBER"]
"""

import re
import unicodedata

from .abbreviations import ABBREVIATIONS
from .canonical_map import CANONICAL_MAP


# ── Pattern cleaning rules ──────────────────────────────────────────────────
PATTERN_RULES = [
    (r'[,.;:\s]+$',              ''),    # trailing punctuation/whitespace
    (r'\s{2,}',                   ' '),   # collapse multiple spaces
    (r'^The\s+',                  ''),    # leading "The "
    (r'[–—]',                     '-'),   # unify dashes
    (r'\.\s*,?\s*$',              ''),    # trailing dot artifacts
    (r'\s+\)',                    ')'),   # space before closing paren
]

# Country suffixes to strip before canonical mapping
COUNTRY_PATTERN = r',\s*(USA|United States|Canada|France|Germany|Italy|Spain|UK|United Kingdom|China|Japan|Switzerland|Netherlands|Sweden|Denmark|Norway|Austria|Belgium|Finland|Ireland|Portugal|Australia|New Zealand|Singapore|Brazil|India|Chile|Mexico|Taiwan|Poland|Turkey|Greece|Russia|South Korea|Israel|Czech Republic|Hungary|Romania|Argentina|Colombia|Peru|South Africa|Thailand|Indonesia|Malaysia|Philippines|Vietnam|Egypt|Nigeria|Kenya|Morocco|Tunisia|Algeria|Pakistan|Bangladesh|Sri Lanka|Hong Kong|Macau)\s*$'


def strip_diacritics(s: str) -> str:
    """é → e,  ü → u,  ñ → n, etc."""
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')


def expand_abbreviations(name: str) -> str:
    """Expand known short forms, avoiding double-expansion."""
    for pattern, replacement in ABBREVIATIONS.items():
        if replacement.lower() in name.lower():
            continue
        name = re.sub(pattern, replacement, name)
    return name


def apply_pattern_rules(name: str) -> str:
    """Apply deterministic cleaning patterns."""
    for pattern, replacement in PATTERN_RULES:
        name = re.sub(pattern, replacement, name)
    return name.strip()


def apply_canonical_map(name: str) -> str:
    """Apply manual curated overrides. Exact match first, then case-insensitive."""
    if name in CANONICAL_MAP:
        return CANONICAL_MAP[name]
    for raw, canon in CANONICAL_MAP.items():
        if name.lower() == raw.lower():
            return canon
    return name


def normalize_institution(name: str) -> str:
    """
    Full normalization pipeline for a single institution name.

    Steps:
    1. Strip diacritics
    2. Expand abbreviations (ECB → European Central Bank, etc.)
    3. Apply pattern rules (trailing punctuation, dashes, spacing)
    4. Strip trailing country suffix
    5. Apply canonical map (manual overrides)
    6. Deduplicate consecutive repeated words
    """
    if not name:
        return name

    name = strip_diacritics(name)
    name = expand_abbreviations(name)
    name = apply_pattern_rules(name)

    # Strip trailing country before canonical map (so Fed Board, USA → Fed Board → Fed Bank)
    name = re.sub(COUNTRY_PATTERN, '', name)

    name = apply_canonical_map(name)

    # Deduplicate consecutive repeated words ("DIW Berlin Berlin" → "DIW Berlin")
    parts = name.split()
    deduped = []
    for p in parts:
        if not deduped or p.lower() != deduped[-1].lower():
            deduped.append(p)
    name = ' '.join(deduped)

    return name.strip()


def split_affiliations(raw_inst: str) -> list:
    """
    Split a raw institution string into an array of normalized institutions.

    Handles:
    - Semicolon-separated:  "MIT; NBER" → ["MIT", "NBER"]
    - "X and NBER" suffix:  "Harvard University and NBER" → ["Harvard University", "NBER"]
    - " & " separator:      "IESE & Wharton" → ["IESE", "Wharton"]
    - Single:               "Stanford University" → ["Stanford University"]
    """
    if not raw_inst:
        return []

    # Step 1: Split on semicolons
    parts = re.split(r'\s*;\s*', raw_inst)

    # Step 2: For each part, split "and NBER" suffix → [base, "NBER"]
    expanded = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.search(r'\s+and\s+NBER\s*$', part, re.IGNORECASE)
        if m:
            base = part[:m.start()].strip()
            expanded.append(base)
            expanded.append('NBER')
        else:
            expanded.append(part)

    # Step 3: Split on " & " (with spaces, to avoid "A&M" false positive)
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
