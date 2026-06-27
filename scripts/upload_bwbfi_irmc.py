#!/usr/bin/env python3
"""Upload BWBFI and IRMC v2 data + scripts to Google Drive."""
import json, os, sys

DATA_DIR = os.path.expanduser("~/economics-conferences")
sys.path.insert(0, os.path.join(DATA_DIR, "pipeline"))
from master_pipeline import CONFERENCES_2026, upload_to_drive

for key in ["BWBFI", "IRMC"]:
    conf_info = CONFERENCES_2026.get(key)
    if not conf_info:
        print(f"❌ Unknown: {key}")
        continue
    
    print(f"\n{'='*50}")
    print(f"📤 {key}: Uploading to Drive...")
    upload_to_drive(key, conf_info)

print("\n✅ All uploads complete!")
