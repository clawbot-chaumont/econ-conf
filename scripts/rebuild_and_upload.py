#!/usr/bin/env python3
"""
Step 1: Rebuild all v2 data files
Step 2: Update Sheet + Drive for GDRE, EEA, RES, CEBRA, SFS
"""
import json, os, sys
from datetime import datetime, timezone

DATA_DIR = os.path.expanduser("~/economics-conferences")
sys.path.insert(0, os.path.join(DATA_DIR))
sys.path.insert(0, os.path.join(DATA_DIR, "pipeline"))

# Step 1: rebuild all data
from scrape_all_v2 import *
import asyncio

async def step1():
    print("=" * 60)
    print("STEP 1: REBUILD v2 DATA")
    print("=" * 60)
    
    # GDRE
    print("\n📌 GDRE 2026")
    write_v2("gdre2026", build_gdre())
    
    # EEA - use TSV parser
    print("\n📌 EEA 2026")
    from eea_tsv_parser import build_eea_v2
    write_v2("eea2026", build_eea_v2())
    
    # RES
    print("\n📌 RES 2026")
    write_v2("res2026", convert_res_to_v2())
    
    # CEBRA
    print("\n📌 CEBRA 2026")
    write_v2("cebra2026", convert_cebra_to_v2())
    
    # SFS
    print("\n📌 SFS 2026")
    write_v2("sfs2026", convert_sfs_to_v2())

asyncio.run(step1())

# Step 2: Update Sheet + Drive
print("\n" + "=" * 60)
print("STEP 2: UPDATE SHEET + DRIVE")
print("=" * 60)

from master_pipeline import update_google_sheet, upload_to_drive, CONFERENCES_2026, load_data_json

for conf_key in ["GDRE", "EEA", "RES", "CEBRA", "SFS"]:
    conf_info = CONFERENCES_2026.get(conf_key)
    folder = conf_info["folder"]
    data = load_data_json(folder)
    
    if not data:
        print(f"❌ No data for {conf_key}")
        continue
    
    sessions = data.get("sessions", [])
    participants = data.get("participants", [])
    
    print(f"\n🏛️  {conf_key}")
    print(f"   Sessions: {len(sessions)}, Participants: {len(participants)}")
    
    # Update Sheet
    update_google_sheet(conf_key, data, conf_info)
    
    # Upload to Drive
    upload_to_drive(conf_key, conf_info)

print("\n" + "=" * 60)
print("✅ ALL DONE")
print("=" * 60)
