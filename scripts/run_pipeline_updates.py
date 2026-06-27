#!/usr/bin/env python3
"""Run pipeline Sheet + Drive updates for all 5 conferences without overwriting data."""
import json, os, sys

DATA_DIR = "/root/economics-conferences"
sys.path.insert(0, os.path.join(DATA_DIR, "pipeline"))
from master_pipeline import CONFERENCES_2026, update_google_sheet, upload_to_drive

conferences = ["AFA", "CEPRPS", "ECBARC", "CMRC", "MYE"]

for key in conferences:
    conf_info = CONFERENCES_2026.get(key)
    if not conf_info:
        print(f"❌ Unknown: {key}")
        continue
    
    folder = conf_info["folder"]
    data_path = os.path.join(DATA_DIR, folder, "data.json")
    if not os.path.exists(data_path):
        print(f"❌ No data.json for {key}")
        continue
    
    with open(data_path) as f:
        data = json.load(f)
    
    print(f"\n{'='*50}")
    print(f"📤 {key}: Updating Sheet + Drive...")
    print(f"   Sessions: {data.get('total_sessions', len(data.get('sessions',[])))}, Participants: {data.get('total_participants', len(data.get('participants',[])))}")
    
    try:
        update_google_sheet(key, data, conf_info)
        print(f"   ✅ Sheet updated")
    except Exception as e:
        print(f"   ⚠️ Sheet error: {e}")
    
    try:
        upload_to_drive(key, conf_info)
        print(f"   ✅ Drive uploaded")
    except Exception as e:
        print(f"   ⚠️ Drive error: {e}")

print("\n🎉 All done!")
