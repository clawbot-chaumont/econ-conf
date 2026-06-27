#!/usr/bin/env python3
"""
Sync ALL_CONFERENCES_2026.json -> Supabase.
Usage: python3 sync_to_supabase.py
"""
import json, os, httpx
from collections import Counter

SUPABASE_URL = "https://hiqdoxzyxlytcdufokoa.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhpcWRveHp5eGx5dGNkdWZva29hIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MjU4Njg0NywiZXhwIjoyMDk4MTYyODQ3fQ.Cp7cYO-JkIdkwYFHbqlEOxNci9tNtv6iHchCD-FhRjM"
JSON_PATH = os.path.expanduser("~/econ-conf/data/outputs/ALL_CONFERENCES_2026.json")

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

BASE = f"{SUPABASE_URL}/rest/v1"

def upsert_conferences(confs_data):
    rows = []
    for conf_key, conf in sorted(confs_data.items()):
        name = conf.get("conference_name", conf_key)
        short = conf_key.split(" (")[0].split(" 20")[0]
        year = conf.get("year", 2026)
        pcount = len(conf.get("participants", []))
        rows.append({"short_name": short, "full_name": name, "year": year, "participant_count": pcount})

    resp = httpx.post(
        f"{BASE}/conferences",
        headers={**HEADERS, "Prefer": "resolution=merge-duplicates,return=representation"},
        json=rows,
        timeout=60
    )
    if resp.status_code not in (200, 201):
        print(f"Conferences upsert failed: {resp.status_code} {resp.text[:300]}")
        return {}

    result = resp.json()
    name_to_id = {r["short_name"]: r["id"] for r in result}
    print(f"  {len(result)} conferences upserted")
    return name_to_id

def upsert_participants(confs_data, conf_id_map):
    batch = []
    for conf_key, conf in sorted(confs_data.items()):
        short_name = conf_key.split(" (")[0].split(" 20")[0]
        conf_id = conf_id_map.get(short_name)
        if not conf_id:
            print(f"  No conf_id for {conf_key}")
            continue
        for p in conf.get("participants", []):
            insts = [i for i in p.get("institutions", []) if i]
            papers = [pp for pp in p.get("papers", []) if pp]
            sessions = [ss for ss in p.get("sessions", []) if ss]
            batch.append({
                "conference_id": conf_id,
                "name": p["name"],
                "institutions": insts,
                "papers": papers,
                "sessions": sessions
            })

    print("  Clearing existing participants...")
    httpx.delete(f"{BASE}/participants", headers=HEADERS, timeout=30)

    total = 0
    for i in range(0, len(batch), 1000):
        chunk = batch[i:i+1000]
        resp = httpx.post(f"{BASE}/participants", headers={**HEADERS, "Prefer": "return=minimal"}, json=chunk, timeout=120)
        if resp.status_code in (200, 201, 204):
            total += len(chunk)
            print(f"  {total}/{len(batch)} participants...")
        else:
            print(f"  Batch failed at {i}: {resp.status_code} {resp.text[:200]}")
            return
    print(f"  {total} participants inserted")

def upsert_institutions(confs_data):
    counter = Counter()
    for conf in confs_data.values():
        for p in conf.get("participants", []):
            for inst in p.get("institutions", []):
                if inst:
                    counter[inst] += 1

    rows = [{"name": name, "participant_count": count} for name, count in counter.most_common()]

    print("  Clearing existing institutions...")
    httpx.delete(f"{BASE}/institutions", headers=HEADERS, timeout=30)

    total = 0
    for i in range(0, len(rows), 500):
        chunk = rows[i:i+500]
        resp = httpx.post(f"{BASE}/institutions", headers={**HEADERS, "Prefer": "return=minimal"}, json=chunk, timeout=60)
        if resp.status_code in (200, 201, 204):
            total += len(chunk)
    print(f"  {total} institutions inserted")

def main():
    print(f"Loading {JSON_PATH}...")
    with open(JSON_PATH) as f:
        data = json.load(f)
    print(f"{len(data)} conferences, {sum(len(c.get('participants',[])) for c in data.values())} participants")

    print("\n1 Conferences...")
    conf_id_map = upsert_conferences(data)

    print("\n2 Participants...")
    upsert_participants(data, conf_id_map)

    print("\n3 Institutions...")
    upsert_institutions(data)

    print("\nSync complete!")

if __name__ == "__main__":
    main()
