#!/usr/bin/env python3
"""
econ-conf — Economics Conference Data Pipeline

One-command entry point to run the full pipeline:
  python run.py                  # Build JSON from latest CSV
  python run.py --from-scrape    # Re-scrape all conferences first
  python run.py --upload         # Build + upload to Google Drive
  python run.py --normalize      # Run institution normalization
  python run.py --conference AEA # Run pipeline for one conference
  python run.py --all            # Run pipeline for all conferences
  python run.py --status         # Show coverage stats
"""

import argparse
import json
import os
import sys
import subprocess
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_DIR, 'scripts')
OUTPUTS_DIR = os.path.join(PROJECT_DIR, 'data', 'outputs')
CONF_DIR    = os.path.join(PROJECT_DIR, 'data', 'conferences')

# Google Drive folder ID for conference data
DRIVE_FOLDER_ID = "1IQY4Ip1X2ZzsxLn14okVcvMuV0CQGQOQ"


def run_script(name, *args):
    """Run a script from the scripts/ directory."""
    script = os.path.join(SCRIPTS_DIR, name)
    if not os.path.exists(script):
        print(f"❌ Script not found: {script}")
        return False
    cmd = [sys.executable, script] + list(args)
    print(f"▶ Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0


def build_json():
    """Build ALL_CONFERENCES_2026.json from raw CSV."""
    print("\n" + "="*60)
    print("📦 Building ALL_CONFERENCES_2026.json...")
    print("="*60)
    
    # Find the CSV
    csv_candidates = [
        os.path.expanduser("~/economics-conferences/ALL_CONFERENCES_2026.csv"),
        os.path.join(OUTPUTS_DIR, 'ALL_CONFERENCES_2026.csv'),
    ]
    csv_path = None
    for p in csv_candidates:
        if os.path.exists(p):
            csv_path = p
            break
    
    if not csv_path:
        print("❌ No CSV found. Run --normalize first.")
        return False
    
    json_path = os.path.join(OUTPUTS_DIR, 'ALL_CONFERENCES_2026.json')
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    
    from econ_conf.build.json_builder import build_json as _build
    stats = _build(csv_path, json_path)
    
    print(f"✅ JSON built: {json_path}")
    print(f"   Conferences: {len(json.load(open(json_path)))}")
    print(f"   Participants: {stats['entries']}")
    return True


def upload_json():
    """Upload the built JSON to Google Drive."""
    json_path = os.path.join(OUTPUTS_DIR, 'ALL_CONFERENCES_2026.json')
    if not os.path.exists(json_path):
        print("❌ No JSON to upload. Run build first.")
        return False
    
    from econ_conf.utils.drive import upload
    try:
        result = upload(json_path, name="ALL_CONFERENCES_2026.json", parent=DRIVE_FOLDER_ID)
        print(f"✅ Uploaded: {result['webViewLink']}")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


def show_status():
    """Show coverage stats for all conferences."""
    from econ_conf.config import CONFERENCES_2026
    
    print("\n" + "="*60)
    print("📊 CONFERENCE COVERAGE STATUS")
    print("="*60)
    
    complete = 0
    partial = 0
    empty = 0
    
    for key, info in sorted(CONFERENCES_2026.items()):
        folder = info.get('folder', '')
        data_path = os.path.join(CONF_DIR, folder, 'data.json')
        
        if not os.path.exists(data_path):
            print(f"  ❌ {key:20s} No data folder")
            empty += 1
            continue
        
        with open(data_path) as f:
            data = json.load(f)
        
        sessions = len(data.get('sessions', []))
        participants = len(data.get('participants', []))
        conf_name = data.get('conference', {}).get('name', info['name'])[:50]
        
        if sessions > 0 and participants > 0:
            icon = "✅"
            complete += 1
        elif participants > 0 or sessions > 0:
            icon = "⚠️"
            partial += 1
        else:
            icon = "❌"
            empty += 1
        
        print(f"  {icon} {key:20s} {participants:>4} participants  {sessions:>3} sessions  — {conf_name}")
    
    print(f"\n  Complete: {complete}  |  Partial: {partial}  |  Empty: {empty}  |  Total: {len(CONFERENCES_2026)}")


def normalize():
    """Run institution normalization on the raw CSV."""
    print("\n" + "="*60)
    print("🏷️  Running institution normalization...")
    print("="*60)
    
    # Try to use the normalization script
    norm_script = os.path.join(SCRIPTS_DIR, 'normalize_institutions.py')
    if os.path.exists(norm_script):
        return run_script('normalize_institutions.py')
    else:
        print("❌ normalize_institutions.py not found")
        return False


def run_pipeline(conference_key=None):
    """Run the master pipeline for one or all conferences."""
    print("\n" + "="*60)
    print(f"🔄 Running master pipeline{' for ' + conference_key if conference_key else ''}...")
    print("="*60)
    
    pipeline_script = os.path.join(PROJECT_DIR, 'econ_conf', 'pipeline', 'master_pipeline.py')
    if not os.path.exists(pipeline_script):
        pipeline_script = os.path.join(SCRIPTS_DIR, 'master_pipeline.py')
    
    if not os.path.exists(pipeline_script):
        print("❌ master_pipeline.py not found")
        return False
    
    cmd = [sys.executable, pipeline_script]
    if conference_key:
        cmd.append(conference_key)
    else:
        cmd.append('--all')
    
    print(f"▶ Running: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description='Economics Conference Data Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--from-scrape', action='store_true', help='Scrape all conferences first')
    parser.add_argument('--normalize', action='store_true', help='Run institution normalization')
    parser.add_argument('--upload', action='store_true', help='Upload to Google Drive')
    parser.add_argument('--status', action='store_true', help='Show coverage stats')
    parser.add_argument('--conference', type=str, help='Run pipeline for one conference (key)')
    parser.add_argument('--all', action='store_true', help='Run pipeline for all conferences')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
        return
    
    if args.from_scrape:
        # Run the full scrape pipeline
        run_pipeline(None)  # all
    
    if args.normalize:
        normalize()
    
    # Always build JSON
    build_json()
    
    if args.upload:
        upload_json()
    
    if args.conference:
        run_pipeline(args.conference)
    
    if args.all:
        run_pipeline(None)
    
    # If no args, just build
    if not any(vars(args).values()):
        build_json()
    
    print(f"\n✅ Done at {datetime.now().strftime('%H:%M:%S')}")


if __name__ == '__main__':
    main()
