"""
Build ALL_CONFERENCES_2026.json — a structured dataset grouped by conference.

Output structure:
    {
        "AEA": {
            "conference_name": "American Economic Association Annual Meeting",
            "year": 2026,
            "participants": [
                {
                    "name": "Raj Chetty",
                    "institutions": ["Harvard University", "NBER"],
                    "papers": ["..."],
                    "sessions": ["..."]
                }
            ]
        },
        ...
    }

Usage:
    python -m econ_conf.build.json_builder [--input CSV_PATH] [--output JSON_PATH]
"""

import argparse
import csv
import json
import os
import re
import sys

from econ_conf.normalize.institutions import split_affiliations


def build_json(csv_path: str, json_path: str) -> dict:
    """Read CSV, normalize, group by conference, write JSON. Returns stats dict."""
    entries = {}  # {conf_short: {conference_name, year, participants: {name: {...}}}}
    stats = {'total_rows': 0, 'entries': 0, 'multi_inst': 0, 'with_nber': 0}

    with open(csv_path, newline='', encoding='utf-8') as f:
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

            # Init conference
            if conf_short not in entries:
                entries[conf_short] = {
                    'conference_name': conf_name,
                    'year': int(year) if year else 2026,
                    'participants': {},
                }

            conf = entries[conf_short]

            # Init participant
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

    # Reorganize: participants dict → sorted list
    output = {}
    for conf_short, conf_data in sorted(entries.items()):
        participants_list = [
            {'name': name, **data}
            for name, data in sorted(conf_data['participants'].items())
        ]
        output[conf_short] = {
            'conference_name': conf_data['conference_name'],
            'year': conf_data['year'],
            'participants': participants_list,
        }

    # Write JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return stats


def main():
    parser = argparse.ArgumentParser(description='Build ALL_CONFERENCES_2026.json')
    parser.add_argument('--input', default=os.path.expanduser('~/economics-conferences/ALL_CONFERENCES_2026.csv'),
                        help='Input CSV path')
    parser.add_argument('--output', default=os.path.expanduser('~/econ-conf/data/outputs/ALL_CONFERENCES_2026.json'),
                        help='Output JSON path')
    args = parser.parse_args()

    stats = build_json(args.input, args.output)

    print(f'✅ JSON: {args.output}')
    print(f'   Conferences:     {len(json.load(open(args.output))):>6,}')
    print(f'   Participants:    {stats["entries"]:>6,}')
    print(f'   Multi-affiliations: {stats["multi_inst"]:>6,}')
    print(f'   With NBER:          {stats["with_nber"]:>6,}')


if __name__ == '__main__':
    main()
