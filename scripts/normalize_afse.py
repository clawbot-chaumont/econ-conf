#!/usr/bin/env python3
"""
Normalize AFSE 2026 data using the same pipeline as EFA.
Imports clean_institution_name and SAFE_MERGES from conftool_scraper.py
"""
import json, sys, os, re

# Import the normalization functions from the EFA scraper
sys.path.insert(0, os.path.expanduser("~/economics-conferences"))
from conftool_scraper import clean_institution_name, SAFE_MERGES, deduplicate_institutions

with open(os.path.expanduser("~/economics-conferences/afse2026/data.json")) as f:
    data = json.load(f)

print(f"Chargé : {data['total_papers']} papiers, {data['total_participants']} participants")
print(f"  Sessions: {len(data['sessions'])}")
print()

# Count unique institutions before
raw_insts = set()
for s in data['sessions']:
    for p in s['papers']:
        raw_insts.add(p['institution'])
print(f"🏛️  Institutions uniques (brutes) : {len(raw_insts)}")

# 1. Apply clean_institution_name to each paper's institution
for s in data['sessions']:
    for p in s['papers']:
        p['institution_clean'] = clean_institution_name(p['institution'])

# 2. Apply SAFE_MERGES deduplication
for s in data['sessions']:
    for p in s['papers']:
        inst = p['institution_clean']
        if inst in SAFE_MERGES:
            p['institution_clean'] = SAFE_MERGES[inst]

# Also apply SAFE_MERGES to multi-institution strings
for s in data['sessions']:
    for p in s['papers']:
        parts = p['institution_clean'].split('; ')
        new_parts = []
        for part in parts:
            part = part.strip()
            if part in SAFE_MERGES:
                part = SAFE_MERGES[part]
            if part and part not in new_parts:
                new_parts.append(part)
        p['institution_clean'] = '; '.join(new_parts)

# 4. AFSE-specific safe merges (after general SAFE_MERGES)
AFSE_SAFE_MERGES = {
    # Paris universities
    'Universite Paris 1': 'Universite Paris 1 Pantheon-Sorbonne',
    'Universite Paris 1 Pantheon': 'Universite Paris 1 Pantheon-Sorbonne',
    'Universite Paris 1 Pantheon-': 'Universite Paris 1 Pantheon-Sorbonne',
    'Pantheon-Sorbonne': 'Universite Paris 1 Pantheon-Sorbonne',
    'Universite Paris-pantheon-assas': 'Universite Paris-Pantheon-Assas',
    'Universite Paris-Pantheon-Assas': 'Universite Paris-Pantheon-Assas',
    'Universite Paris Dauphine': 'Universite Paris Dauphine-PSL',
    'Universite Paris Dauphine-Psl': 'Universite Paris Dauphine-PSL',
    'University Paris-dauphine-': 'Universite Paris Dauphine-PSL',
    'Universite Paris-Dauphine-': 'Universite Paris Dauphine-PSL',
    'Paris School of Economics': 'Paris School of Economics',
    'Sciences Po': 'Sciences Po',
    
    # Acronyms
    'Inrae': 'INRAE',
    'Cnrs': 'CNRS',
    'Cired': 'CIRED',
    'Crest': 'CREST',
    
    # Name fixes
    'Universite Dorleans': "Universite d'Orleans",
    "Universite dOrleans": "Universite d'Orleans",
    'Nantes Universite': 'Nantes Universite',
    'Universite Evry Paris-Saclay': 'Universite Evry Paris-Saclay',
    'Ecole Polytechnique - Crest': 'Ecole Polytechnique - CREST',
    'Ecole Polytechnique - CREST': 'Ecole Polytechnique - CREST',
    
    # Keep as-is (already good)
    'Universite de Strasbourg': 'Universite de Strasbourg',
    'Universite de Lille': 'Universite de Lille',
    'Universite de Bordeaux': 'Universite de Bordeaux',
    'Banque de France': 'Banque de France',
    'Universite Paris Nanterre': 'Universite Paris Nanterre',
}

for s in data['sessions']:
    for p in s['papers']:
        inst = p['institution_clean']
        if inst in AFSE_SAFE_MERGES:
            p['institution_clean'] = AFSE_SAFE_MERGES[inst]

# 4. Rebuild participant-centric data
participants = {}
for s in data['sessions']:
    for p in s['papers']:
        name = p['author']
        if name not in participants:
            participants[name] = {
                'name': name,
                'institution_raw': p['institution'],
                'institution_clean': p['institution_clean'],
                'papers': [],
                'is_presenter': True
            }
        participants[name]['papers'].append({
            'title': p['title'],
            'session': s['session_title']
        })

# Stabilize institutions per participant
from collections import Counter
for name, pdata in participants.items():
    insts_clean = []
    for s in data['sessions']:
        for pp in s['papers']:
            if pp.get('author') == name and 'institution_clean' in pp:
                insts_clean.append(pp['institution_clean'])
    if insts_clean:
        pdata['institution_clean'] = Counter(insts_clean).most_common(1)[0][0]

output = {
    "conference": data['conference'],
    "total_papers": data['total_papers'],
    "total_participants": len(participants),
    "sessions": data['sessions'],
    "participants": sorted(participants.values(), key=lambda x: x['name'])
}

# Count after
clean_insts = set()
for s in data['sessions']:
    for p in s['papers']:
        clean_insts.add(p['institution_clean'])
print(f"🏛️  Institutions uniques (nettoyees) : {len(clean_insts)}")
print(f"   Reduction : {len(raw_insts) - len(clean_insts)} ({(len(raw_insts)-len(clean_insts))/len(raw_insts)*100:.0f}%)")

# Save
import shutil
outdir = os.path.expanduser("~/economics-conferences/afse2026")
with open(os.path.join(outdir, "data.json"), "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n✅ Sauvegarde dans {outdir}/data.json")
print()

# Show top institutions
from collections import Counter
inst_counts = Counter()
for s in data['sessions']:
    for p in s['papers']:
        if len(p['institution_clean']) > 5:
            inst_counts[p['institution_clean']] += 1

print(f"🏛️  TOP 20 INSTITUTIONS AFSE 2026 :")
print(f"{'':>3s} {'Institution':55s} {'Papiers':>7s}")
for i, (inst, count) in enumerate(inst_counts.most_common(20), 1):
    print(f"  {i:2d}. {inst:55s} {count:2d}")

print(f"\n=== ÉCHANTILLON NETTOYE ===")
for s in data['sessions'][:3]:
    print(f"\n📌 {s['session_title'][:60]}")
    for p in s['papers'][:2]:
        print(f"   👤 {p['author'][:25]:25s}")
        print(f"     raw:   {p['institution'][:50]}")
        print(f"     clean: {p['institution_clean'][:50]}")
        print(f"     📄 {p['title'][:70]}")
