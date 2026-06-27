#!/usr/bin/env python3
"""Scraper for 5th BFSR Conference - March 23-24, 2026, Rome"""
import json, os
from datetime import datetime

data = {
    "conference": {
        "name": "5th Bank of Italy, Bocconi University, EIEF and CEPR Conference on Financial Stability and Regulation",
        "short_name": "BFSR 2026",
        "year": 2026,
        "edition": "5th",
        "start_date": "2026-03-23",
        "end_date": "2026-03-24",
        "location": "Rome, Italy",
        "venue": "Carlo Azeglio Ciampi Centre for Monetary and Financial Education, Banca d'Italia",
        "city": "Rome",
        "country": "Italy",
        "website": "https://www.bancaditalia.it/media/agenda/2026-03-23_fifth-edition-of-the-conference-on-financial-stability-and-regulation/",
        "program_url": "https://www.bancaditalia.it/media/agenda/convegni-2026/5th-BdI-Bocconi-EIEF-CEPR-program.pdf",
        "organizer": "Banca d'Italia, Bocconi University – Baffi, EIEF, CEPR",
        "description": "The conference brings together leading world scholars and policy-makers to discuss financial stability and regulation.",
        "extras": {
            "keynote_speaker": "Tano Santos (Columbia Business School and CEPR)",
            "opening_remarks": "Chiara Scotti, Board Member, Banca d'Italia",
            "program_committee": [
                "Emilia Bonaccorsi di Patti (Banca d'Italia)",
                "Elena Carletti (Bocconi University, CEPR)",
                "Filippo De Marco (Bocconi University, CEPR)",
                "Alessio De Vincenzo (Banca d'Italia)",
                "Andrea Fabiani (Banca d'Italia)",
                "Marco Pagano (University of Naples Federico II, EIEF, CEPR)",
                "José Luis Peydró (LUISS, EIEF, CEPR)",
                "Andrea Polo (LUISS, EIEF, CEPR)",
                "Anatoli Segura (Banca d'Italia, CEPR)"
            ]
        }
    },
    "scrape_metadata": {
        "scraped_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": "https://www.bancaditalia.it/media/agenda/2026-03-23_fifth-edition-of-the-conference-on-financial-stability-and-regulation/",
        "program_url": "https://www.bancaditalia.it/media/agenda/convegni-2026/5th-BdI-Bocconi-EIEF-CEPR-program.pdf",
        "script_name": "scrape_bfsr.py",
        "program_available": True,
        "program_type": "pdf",
        "notes": "Program extracted from PDF. Sessions structured from PDF content.",
        "errors": []
    },
    "sessions": [
        {
            "session_id": "S01",
            "session_title": "Session I - Monetary Policy Transmission through Bank Balance Sheets",
            "session_type": "Contributed",
            "track": "Monetary Policy",
            "day": "Monday",
            "date": "2026-03-23",
            "time": "10:20 - 11:50",
            "chair": "José Luis Peydró",
            "chair_affiliation": "LUISS, EIEF and CEPR",
            "papers": [
                {
                    "paper_id": "P001",
                    "title": "Securities Losses and the Bank Collateral Channel of Monetary Transmission",
                    "authors": ["Mariassunta Giannetti", "Martina Jasova", "Caterina Mendicino", "Dominik Supera"],
                    "presenter": "Caterina Mendicino",
                    "discussant": "Christian Eufinger (IESE Business School)",
                    "affiliations": ["Stockholm School of Economics and CEPR", "Columbia University", "European Central Bank", "Columbia Business School"]
                },
                {
                    "paper_id": "P002",
                    "title": "Quantitative Tightening: The Bank Liquidity-Duration Nexus",
                    "authors": ["Matthieu Chavaz", "Alba Patozi", "Mo Wazzi"],
                    "presenter": "Matthieu Chavaz",
                    "discussant": "Enrico Sette (European Central Bank and CEPR)",
                    "affiliations": ["Bank for International Settlements", "Bank of England", "University of Oxford"]
                }
            ]
        },
        {
            "session_id": "S02",
            "session_title": "Session II - Information, Platforms, and Algorithms in Credit Markets",
            "session_type": "Contributed",
            "track": "Credit Markets",
            "day": "Monday",
            "date": "2026-03-23",
            "time": "12:00 - 13:30",
            "chair": "Marco Pagano",
            "chair_affiliation": "University of Naples Federico II, EIEF and CEPR",
            "papers": [
                {
                    "paper_id": "P003",
                    "title": "Platform finance",
                    "authors": ["Yingjie Huang"],
                    "presenter": "Yingjie Huang",
                    "discussant": "Magdalena Rola-Janicka (Imperial College and CEPR)",
                    "affiliations": ["University of Amsterdam"]
                },
                {
                    "paper_id": "P004",
                    "title": "Black Box Credit Scoring and Data Sharing",
                    "authors": ["Alessio Ozanne"],
                    "presenter": "Alessio Ozanne",
                    "discussant": "Chiara Lattanzio (UCL)",
                    "affiliations": ["University of Vienna"]
                }
            ]
        },
        {
            "session_id": "S03",
            "session_title": "Session III - Safe Asset Market Fragility, Dealers, and Central Bank Interventions",
            "session_type": "Contributed",
            "track": "Financial Markets",
            "day": "Monday",
            "date": "2026-03-23",
            "time": "14:30 - 16:00",
            "chair": "Enrico Perotti",
            "chair_affiliation": "University of Amsterdam and CEPR",
            "papers": [
                {
                    "paper_id": "P005",
                    "title": "Central Bank Balance Sheet and Treasury Market Disruptions",
                    "authors": ["Adrien d'Avernas", "Damon Petersen", "Quentin Vandeweyver"],
                    "presenter": "Quentin Vandeweyver",
                    "discussant": "Loriana Pelizzon (SAFE Goethe, University of Venice and CEPR)",
                    "affiliations": ["Stockholm School of Economics and CEPR", "MIT", "Chicago Booth"]
                },
                {
                    "paper_id": "P006",
                    "title": "Dealers Information and Liquidity Crises in Safe Assets",
                    "authors": ["Robert Czech", "Win Monroe"],
                    "presenter": "Win Monroe",
                    "discussant": "Andrei Kirilenko (Cambridge Judge Business School and CEPR)",
                    "affiliations": ["Bank of England", "Copenhagen Business School"]
                }
            ]
        },
        {
            "session_id": "S04",
            "session_title": "Session IV - Distressed Firms, Credit Misallocation, and Macroeconomic Trade-offs",
            "session_type": "Contributed",
            "track": "Macroeconomics",
            "day": "Monday",
            "date": "2026-03-23",
            "time": "16:30 - 18:00",
            "chair": "Emilia Bonaccorsi di Patti",
            "chair_affiliation": "Banca d'Italia",
            "papers": [
                {
                    "paper_id": "P007",
                    "title": "Extend-and-Pretend in the U.S. CRE Market",
                    "authors": ["Matteo Crosignani", "Saketh Prazad"],
                    "presenter": "Matteo Crosignani",
                    "discussant": "Luana Zaccaria (Luiss, EIEF and CEPR)",
                    "affiliations": ["Federal Reserve Bank of New York", "Harvard University"]
                },
                {
                    "paper_id": "P008",
                    "title": "Stabilization vs. Growth",
                    "authors": ["Miguel Faria-e-Castro", "Pascal Paul", "Juan M. Sánchez"],
                    "presenter": "Pascal Paul",
                    "discussant": "Federico Kochen (CEMFI)",
                    "affiliations": ["Federal Reserve Bank of Saint Louis", "Federal Reserve Bank of San Francisco", "Federal Reserve Bank of Saint Louis"]
                }
            ]
        },
        {
            "session_id": "S05",
            "session_title": "Session V - Bank Regulation, Supervision, and Credit Allocation",
            "session_type": "Contributed",
            "track": "Banking Regulation",
            "day": "Tuesday",
            "date": "2026-03-24",
            "time": "09:30 - 11:00",
            "chair": "Rafael Repullo",
            "chair_affiliation": "CEMFI and CEPR",
            "papers": [
                {
                    "paper_id": "P009",
                    "title": "Mitigating the risks of deregulation: The role of supervisory attention",
                    "authors": ["Elena Carletti", "Filippo De Marco", "Alberto Manconi", "Isabella Wolfskeil"],
                    "presenter": "Alberto Manconi",
                    "discussant": "Puriya Abbassi (BIS)",
                    "affiliations": ["Bocconi and CEPR", "Bocconi and CEPR", "Bocconi and CEPR", "Federal Reserve Board of Governors"]
                },
                {
                    "paper_id": "P010",
                    "title": "Supervisory-Driven Credit Reallocation",
                    "authors": ["F. Fiordelisi", "A. Maddaloni", "David Marques Ibanez", "Manju Puri", "Francesco Saverio Stentella Lopes"],
                    "presenter": "A. Maddaloni",
                    "discussant": "Angelo D'Andrea (Banca d'Italia)",
                    "affiliations": ["University of Essex", "European Central Bank", "European Central Bank", "Duke University (Fuqua School of Business)", "University of Roma Tre"]
                }
            ]
        },
        {
            "session_id": "S06",
            "session_title": "Session VI - Non-banks and Their Interconnections with Banks",
            "session_type": "Contributed",
            "track": "Financial Stability",
            "day": "Tuesday",
            "date": "2026-03-24",
            "time": "11:30 - 13:00",
            "chair": "Alessio De Vincenzo",
            "chair_affiliation": "Banca d'Italia",
            "papers": [
                {
                    "paper_id": "P011",
                    "title": "The Value of Contingent Liquidity from Banks to Nonbank Lenders",
                    "authors": ["Chi Xu"],
                    "presenter": "Chi Xu",
                    "discussant": "Giorgia Piacentino (USC Marshall and CEPR)",
                    "affiliations": ["University of Pennsylvania - The Wharton School"]
                },
                {
                    "paper_id": "P012",
                    "title": "Life Insurers' Private Credit Investments and Annuity Market Share Capture",
                    "authors": ["Ralf Meisenzhal", "Jackson Overpeck", "Andy Polacek"],
                    "presenter": "Ralf Meisenzhal",
                    "discussant": "Dominik Damast (Luiss)",
                    "affiliations": ["Federal Reserve Bank of Chicago", "Federal Reserve Bank of Chicago", "Federal Reserve Bank of Chicago"]
                }
            ]
        }
    ],
    "participants": [
        {"name": "Chiara Scotti", "institution": "Banca d'Italia", "role": "Speaker", "is_presenter": True, "papers": [], "paper_titles": ["Welcome Address"]},
        {"name": "Tano Santos", "institution": "Columbia Business School and CEPR", "role": "Keynote Speaker", "is_presenter": True, "papers": [], "paper_titles": ["Destabilizing Digital Bank Walks"]},
        {"name": "Elena Carletti", "institution": "Bocconi and CEPR", "role": "Chair", "is_presenter": False, "papers": ["Mitigating the risks of deregulation: The role of supervisory attention"], "paper_titles": ["Mitigating the risks of deregulation: The role of supervisory attention"]},
        {"name": "José Luis Peydró", "institution": "LUISS, EIEF and CEPR", "role": "Chair", "is_presenter": False, "papers": [], "paper_titles": []},
        {"name": "Mariassunta Giannetti", "institution": "Stockholm School of Economics and CEPR", "role": "Author", "is_presenter": False, "papers": ["Securities Losses and the Bank Collateral Channel of Monetary Transmission"], "paper_titles": ["Securities Losses and the Bank Collateral Channel of Monetary Transmission"]},
        {"name": "Martina Jasova", "institution": "Columbia University", "role": "Author", "is_presenter": False, "papers": ["Securities Losses and the Bank Collateral Channel of Monetary Transmission"], "paper_titles": ["Securities Losses and the Bank Collateral Channel of Monetary Transmission"]},
        {"name": "Caterina Mendicino", "institution": "European Central Bank", "role": "Presenter", "is_presenter": True, "papers": ["Securities Losses and the Bank Collateral Channel of Monetary Transmission"], "paper_titles": ["Securities Losses and the Bank Collateral Channel of Monetary Transmission"]},
        {"name": "Dominik Supera", "institution": "Columbia Business School", "role": "Author", "is_presenter": False, "papers": ["Securities Losses and the Bank Collateral Channel of Monetary Transmission"], "paper_titles": ["Securities Losses and the Bank Collateral Channel of Monetary Transmission"]},
        {"name": "Matthieu Chavaz", "institution": "Bank for International Settlements", "role": "Presenter", "is_presenter": True, "papers": ["Quantitative Tightening: The Bank Liquidity-Duration Nexus"], "paper_titles": ["Quantitative Tightening: The Bank Liquidity-Duration Nexus"]},
        {"name": "Alba Patozi", "institution": "Bank of England", "role": "Author", "is_presenter": False, "papers": ["Quantitative Tightening: The Bank Liquidity-Duration Nexus"], "paper_titles": ["Quantitative Tightening: The Bank Liquidity-Duration Nexus"]},
        {"name": "Mo Wazzi", "institution": "University of Oxford", "role": "Author", "is_presenter": False, "papers": ["Quantitative Tightening: The Bank Liquidity-Duration Nexus"], "paper_titles": ["Quantitative Tightening: The Bank Liquidity-Duration Nexus"]},
        {"name": "Marco Pagano", "institution": "University of Naples Federico II, EIEF and CEPR", "role": "Chair", "is_presenter": False, "papers": [], "paper_titles": []},
        {"name": "Yingjie Huang", "institution": "University of Amsterdam", "role": "Presenter", "is_presenter": True, "papers": ["Platform finance"], "paper_titles": ["Platform finance"]},
        {"name": "Alessio Ozanne", "institution": "University of Vienna", "role": "Presenter", "is_presenter": True, "papers": ["Black Box Credit Scoring and Data Sharing"], "paper_titles": ["Black Box Credit Scoring and Data Sharing"]},
        {"name": "Enrico Perotti", "institution": "University of Amsterdam and CEPR", "role": "Chair", "is_presenter": False, "papers": [], "paper_titles": []},
        {"name": "Adrien d'Avernas", "institution": "Stockholm School of Economics and CEPR", "role": "Author", "is_presenter": False, "papers": ["Central Bank Balance Sheet and Treasury Market Disruptions"], "paper_titles": ["Central Bank Balance Sheet and Treasury Market Disruptions"]},
        {"name": "Damon Petersen", "institution": "MIT", "role": "Author", "is_presenter": False, "papers": ["Central Bank Balance Sheet and Treasury Market Disruptions"], "paper_titles": ["Central Bank Balance Sheet and Treasury Market Disruptions"]},
        {"name": "Quentin Vandeweyver", "institution": "Chicago Booth", "role": "Presenter", "is_presenter": True, "papers": ["Central Bank Balance Sheet and Treasury Market Disruptions"], "paper_titles": ["Central Bank Balance Sheet and Treasury Market Disruptions"]},
        {"name": "Robert Czech", "institution": "Bank of England", "role": "Author", "is_presenter": False, "papers": ["Dealers Information and Liquidity Crises in Safe Assets"], "paper_titles": ["Dealers Information and Liquidity Crises in Safe Assets"]},
        {"name": "Win Monroe", "institution": "Copenhagen Business School", "role": "Presenter", "is_presenter": True, "papers": ["Dealers Information and Liquidity Crises in Safe Assets"], "paper_titles": ["Dealers Information and Liquidity Crises in Safe Assets"]},
        {"name": "Emilia Bonaccorsi di Patti", "institution": "Banca d'Italia", "role": "Chair", "is_presenter": False, "papers": [], "paper_titles": []},
        {"name": "Matteo Crosignani", "institution": "Federal Reserve Bank of New York", "role": "Presenter", "is_presenter": True, "papers": ["Extend-and-Pretend in the U.S. CRE Market"], "paper_titles": ["Extend-and-Pretend in the U.S. CRE Market"]},
        {"name": "Saketh Prazad", "institution": "Harvard University", "role": "Author", "is_presenter": False, "papers": ["Extend-and-Pretend in the U.S. CRE Market"], "paper_titles": ["Extend-and-Pretend in the U.S. CRE Market"]},
        {"name": "Miguel Faria-e-Castro", "institution": "Federal Reserve Bank of Saint Louis", "role": "Author", "is_presenter": False, "papers": ["Stabilization vs. Growth"], "paper_titles": ["Stabilization vs. Growth"]},
        {"name": "Pascal Paul", "institution": "Federal Reserve Bank of San Francisco", "role": "Presenter", "is_presenter": True, "papers": ["Stabilization vs. Growth"], "paper_titles": ["Stabilization vs. Growth"]},
        {"name": "Juan M. Sánchez", "institution": "Federal Reserve Bank of Saint Louis", "role": "Author", "is_presenter": False, "papers": ["Stabilization vs. Growth"], "paper_titles": ["Stabilization vs. Growth"]},
        {"name": "Rafael Repullo", "institution": "CEMFI and CEPR", "role": "Chair", "is_presenter": False, "papers": [], "paper_titles": []},
        {"name": "Filippo De Marco", "institution": "Bocconi and CEPR", "role": "Author", "is_presenter": False, "papers": ["Mitigating the risks of deregulation: The role of supervisory attention"], "paper_titles": ["Mitigating the risks of deregulation: The role of supervisory attention"]},
        {"name": "Alberto Manconi", "institution": "Bocconi and CEPR", "role": "Presenter", "is_presenter": True, "papers": ["Mitigating the risks of deregulation: The role of supervisory attention"], "paper_titles": ["Mitigating the risks of deregulation: The role of supervisory attention"]},
        {"name": "Isabella Wolfskeil", "institution": "Federal Reserve Board of Governors", "role": "Author", "is_presenter": False, "papers": ["Mitigating the risks of deregulation: The role of supervisory attention"], "paper_titles": ["Mitigating the risks of deregulation: The role of supervisory attention"]},
        {"name": "F. Fiordelisi", "institution": "University of Essex", "role": "Author", "is_presenter": False, "papers": ["Supervisory-Driven Credit Reallocation"], "paper_titles": ["Supervisory-Driven Credit Reallocation"]},
        {"name": "A. Maddaloni", "institution": "European Central Bank", "role": "Presenter", "is_presenter": True, "papers": ["Supervisory-Driven Credit Reallocation"], "paper_titles": ["Supervisory-Driven Credit Reallocation"]},
        {"name": "David Marques Ibanez", "institution": "European Central Bank", "role": "Author", "is_presenter": False, "papers": ["Supervisory-Driven Credit Reallocation"], "paper_titles": ["Supervisory-Driven Credit Reallocation"]},
        {"name": "Manju Puri", "institution": "Duke University (Fuqua School of Business)", "role": "Author", "is_presenter": False, "papers": ["Supervisory-Driven Credit Reallocation"], "paper_titles": ["Supervisory-Driven Credit Reallocation"]},
        {"name": "Francesco Saverio Stentella Lopes", "institution": "University of Roma Tre", "role": "Author", "is_presenter": False, "papers": ["Supervisory-Driven Credit Reallocation"], "paper_titles": ["Supervisory-Driven Credit Reallocation"]},
        {"name": "Alessio De Vincenzo", "institution": "Banca d'Italia", "role": "Chair", "is_presenter": False, "papers": [], "paper_titles": []},
        {"name": "Chi Xu", "institution": "University of Pennsylvania - The Wharton School", "role": "Presenter", "is_presenter": True, "papers": ["The Value of Contingent Liquidity from Banks to Nonbank Lenders"], "paper_titles": ["The Value of Contingent Liquidity from Banks to Nonbank Lenders"]},
        {"name": "Ralf Meisenzhal", "institution": "Federal Reserve Bank of Chicago", "role": "Presenter", "is_presenter": True, "papers": ["Life Insurers' Private Credit Investments and Annuity Market Share Capture"], "paper_titles": ["Life Insurers' Private Credit Investments and Annuity Market Share Capture"]},
        {"name": "Jackson Overpeck", "institution": "Federal Reserve Bank of Chicago", "role": "Author", "is_presenter": False, "papers": ["Life Insurers' Private Credit Investments and Annuity Market Share Capture"], "paper_titles": ["Life Insurers' Private Credit Investments and Annuity Market Share Capture"]},
        {"name": "Andy Polacek", "institution": "Federal Reserve Bank of Chicago", "role": "Author", "is_presenter": False, "papers": ["Life Insurers' Private Credit Investments and Annuity Market Share Capture"], "paper_titles": ["Life Insurers' Private Credit Investments and Annuity Market Share Capture"]}
    ],
    "total_sessions": 6,
    "total_papers": 12,
    "total_participants": 38
}

# Write data.json
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"✅ BFSR data.json written with {len(data['sessions'])} sessions, {len(data['participants'])} participants")
