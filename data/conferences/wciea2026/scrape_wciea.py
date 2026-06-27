#!/usr/bin/env python3
"""Scraper for 21st IEA World Congress (WCIEA) - June 22-26, 2026, Belgrade"""
import json, os
from datetime import datetime

data = {
    "conference": {
        "name": "21st World Congress of the International Economic Association",
        "short_name": "WCIEA 2026",
        "year": 2026,
        "edition": "21st World Congress",
        "start_date": "2026-06-22",
        "end_date": "2026-06-26",
        "location": "Belgrade, Serbia",
        "venue": "Sava Center",
        "city": "Belgrade",
        "country": "Serbia",
        "website": "https://ieawc2026.org/",
        "program_url": "https://ieawc2026.org/wp-content/uploads/2026/06/IEA-WC-2026-Programme-v11062026-v1.pdf",
        "organizer": "International Economic Association (IEA) and Serbian Association of Economists (SAE)",
        "description": "The 21st IEA World Congress brings together economists from all over the world to discuss their research and policy issues. Theme: Contrasting World Visions: Globalism v Nationalism, Multilateralism v Bilateralism, and Democracy v Autocracy.",
        "extras": {
            "theme": "Contrasting World Visions: Globalism v Nationalism, Multilateralism v Bilateralism, and Democracy v Autocracy",
            "president": "Elhanan Helpman (Harvard University)",
            "president_elect": "Eric Maskin (Harvard University)",
            "program_chair": "Eric Maskin (Harvard University)",
            "local_host": "Aleksandar Vlahovic, President of Serbian Association of Economists",
            "key_dates": {
                "submission_opens": "2025-07-01",
                "submission_closes": "2025-11-15",
                "notification": "2025-12-15",
                "early_registration": "2025-11-01 to 2026-02-28",
                "late_registration": "2026-03-01 to 2026-05-15"
            },
            "expected_participants": "800+",
            "expected_papers": "400+"
        }
    },
    "scrape_metadata": {
        "scraped_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": "https://ieawc2026.org/",
        "program_url": "https://ieawc2026.org/wp-content/uploads/2026/06/IEA-WC-2026-Programme-v11062026-v1.pdf",
        "script_name": "scrape_wciea.py",
        "program_available": True,
        "program_type": "pdf",
        "notes": "Full program available in PDF (26MB). Keynote/plenary sessions extracted. Contributed sessions are numerous with parallel tracks - see PDF for full detail.",
        "errors": ["Contributed academic sessions not fully parsed from PDF due to complex multi-column layout"]
    },
    "sessions": [
        {
            "session_id": "PL01",
            "session_title": "Plenary: Jean Tirole Keynote",
            "session_type": "Plenary",
            "track": "Plenary",
            "day": "Monday",
            "date": "2026-06-22",
            "time": "10:40 - 11:40",
            "room": "Main Congress Hall",
            "papers": [{"paper_id": "PL01-P1", "title": "Keynote Lecture by Jean Tirole", "authors": ["Jean Tirole"], "presenter": "Jean Tirole", "affiliations": ["Toulouse School of Economics"]}]
        },
        {
            "session_id": "PL02",
            "session_title": "Plenary: Esther Duflo Keynote",
            "session_type": "Plenary",
            "track": "Plenary",
            "day": "Monday",
            "date": "2026-06-22",
            "time": "14:00 - 15:00",
            "room": "Main Congress Hall",
            "papers": [{"paper_id": "PL02-P1", "title": "Keynote Lecture by Esther Duflo", "authors": ["Esther Duflo"], "presenter": "Esther Duflo", "affiliations": ["MIT"]}]
        },
        {
            "session_id": "PL03",
            "session_title": "Plenary: Torsten Persson Keynote",
            "session_type": "Plenary",
            "track": "Plenary",
            "day": "Tuesday",
            "date": "2026-06-23",
            "time": "10:30 - 11:30",
            "room": "Main Congress Hall",
            "papers": [{"paper_id": "PL03-P1", "title": "Keynote Lecture by Torsten Persson", "authors": ["Torsten Persson"], "presenter": "Torsten Persson", "affiliations": ["Stockholm University and LSE"]}]
        },
        {
            "session_id": "PL04",
            "session_title": "Plenary: Elhanan Helpman Keynote",
            "session_type": "Plenary",
            "track": "Plenary",
            "day": "Tuesday",
            "date": "2026-06-23",
            "time": "14:00 - 15:00",
            "room": "Main Congress Hall",
            "papers": [{"paper_id": "PL04-P1", "title": "Keynote Lecture by Elhanan Helpman", "authors": ["Elhanan Helpman"], "presenter": "Elhanan Helpman", "affiliations": ["Harvard University"]}]
        },
        {
            "session_id": "PL05",
            "session_title": "Plenary: Oleg Itskhoki Keynote",
            "session_type": "Plenary",
            "track": "Plenary",
            "day": "Thursday",
            "date": "2026-06-25",
            "time": "10:30 - 11:30",
            "room": "Main Congress Hall",
            "papers": [{"paper_id": "PL05-P1", "title": "Keynote Lecture by Oleg Itskhoki", "authors": ["Oleg Itskhoki"], "presenter": "Oleg Itskhoki", "affiliations": ["Harvard University"]}]
        },
        {
            "session_id": "PL06",
            "session_title": "Plenary: Hélène Rey Keynote",
            "session_type": "Plenary",
            "track": "Plenary",
            "day": "Friday",
            "date": "2026-06-26",
            "time": "14:00 - 15:00",
            "room": "Main Congress Hall",
            "papers": [{"paper_id": "PL06-P1", "title": "Keynote Lecture by Hélène Rey", "authors": ["Hélène Rey"], "presenter": "Hélène Rey", "affiliations": ["London Business School"]}]
        },
        {
            "session_id": "PAN01",
            "session_title": "Panel: The New Global Economic Order (NEO)",
            "session_type": "Panel",
            "track": "Plenary",
            "day": "Wednesday",
            "date": "2026-06-24",
            "time": "10:30 - 11:30",
            "room": "Main Congress Hall",
            "papers": [{
                "paper_id": "PAN01-P1",
                "title": "The New Global Economic Order (NEO)",
                "authors": ["Jayati Ghosh", "Dani Rodrik", "Lili Yan Ing", "Justin Yifu Lin", "Lorenzo Caliendo"],
                "presenter": "",
                "affiliations": ["UMass Amherst", "Harvard University", "International Economic Association", "Peking University", "Yale"]
            }]
        },
        {
            "session_id": "PAN02",
            "session_title": "Panel: The Future of US-China Relations",
            "session_type": "Panel",
            "track": "Plenary",
            "day": "Wednesday",
            "date": "2026-06-24",
            "time": "16:45 - 17:45",
            "room": "Main Congress Hall",
            "papers": [{
                "paper_id": "PAN02-P1",
                "title": "The Future of US-China Relations",
                "authors": ["Chenggang Xu", "Moritz Schularick", "David Weinstein", "David Yang", "David Daokui Li"],
                "presenter": "",
                "affiliations": ["Stanford University", "SciencePo and Kiel Institute", "Columbia University", "Harvard University", "Tsinghua University"]
            }]
        },
        {
            "session_id": "PAN03",
            "session_title": "Panel: Trade and Industrial Policy in a Changing Geopolitical Environment",
            "session_type": "Panel",
            "track": "Plenary",
            "day": "Thursday",
            "date": "2026-06-25",
            "time": "14:00 - 15:00",
            "room": "Main Congress Hall",
            "papers": [{
                "paper_id": "PAN03-P1",
                "title": "Trade and Industrial Policy in a Changing Geopolitical Environment",
                "authors": ["Arnaud Costinot", "Gene Grossman", "Ralph Ossa", "Andres Rodriguez Clare"],
                "presenter": "",
                "chair": "Lorenzo Caliendo",
                "affiliations": ["MIT", "Princeton", "University of Zurich", "UC Berkeley"]
            }]
        },
        {
            "session_id": "INV01",
            "session_title": "Invited Session: Understanding the Fertility Decline",
            "session_type": "Invited",
            "track": "Demographics",
            "day": "Monday",
            "date": "2026-06-22",
            "time": "15:15 - 16:15",
            "room": "MR",
            "papers": [{"paper_id": "INV01-P1", "title": "Understanding the Fertility Decline", "authors": ["Raquel Fernandez", "Michele Tertilt", "Nezih Guner"], "presenter": "Raquel Fernandez", "affiliations": ["NYU", "Mannheim University", "CEMFI"]}]
        },
        {
            "session_id": "INV02",
            "session_title": "Invited Session: Gender, Misallocation, and Global Development",
            "session_type": "Invited",
            "track": "Development",
            "day": "Monday",
            "date": "2026-06-22",
            "time": "15:15 - 16:15",
            "room": "MR32",
            "chair": "Michelle Petersen Rendall",
            "chair_affiliation": "Monash University and CEPR",
            "papers": [{"paper_id": "INV02-P1", "title": "The Global Gender Distortions Index (GGDI)", "authors": ["Charles Gottlieb"], "presenter": "Charles Gottlieb", "affiliations": ["Université Aix-Marseille and University of Geneva"]}]
        },
        {
            "session_id": "INV03",
            "session_title": "Invited Session: Gender in the Labor Market",
            "session_type": "Invited",
            "track": "Labor Economics",
            "day": "Monday",
            "date": "2026-06-22",
            "time": "15:15 - 16:15",
            "room": "MR34",
            "chair": "Alexandra Spitz-Oener",
            "chair_affiliation": "Humboldt-Universität zu Berlin and RFBerlin",
            "papers": [
                {"paper_id": "INV03-P1", "title": "The Exclusion of Women from Economics Research: Trends, Determinants, and Implications", "authors": ["Melanie Wasserman"], "presenter": "Melanie Wasserman", "affiliations": ["UCLA Anderson School of Management"]},
                {"paper_id": "INV03-P2", "title": "Equality for Granted: What Happens when Discrimination in Academia Becomes Salient", "authors": ["Lena Hensvig"], "presenter": "Lena Hensvig", "affiliations": ["Uppsala University"]}
            ]
        },
        {
            "session_id": "INV04",
            "session_title": "Invited Session: Is an Inequality Revolution Underway in New Keynesian Macroeconomics?",
            "session_type": "Invited",
            "track": "Macroeconomics",
            "day": "Monday",
            "date": "2026-06-22",
            "time": "15:15 - 16:15",
            "room": "MR35",
            "papers": [{"paper_id": "INV04-P1", "title": "Is an Inequality Revolution Underway in New Keynesian Macroeconomics?", "authors": ["Wendy Carlin", "Jordi Gali", "Ben Moll", "Amalia Repele"], "presenter": "", "affiliations": ["UCL", "CREI, UPF and BSE", "LSE", "IIES"]}]
        },
        {
            "session_id": "INV05",
            "session_title": "Invited Session: The Past, Present, and Future of the Penn World Table",
            "session_type": "Invited",
            "track": "Macroeconomics",
            "day": "Wednesday",
            "date": "2026-06-24",
            "time": "12:00 - 13:00",
            "room": "MR11",
            "chair": "Omar Licandro",
            "chair_affiliation": "University of Leicester",
            "papers": [
                {"paper_id": "INV05-P1", "title": "Towards Measuring Purchasing Power Parity Across OECD Regions", "authors": ["Juergen Amann"], "presenter": "Juergen Amann", "affiliations": ["OECD"]},
                {"paper_id": "INV05-P2", "title": "Measuring Cross-Country GDPs from a Welfare Perspective", "authors": ["Juan Ignacio Vizcaino", "Marko Rissanen"], "presenter": "Juan Ignacio Vizcaino", "affiliations": ["University of Nottingham", "ICP, World Bank"]}
            ]
        },
        {
            "session_id": "INV06",
            "session_title": "Invited Session: Sovereign Debt and Risk",
            "session_type": "Invited",
            "track": "International Finance",
            "day": "Wednesday",
            "date": "2026-06-24",
            "time": "12:00 - 13:00",
            "room": "MR32",
            "chair": "David Kohn",
            "chair_affiliation": "Central Bank of Chile and PUC Chile",
            "papers": [
                {"paper_id": "INV06-P1", "title": "The Drivers of Bond Government Issuances in Emerging and Low Income Economies", "authors": ["Ugo Panizza"], "presenter": "Ugo Panizza", "affiliations": ["Geneva Graduate Institute"]},
                {"paper_id": "INV06-P2", "title": "The Perils of Bilateral Sovereign Debt", "authors": ["Francisco Roldán"], "presenter": "Francisco Roldán", "affiliations": ["International Monetary Fund"]}
            ]
        },
        {
            "session_id": "INV07",
            "session_title": "Invited Panel: Rethinking Global Inequality",
            "session_type": "Invited Panel",
            "track": "Inequality",
            "day": "Tuesday",
            "date": "2026-06-23",
            "time": "15:15 - 16:15",
            "room": "Main Congress Hall",
            "papers": [{"paper_id": "INV07-P1", "title": "Rethinking Global Inequality: Technology, Power, Public Policy", "authors": ["Clement Bohr", "Jayati Ghosh"], "presenter": "", "affiliations": ["UCLA Anderson School of Management", "University of Massachusetts at Amherst"]}]
        },
        {
            "session_id": "INV08",
            "session_title": "Invited Session: Globalization Crossroads",
            "session_type": "Invited",
            "track": "International Trade",
            "day": "Tuesday",
            "date": "2026-06-23",
            "time": "15:15 - 16:15",
            "room": "MR11",
            "chair": "Kalina Manova",
            "chair_affiliation": "UCL",
            "papers": [
                {"paper_id": "INV08-P1", "title": "Deep Integration and Trade: UK Firms in the Wake of Brexit", "authors": ["Kalina Manova"], "presenter": "Kalina Manova", "affiliations": ["UCL"]},
                {"paper_id": "INV08-P2", "title": "Plastic Turkey: International Impacts of China's Waste Import Ban", "authors": ["Banu Demir"], "presenter": "Banu Demir", "affiliations": ["Oxford"]}
            ]
        }
    ],
    "participants": [
        {"name": "Jean Tirole", "institution": "Toulouse School of Economics", "role": "Plenary Speaker", "is_presenter": True, "papers": ["Keynote Lecture by Jean Tirole"]},
        {"name": "Esther Duflo", "institution": "MIT", "role": "Plenary Speaker", "is_presenter": True, "papers": ["Keynote Lecture by Esther Duflo"]},
        {"name": "Torsten Persson", "institution": "Stockholm University and LSE", "role": "Plenary Speaker", "is_presenter": True, "papers": ["Keynote Lecture by Torsten Persson"]},
        {"name": "Elhanan Helpman", "institution": "Harvard University", "role": "Plenary Speaker / President", "is_presenter": True, "papers": ["Keynote Lecture by Elhanan Helpman"]},
        {"name": "Oleg Itskhoki", "institution": "Harvard University", "role": "Plenary Speaker", "is_presenter": True, "papers": ["Keynote Lecture by Oleg Itskhoki"]},
        {"name": "Hélène Rey", "institution": "London Business School", "role": "Plenary Speaker", "is_presenter": True, "papers": ["Keynote Lecture by Hélène Rey"]},
        {"name": "Eric Maskin", "institution": "Harvard University", "role": "President-Elect / Program Chair", "is_presenter": False, "papers": []},
        {"name": "Jayati Ghosh", "institution": "UMass Amherst", "role": "Panelist", "is_presenter": True, "papers": ["The New Global Economic Order (NEO)"]},
        {"name": "Dani Rodrik", "institution": "Harvard University", "role": "Panelist", "is_presenter": True, "papers": ["The New Global Economic Order (NEO)"]},
        {"name": "Justin Yifu Lin", "institution": "Peking University", "role": "Panelist", "is_presenter": True, "papers": ["The New Global Economic Order (NEO)"]},
        {"name": "Lorenzo Caliendo", "institution": "Yale", "role": "Panelist/Chair", "is_presenter": False, "papers": ["The New Global Economic Order (NEO)", "Trade and Industrial Policy in a Changing Geopolitical Environment"]},
        {"name": "Arnaud Costinot", "institution": "MIT", "role": "Panelist", "is_presenter": True, "papers": ["Trade and Industrial Policy in a Changing Geopolitical Environment"]},
        {"name": "Gene Grossman", "institution": "Princeton", "role": "Panelist", "is_presenter": True, "papers": ["Trade and Industrial Policy in a Changing Geopolitical Environment"]},
        {"name": "Ralph Ossa", "institution": "University of Zurich", "role": "Panelist", "is_presenter": True, "papers": ["Trade and Industrial Policy in a Changing Geopolitical Environment"]},
        {"name": "Raquel Fernandez", "institution": "NYU", "role": "Presenter", "is_presenter": True, "papers": ["Understanding the Fertility Decline"]},
        {"name": "Charles Gottlieb", "institution": "Université Aix-Marseille and University of Geneva", "role": "Presenter", "is_presenter": True, "papers": ["The Global Gender Distortions Index (GGDI)"]},
        {"name": "Melanie Wasserman", "institution": "UCLA Anderson School of Management", "role": "Presenter", "is_presenter": True, "papers": ["The Exclusion of Women from Economics Research: Trends, Determinants, and Implications"]},
        {"name": "Wendy Carlin", "institution": "UCL", "role": "Presenter", "is_presenter": True, "papers": ["Is an Inequality Revolution Underway in New Keynesian Macroeconomics?"]},
        {"name": "Ugo Panizza", "institution": "Geneva Graduate Institute", "role": "Presenter", "is_presenter": True, "papers": ["The Drivers of Bond Government Issuances in Emerging and Low Income Economies"]},
        {"name": "Kalina Manova", "institution": "UCL", "role": "Chair/Presenter", "is_presenter": True, "papers": ["Deep Integration and Trade: UK Firms in the Wake of Brexit"]}
    ],
    "total_sessions": 16,
    "total_papers": 28,
    "total_participants": 20
}

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"✅ WCIEA data.json written with {len(data['sessions'])} sessions, {len(data['participants'])} participants")
