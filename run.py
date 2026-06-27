#!/usr/bin/env python3
"""
econ-conf — Economics Conference Data Pipeline

One-command entry point to run the full pipeline:
  python run.py                           # Build JSON from latest CSV
  python run.py --scrape AEA              # Scrape one conference
  python run.py --scrape-all              # Scrape all conferences with scrapers
  python run.py --process AEA             # Process data → sheet → Drive (one conf)
  python run.py --process-all             # Process all conferences
  python run.py --full AEA                # Scrape + process + build
  python run.py --full-all                # Full pipeline for all
  python run.py --normalize               # Run institution normalization
  python run.py --upload                  # Build + upload JSON to Drive
  python run.py --status                  # Show coverage stats
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

# Google Drive folder for conference data
DRIVE_FOLDER_ID = "1IQY4Ip1X2ZzsxLn14okVcvMuV0CQGQOQ"

# ── Scraper dispatch ───────────────────────────────────────────────────────
# Maps conference short keys to their scraper script(s).
# KEY: (scraper_script_in_conference_folder, type)
SCRAPER_DISPATCH = {
    # Custom per-conference scrapers
    "AEA":     ("aea2026/scrape_aea.py", "custom"),
    "AFA":     ("afa2026/scrape_afa_program.py", "custom"),
    "AFFI":    ("affi2026/parser_affi.py", "sciencesconf"),
    "AFSE":    ("afse2026/", "placeholder"),
    "BDPCEPR": ("bdpcepr2026/scrape_bdpcepr.py", "custom"),
    "BFSR":    ("bfsr2026/scrape_bfsr.py", "custom"),
    "BWBFI":   ("bwbfi2026/", "placeholder"),
    "CEA":     ("cea2026/", "placeholder"),
    "CMFR":    ("cmfr2026/scrape_cfmr.py", "custom"),
    "CSRA":    ("csra2026/", "placeholder"),
    "DES":     ("des2026/", "placeholder"),
    "EEA":     ("eea2026/eea_scraper_v3.py", "custom"),
    "EFA":     ("efa2026/", "conftool"),
    "ESSFM":   ("essfm2026/scrape_essfm.py", "custom"),
    "GFA":     ("gfa2026/scrape_gfa.py", "custom"),
    "IAAE":    ("iaae2026/", "placeholder"),
    "ICMAIF":  ("icmaif2026/", "placeholder"),
    "IRMC":    ("irmc2026/clean_irmc.py", "custom"),
    "JMA":     ("jma2026/", "placeholder"),
    "MOFIR":   ("mofir2026/parse_program.py", "custom"),
    "MPRC":    ("mprc2026/scrape_mprc.py", "custom"),
    "MYE":     ("mye2026/scrape_mye_v3.py", "custom"),
    "NBER_SI": ("nber2026/", "placeholder"),
    "PDFM":    ("pdfm2026/scrape_pdfm.py", "custom"),
    "RCEA":    ("rcea2026/scrape_rcea.py", "custom"),
    "RES":     ("res2026/scrape_program.py", "custom"),
    "RFILB":   ("rfilb2026/scrape_rfilb.py", "custom"),
    "SCFICF":  ("scficf/", "placeholder"),
    "SEA":     ("sea2026/scrape_sea.py", "custom"),
    "SFS":     ("sfs2026/", "conftool"),
    "SFWFIR":  ("sfwfir2026/scrape_sfwfir.py", "custom"),
    "SIC":     ("sic2026/", "placeholder"),
    "SSFMR":   ("ssfmr2026/scrape_ssfmr.py", "custom"),
    "SWCFI":   ("swcfi2026/", "placeholder"),
    "WCIEA":   ("wciea2026/scrape_wciea.py", "custom"),
    "WEAI":    ("weai2026/", "placeholder"),
    "WFA":     ("wfa2026/scrape_wfa_portal.py", "custom"),
    "3CMFI":   ("3cmfi2026/scrape_3cmfi_v4.py", "custom"),
    "ACMFR":   ("ac-mfr/scrape_acmfr.py", "custom"),
    "CMRC":    ("cmrc2026/", "placeholder"),
    "CEBRA":   ("cebra2026/", "placeholder"),
    "CEPRPS":  ("ceprps2026/", "placeholder"),
    "ECBARC":  ("ecbarc2026/", "placeholder"),
    "GDRE":    ("gdre2026/", "placeholder"),
}

# Batch scraper scripts (cover multiple conferences)
BATCH_SCRAPERS = [
    ("scrape_all_v2.py",      "scrape_all_v2.py"),
    ("fetch_conference_program.py", "fetch_conference_program.py"),
    ("sciencesconf_scraper.py",     "sciencesconf_scraper.py"),
    ("conftool_scraper.py",         "conftool_scraper.py"),
]


def run_script(script_path, *args, cwd=None):
    """Run a Python script."""
    if not os.path.exists(script_path):
        print(f"  ❌ Not found: {script_path}")
        return False
    cmd = [sys.executable, script_path] + list(args)
    print(f"  ▶ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode == 0


def scrape_conference(conf_key):
    """Run the scraper for a single conference."""
    from econ_conf.config import CONFERENCES_2026
    
    if conf_key not in SCRAPER_DISPATCH:
        print(f"❌ No scraper defined for {conf_key}")
        return False
    
    info = CONFERENCES_2026.get(conf_key, {})
    print(f"\n{'='*60}")
    print(f"🕸️  Scraping {conf_key} — {info.get('name', conf_key)}")
    print(f"{'='*60}")
    
    script_rel, stype = SCRAPER_DISPATCH[conf_key]
    
    if stype == "placeholder":
        print(f"  ⚠️  No dedicated scraper yet for {conf_key}")
        print(f"     Folder: data/conferences/{info.get('folder', '?')}")
        return False
    
    if stype == "conftool":
        # Use the shared conftool scraper
        ct_script = os.path.join(SCRIPTS_DIR, 'conftool_scraper.py')
        return run_script(ct_script, conf_key)
    
    if stype == "sciencesconf":
        sc_script = os.path.join(SCRIPTS_DIR, 'sciencesconf_scraper.py')
        return run_script(sc_script, conf_key)
    
    # Custom per-conference scraper
    script_path = os.path.join(CONF_DIR, script_rel)
    return run_script(script_path)


def scrape_all():
    """Run all available scrapers."""
    print("\n" + "="*60)
    print("🕸️  SCRAPING ALL CONFERENCES")
    print("="*60)
    
    success = 0
    failed = 0
    
    for conf_key in sorted(SCRAPER_DISPATCH.keys()):
        try:
            if scrape_conference(conf_key):
                success += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
    
    print(f"\n  ✅ {success} scraped, ❌ {failed} failed")
    return failed == 0


def process_conference(conf_key):
    """Run master_pipeline for one conference (convert → sheet → Drive)."""
    mp_script = os.path.join(PROJECT_DIR, 'econ_conf', 'pipeline', 'master_pipeline.py')
    if not os.path.exists(mp_script):
        mp_script = os.path.join(SCRIPTS_DIR, 'master_pipeline.py')
    
    if not os.path.exists(mp_script):
        print(f"❌ master_pipeline.py not found")
        return False
    
    return run_script(mp_script, conf_key)


def process_all():
    """Run master_pipeline for all conferences."""
    mp_script = os.path.join(PROJECT_DIR, 'econ_conf', 'pipeline', 'master_pipeline.py')
    if not os.path.exists(mp_script):
        mp_script = os.path.join(SCRIPTS_DIR, 'master_pipeline.py')
    
    if not os.path.exists(mp_script):
        print(f"❌ master_pipeline.py not found")
        return False
    
    return run_script(mp_script, '--all')


def build_json():
    """Build ALL_CONFERENCES_2026.json from the raw CSV."""
    print("\n" + "="*60)
    print("📦 Building ALL_CONFERENCES_2026.json...")
    print("="*60)
    
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
        print("  ❌ No CSV found. Run --normalize first.")
        return False
    
    json_path = os.path.join(OUTPUTS_DIR, 'ALL_CONFERENCES_2026.json')
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    
    from econ_conf.build.json_builder import build_json as _build
    stats = _build(csv_path, json_path)
    
    with open(json_path) as f:
        conf_count = len(json.load(f))
    
    print(f"  ✅ {json_path}")
    print(f"     Conferences: {conf_count}")
    print(f"     Participants: {stats['entries']}")
    return True


def upload_json():
    """Upload the built JSON to Google Drive."""
    json_path = os.path.join(OUTPUTS_DIR, 'ALL_CONFERENCES_2026.json')
    if not os.path.exists(json_path):
        print("  ❌ No JSON to upload. Run build first.")
        return False
    
    from econ_conf.utils.drive import upload
    try:
        result = upload(json_path, name="ALL_CONFERENCES_2026.json", parent=DRIVE_FOLDER_ID)
        print(f"  ✅ Uploaded: {result['webViewLink']}")
        return True
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        return False


def normalize():
    """Run institution normalization."""
    print("\n" + "="*60)
    print("🏷️  Running institution normalization...")
    print("="*60)
    
    norm_script = os.path.join(SCRIPTS_DIR, 'normalize_institutions.py')
    if os.path.exists(norm_script):
        return run_script(norm_script)
    else:
        print("  ❌ normalize_institutions.py not found")
        return False


def show_status():
    """Show coverage stats."""
    from econ_conf.config import CONFERENCES_2026
    
    print("\n" + "="*60)
    print("📊 CONFERENCE COVERAGE STATUS")
    print("="*60)
    
    complete = partial = empty = 0
    
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
        
        has_scraper = key in SCRAPER_DISPATCH
        stype = SCRAPER_DISPATCH.get(key, ('', ''))[1]
        
        if sessions > 0 and participants > 0:
            icon = "✅"
            complete += 1
        elif participants > 0 or sessions > 0:
            icon = "⚠️"
            partial += 1
        else:
            icon = "❌"
            empty += 1
        
        scraper_tag = f" [{stype}]" if has_scraper and stype != "placeholder" else ""
        print(f"  {icon} {key:20s} {participants:>4} parts  {sessions:>3} sess{scraper_tag:15s} — {conf_name}")
    
    print(f"\n  ✅ Complete: {complete}  |  ⚠️  Partial: {partial}  |  ❌ Empty: {empty}  |  Total: {len(CONFERENCES_2026)}")


def main():
    parser = argparse.ArgumentParser(
        description='Economics Conference Data Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--scrape', type=str, metavar='KEY', help='Scrape one conference')
    parser.add_argument('--scrape-all', action='store_true', help='Scrape all conferences')
    parser.add_argument('--process', type=str, metavar='KEY', help='Process one conf (sheet+Drive)')
    parser.add_argument('--process-all', action='store_true', help='Process all conferences')
    parser.add_argument('--full', type=str, metavar='KEY', help='Scrape + process + build (one)')
    parser.add_argument('--full-all', action='store_true', help='Full pipeline for all')
    parser.add_argument('--normalize', action='store_true', help='Run institution normalization')
    parser.add_argument('--upload', action='store_true', help='Upload JSON to Drive')
    parser.add_argument('--status', action='store_true', help='Show coverage stats')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
        return
    
    if args.scrape:
        scrape_conference(args.scrape)
    
    if args.scrape_all:
        scrape_all()
    
    if args.process:
        process_conference(args.process)
    
    if args.process_all:
        process_all()
    
    if args.normalize:
        normalize()
    
    if args.upload:
        build_json()
        upload_json()
    
    if args.full:
        scrape_conference(args.full)
        process_conference(args.full)
        build_json()
    
    if args.full_all:
        scrape_all()
        process_all()
        normalize()
        build_json()
    
    # Default: just build
    if not any(vars(args).values()):
        build_json()
    
    print(f"\n✅ Done at {datetime.now().strftime('%H:%M:%S')}")


if __name__ == '__main__':
    main()
