#!/usr/bin/env python3
"""
Final v2 data + pipeline runner.
Creates v2 data.json for all 5 conferences, then updates Sheet + Drive.
"""
import json, os, sys
from datetime import datetime

DATA_DIR = "/root/economics-conferences"
sys.path.insert(0, os.path.join(DATA_DIR, "pipeline"))
from master_pipeline import CONFERENCES_2026, write_data_json, update_google_sheet, upload_to_drive, convert_to_v2

def re_create_all():
    """Re-create v2 data.json for all 5 conferences after pipeline ran."""
    
    # ═══ AFA 2026 ═══
    afa_data = {
        "conference": {
            "name": "American Finance Association Annual Meeting",
            "short_name": "AFA 2026",
            "year": 2026,
            "edition": "2026 Annual Meeting",
            "start_date": "2026-01-03",
            "end_date": "2026-01-05",
            "location": "Philadelphia, PA, USA",
            "venue": "Loews Philadelphia Hotel & Philadelphia Marriott Downtown",
            "city": "Philadelphia",
            "country": "USA",
            "website": "https://www.afajof.org/annual-meeting/",
            "program_url": "https://afajof.org/management/full-program2026.html",
            "organizer": "American Finance Association",
            "description": "The annual meeting of the American Finance Association, featuring research presentations in all areas of finance.",
            "extras": {
                "program_chair": "Wei Jiang",
                "phd_student_panel": "Navigating Research Setbacks, When to Stay and When to Fold, How to Take Rejections Well, Connecting with Your Audience",
                "presidential_address": "Ulrike Malmendier on 'Human Finance: Incorporating Insights from the Life...'",
                "special_sessions": ["AFA Panel: Private Assets Amidst Regulation and Technology", "Poster Session TOUR", "AFA PhD Student Panel", "AFFECT Committee Reception - DATA AND DRINKS"],
            }
        },
        "scrape_metadata": {
            "scraped_at": datetime.now().isoformat(),
            "source_url": "https://www.afajof.org/annual-meeting/",
            "program_url": "https://afajof.org/management/full-program2026.html",
            "script_name": "create_v2_all.py",
            "program_available": True,
            "program_type": "web",
            "notes": "Full program with ~205 sessions and ~245 papers. Scraped from AFA management site.",
            "errors": [],
        },
        "sessions": [],
        "participants": [],
        "papers": [],
        "total_sessions": 205,
        "total_papers": 245,
        "total_participants": 0,
    }
    
    # Load old data to preserve sessions
    old_path = os.path.join(DATA_DIR, "afa2026", "data.json")
    if os.path.exists(old_path):
        with open(old_path) as f:
            old_content = f.read()
        # Find sessions data in old format
        import re
        # Try to find sessions data
        try:
            old_data = json.loads(old_content)
            if old_data.get("sessions"):
                afa_data["sessions"] = old_data["sessions"]
                # Recalculate
                total_papers = 0
                for s in afa_data["sessions"]:
                    total_papers += len(s.get("papers", []))
                afa_data["total_sessions"] = len(afa_data["sessions"])
                afa_data["total_papers"] = total_papers
            if old_data.get("participants"):
                afa_data["participants"] = old_data["participants"]
                afa_data["total_participants"] = len(old_data["participants"])
        except:
            pass
    
    write_data_json("afa2026", afa_data)
    
    # ═══ CEPRPS 2026 ═══
    ceprps_data = {
        "conference": {
            "name": "CEPR Paris Symposium",
            "short_name": "CEPRPS 2026",
            "year": 2026,
            "edition": "5th Edition",
            "start_date": "2026-12-08",
            "end_date": "2026-12-10",
            "location": "Paris, France",
            "venue": "",
            "city": "Paris",
            "country": "France",
            "website": "https://cepr.org/events/event-series/cepr-paris-symposium",
            "program_url": "",
            "organizer": "Centre for Economic Policy Research (CEPR)",
            "description": "The 5th edition of CEPR's annual flagship symposium. No dedicated event page or program published yet.",
            "extras": {
                "likely_venues": ["Banque de France", "Collège de France", "Sciences Po"],
                "past_program_2025_url": "https://cepr.org/system/files/2025-10/2025_Paris_Sym_Prelim.pdf",
            }
        },
        "scrape_metadata": {
            "scraped_at": datetime.now().isoformat(),
            "source_url": "https://cepr.org/events/event-series/cepr-paris-symposium",
            "program_url": None,
            "script_name": "create_v2_all.py",
            "program_available": False,
            "program_type": "web",
            "notes": "Dedicated 2026 page not published yet (404). Event expected December 2026.",
            "errors": ["CEPR event page returned 404", "No program URL available yet"],
        },
        "sessions": [],
        "participants": [],
        "total_sessions": 0,
        "total_papers": 0,
        "total_participants": 0,
    }
    write_data_json("ceprps2026", ceprps_data)
    
    # ═══ ECBARC 2026 ═══
    ecbarc_data = {
        "conference": {
            "name": "ECB Annual Research Conference",
            "short_name": "ECBARC 2026",
            "year": 2026,
            "edition": "11th Edition",
            "start_date": "2026-09-21",
            "end_date": "2026-09-22",
            "location": "Frankfurt, Germany",
            "venue": "",
            "city": "Frankfurt",
            "country": "Germany",
            "website": "https://www.ecb.europa.eu/press/conferences/html/index.en.html",
            "organizer": "European Central Bank",
            "description": "The 11th ECB Annual Research Conference. Listed on ECB conferences page but no dedicated page or program published yet.",
            "extras": {
                "contact_email": "ARConference@ecb.europa.eu",
                "reference_2025_theme": "The Next Financial Crisis?",
                "reference_2025_joint_with": "Stanford's Hoover Institution",
            }
        },
        "scrape_metadata": {
            "scraped_at": datetime.now().isoformat(),
            "source_url": "https://www.ecb.europa.eu/press/conferences/html/index.en.html",
            "program_url": None,
            "script_name": "create_v2_all.py",
            "program_available": False,
            "program_type": "web",
            "notes": "Listed on ECB conferences index (no hyperlink). Dedicated page not published yet.",
            "errors": [
                "ECB ARC dedicated page -> 404 (not published yet)",
            ],
        },
        "sessions": [],
        "participants": [],
        "total_sessions": 0,
        "total_papers": 0,
        "total_participants": 0,
    }
    write_data_json("ecbarc2026", ecbarc_data)
    
    # ═══ CMRC 2026 ═══
    cmrc_data = {
        "conference": {
            "name": "Community Banking Research Conference",
            "short_name": "CMRC 2026",
            "year": 2026,
            "edition": "14th Annual",
            "start_date": "2026-10-06",
            "end_date": "2026-10-07",
            "location": "St. Louis, MO, USA",
            "venue": "Gateway Auditorium, Federal Reserve Bank of St. Louis",
            "city": "St. Louis",
            "country": "USA",
            "website": "https://www.communitybanking.org/conferences/2026",
            "organizer": "Federal Reserve System, CSBS, FDIC",
            "description": "Brings together community bankers, academics, policymakers and bank regulators to discuss the latest research on community banking.",
            "extras": {
                "keynote_speaker": {"name": "Jill Castilla", "organization": "Citizens Bank of Edmond", "title": "Chairman, President and CEO"},
                "emerging_scholars": ["Aidan Hathaway (University of Alabama)", "Jeffrey Jou (University of Pennsylvania)", "Asli Uyanik (Rice University)"],
                "cfp_deadline": "2026-05-01",
                "author_notification": "2026-06-22",
                "case_study_competition": "35 student teams from 27 colleges and universities",
            }
        },
        "scrape_metadata": {
            "scraped_at": datetime.now().isoformat(),
            "source_url": "https://www.communitybanking.org/conferences/2026",
            "program_url": "https://www.communitybanking.org/conferences/2026",
            "script_name": "create_v2_all.py",
            "program_available": False,
            "program_type": "web",
            "notes": "AngularJS SPA. Detailed program not published yet. CfP closed May 1; notifications June 22.",
            "errors": ["Detailed program/sessions not published yet"],
        },
        "sessions": [],
        "participants": [
            {"name": "Jill Castilla", "institution": "Citizens Bank of Edmond", "role": "Keynote Speaker", "is_presenter": True, "papers": [], "paper_titles": []},
            {"name": "Aidan Hathaway", "institution": "University of Alabama", "role": "Emerging Scholar", "is_presenter": True, "papers": [], "paper_titles": []},
            {"name": "Jeffrey Jou", "institution": "University of Pennsylvania", "role": "Emerging Scholar", "is_presenter": True, "papers": [], "paper_titles": []},
            {"name": "Asli Uyanik", "institution": "Rice University", "role": "Emerging Scholar", "is_presenter": True, "papers": [], "paper_titles": []},
        ],
        "total_sessions": 0,
        "total_papers": 0,
        "total_participants": 4,
    }
    write_data_json("cmrc2026", cmrc_data)
    
    # ═══ MYE 2026 ═══
    mye_data = {
        "conference": {
            "name": "EAYE Annual Meeting (formerly Spring Meeting of Young Economists)",
            "short_name": "MYE 2026",
            "year": 2026,
            "edition": "2026 Edition",
            "start_date": "2026-05-18",
            "end_date": "2026-05-20",
            "location": "Bilbao, Spain",
            "venue": "Bizkaia Aretoa",
            "city": "Bilbao",
            "country": "Spain",
            "website": "https://www.eaye.info/",
            "program_url": "https://www.eaye.info/eayeam/2026-edition/program-2026",
            "organizer": "European Association of Young Economists (EAYE)",
            "description": "Major international conference for young economists. Formerly called the Spring Meeting of Young Economists (SMYE).",
            "extras": {
                "host": "University of the Basque Country",
                "keynote_speakers": [
                    {"name": "Manuel Arellano", "institution": "CEMFI"},
                    {"name": "Giacomo Ponzetto", "institution": "CREI and Universitat Pompeu Fabra"},
                ],
                "submission_deadline": "2025-12-28",
                "submission_system": "CMT (Microsoft)",
                "conference_dinner": "San Joseren Jauregia, Getxo",
                "cocktail_reception": "Menchu Gal terrace at Bizkaia Aretoa",
                "original_domain": "smye.org (expired)",
                "new_home": "eaye.info",
            }
        },
        "scrape_metadata": {
            "scraped_at": datetime.now().isoformat(),
            "source_url": "https://www.eaye.info/",
            "program_url": "https://www.eaye.info/eayeam/2026-edition/program-2026",
            "script_name": "create_v2_all.py",
            "program_available": True,
            "program_type": "web",
            "notes": "SMYE domain expired. Moved to eaye.info. Conference took place May 18-20 2026 in Bilbao. Program page exists but detailed schedule not published online. Keynotes confirmed.",
            "errors": ["smye.org -> domain expired", "Program page has no detailed schedule content"],
        },
        "sessions": [],
        "participants": [
            {"name": "Manuel Arellano", "institution": "CEMFI", "role": "Keynote Speaker", "is_presenter": True, "papers": [], "paper_titles": []},
            {"name": "Giacomo Ponzetto", "institution": "CREI and Universitat Pompeu Fabra", "role": "Keynote Speaker", "is_presenter": True, "papers": [], "paper_titles": []},
        ],
        "papers": [],
        "total_sessions": 0,
        "total_papers": 0,
        "total_participants": 2,
    }
    write_data_json("mye2026", mye_data)
    
    print("✅ All v2 data.json files (re)created!")

if __name__ == "__main__":
    # Step 1: Create v2 data
    re_create_all()
    
    # Step 2: For each conference, update sheet + drive
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
        print(f"📤 {key}: Updating sheet + drive...")
        
        # Update Sheet
        update_google_sheet(key, data, conf_info)
        
        # Upload to Drive
        upload_to_drive(key, conf_info)
        
        print(f"✅ {key} done!")
    
    print("\n🎉 All 5 conferences processed for Sheet + Drive!")
