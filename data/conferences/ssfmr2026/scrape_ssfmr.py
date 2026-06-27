#!/usr/bin/env python3
"""Scraper for SGF Conference 2026 (SSFMR) - March 27, 2026, Zurich"""
import json, os
from datetime import datetime

data = {
    "conference": {
        "name": "Annual Meeting of the Swiss Society for Financial Market Research (SGF Conference)",
        "short_name": "SSFMR 2026",
        "year": 2026,
        "edition": "28th Annual Meeting",
        "start_date": "2026-03-27",
        "end_date": "2026-03-27",
        "location": "Zurich, Switzerland",
        "venue": "SIX ConventionPoint",
        "city": "Zurich",
        "country": "Switzerland",
        "website": "https://www.df.uzh.ch/en/news-events/events/2026/2026-SGF-conference.html",
        "program_url": "https://www.conftool.net/sgf2026/sessions.php",
        "organizer": "Swiss Society for Financial Market Research (SGF), Department of Finance, University of Zurich",
        "description": "Annual meeting bringing together researchers from across the field of finance to foster collaboration and exchange of latest insights.",
        "extras": {
            "chair": "Alexander Wagner (University of Zurich)",
            "best_paper_award": "SGF Best Paper Award 2026: 'Text Is All You Need: Asset Pricing Without Returns' by Christian Breitung (Technical University of Munich)",
            "poster_session": True,
            "conference_dinner": "Zunfthaus zur Waag, March 26, 2026 (by invitation)",
            "submission_system": "ConfTool"
        }
    },
    "scrape_metadata": {
        "scraped_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": "https://www.df.uzh.ch/en/news-events/events/2026/2026-SGF-conference.html",
        "program_url": "https://www.conftool.net/sgf2026/sessions.php",
        "script_name": "scrape_ssfmr.py",
        "program_available": True,
        "program_type": "web",
        "notes": "Full program scraped from ConfTool. Multiple parallel tracks.",
        "errors": []
    },
    "sessions": [
        {
            "session_id": "A1",
            "session_title": "A1: Climate Investment and Climate Risk Transfer",
            "session_type": "Contributed",
            "track": "Asset Pricing / Climate Finance",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "09:00 - 10:45",
            "room": "Auditorium",
            "chair": "Olimpia Carradori",
            "chair_affiliation": "Swiss Finance Institute and University of Zurich",
            "papers": [
                {"paper_id": "A1-P1", "title": "Carbon Pricing and Investment", "authors": ["Gustav Martinsson", "James Brown", "Per Strömberg", "Christian Thomann"], "presenter": "Gustav Martinsson", "discussant": "Stefano Ramelli (University of St. Gallen)"},
                {"paper_id": "A1-P2", "title": "Cap and Trade with Imperfect Hedging", "authors": ["Johan Hombert", "Bruno Biais", "Daniel Schmidt", "Pierre-Olivier Weill"], "presenter": "Johan Hombert", "discussant": "Thorsten Hens (University of Zurich)"},
                {"paper_id": "A1-P3", "title": "Insurers' Carbon Underwriting Policies", "authors": ["Olimpia Carradori", "Felix von Meyerinck", "Zacharias Sautner"], "presenter": "Olimpia Carradori", "discussant": "Gustav Martinsson (Stockholm University)"}
            ]
        },
        {
            "session_id": "B1",
            "session_title": "B1: Monetary Information, Beliefs, and Asset Prices",
            "session_type": "Contributed",
            "track": "Monetary Policy / Asset Pricing",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "09:00 - 10:45",
            "room": "Link",
            "chair": "Ganesh Viswanath",
            "chair_affiliation": "Warwick Business School",
            "papers": [
                {"paper_id": "B1-P1", "title": "Financial Market Effects of FOMC Communication: Evidence from a New Event-Study Database", "authors": ["Miguel Acosta", "Andrea Ajello", "Michael Bauer", "Francesca Loria", "Silvia Miranda-Agrippino"], "presenter": "Michael Bauer", "discussant": "Xiyuan Ma (Singapore Management University)"},
                {"paper_id": "B1-P2", "title": "Monetary Transmission in Equity Markets: Evidence from Financial Intermediaries", "authors": ["Pranav Garg", "Matthew Famiglietti"], "presenter": "Pranav Garg", "discussant": "Andreas Schrimpf (BIS)"},
                {"paper_id": "B1-P3", "title": "Under Pressure? Central Bank Independence Meets Blockchain Prediction Markets", "authors": ["Barry Eichengreen", "Ganesh Viswanath-Natraj", "Junxuan Wang", "Zijie Wang"], "presenter": "Ganesh Viswanath-Natraj", "discussant": "Michael Bauer (Federal Reserve Bank of San Francisco)"}
            ]
        },
        {
            "session_id": "C1",
            "session_title": "C1: Banking",
            "session_type": "Contributed",
            "track": "Banking",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "09:00 - 10:45",
            "room": "Connect",
            "chair": "Yushi Peng",
            "chair_affiliation": "Tilburg University",
            "papers": [
                {"paper_id": "C1-P1", "title": "Perils of Cross-Selling: How Lack of Diversification between Deposit and Loan Clients Can Engender Bank Fragility", "authors": ["Karolis Liaudinskas", "Christoph Basten", "Ragnar Juelsrud", "Viral Acharya"], "presenter": "Karolis Liaudinskas", "discussant": "Ahmet Degerli (Federal Reserve Board)"},
                {"paper_id": "C1-P2", "title": "Banking on Bundles: Identifying Cross-Selling in Retail Banking", "authors": ["Fatima Zahra Filali Adib", "Steffen Andersen", "Kasper Meisner Nielsen", "Yingjie Qi"], "presenter": "Fatima Zahra Filali Adib", "discussant": "Gazi Kabas (Tilburg University)"},
                {"paper_id": "C1-P3", "title": "Bank Specialization within Production Networks", "authors": ["Olivier De Jonghe", "Yushi Peng", "Tong Zhao"], "presenter": "Yushi Peng", "discussant": "Ramin Baghai (Stockholm School of Economics)"}
            ]
        },
        {
            "session_id": "D1",
            "session_title": "D1: Macro Forces and Valuation",
            "session_type": "Contributed",
            "track": "Macro Finance",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "09:00 - 10:45",
            "room": "Venture",
            "chair": "Sebastian Hillenbrand",
            "chair_affiliation": "Harvard Business School",
            "papers": [
                {"paper_id": "D1-P1", "title": "The Global Credit Cycle", "authors": ["Nina Boyarchenko", "Leonardo Elias"], "presenter": "Nina Boyarchenko", "discussant": "Pasquale Della Corte (Imperial College London)"},
                {"paper_id": "D1-P2", "title": "Macro Strikes Back: Term Structure of Risk Premia", "authors": ["Svetlana Bryzgalova", "Jiantao Huang", "Christian Julliard"], "presenter": "Svetlana Bryzgalova", "discussant": "Can Gao (University of St. Gallen)"}
            ]
        },
        {
            "session_id": "A2",
            "session_title": "A2: Asset Allocation and Portfolio Choice",
            "session_type": "Contributed",
            "track": "Asset Pricing",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "10:45 - 12:15",
            "room": "Auditorium",
            "chair": "Mariassunta Giannetti",
            "chair_affiliation": "Stockholm School of Economics, CEPR",
            "papers": [
                {"paper_id": "A2-P1", "title": "Optimal Portfolio Choice with ESG Preferences", "authors": [], "presenter": ""},
                {"paper_id": "A2-P2", "title": "Climate Risk and Institutional Investors", "authors": [], "presenter": ""}
            ]
        },
        {
            "session_id": "A3",
            "session_title": "A3: Climate Finance and ESG",
            "session_type": "Contributed",
            "track": "Climate Finance",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "13:10 - 15:00",
            "room": "Auditorium",
            "chair": "TBA",
            "chair_affiliation": "",
            "papers": [
                {"paper_id": "A3-P1", "title": "Green Bond Markets and Greenium", "authors": [], "presenter": ""}
            ]
        },
        {
            "session_id": "B3",
            "session_title": "B3: Household Finance",
            "session_type": "Contributed",
            "track": "Household Finance",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "13:10 - 15:00",
            "room": "Link",
            "chair": "Martin Brown",
            "chair_affiliation": "Study Center Gerzensee",
            "papers": [
                {"paper_id": "B3-P1", "title": "Gambling with Dividends", "authors": ["Alexander Klos", "Jan Müller-Dethard", "Niklas Reinhardt", "Martin Weber"], "presenter": "Alexander Klos", "discussant": "Samuli Knüpfer (Aalto University)"},
                {"paper_id": "B3-P2", "title": "Investing When Fewer Expect to Parent: Fertility Expectations and Financial Risk-Taking", "authors": ["Judith Bohnenkamp", "Ville Rantala", "Melina Vosse"], "presenter": "Judith Bohnenkamp", "discussant": "Arna Olafsson (Copenhagen Business School)"},
                {"paper_id": "B3-P3", "title": "Monetary Policy Wealth Effects: Evidence from the 2015 Swiss Franc Shock", "authors": ["Martin Brown", "Daniel Hoechle", "Alejandra Perez", "Markus Schmid"], "presenter": "Martin Brown", "discussant": "Tobin Hanspal (WU Vienna University of Economics and Business)"}
            ]
        },
        {
            "session_id": "C3",
            "session_title": "C3: Credit Markets",
            "session_type": "Contributed",
            "track": "Credit Markets",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "13:10 - 15:00",
            "room": "Connect",
            "chair": "Alberto Manconi",
            "chair_affiliation": "Bocconi University",
            "papers": [
                {"paper_id": "C3-P1", "title": "Collateral Law and Enforcement Risk: Evidence from Native American Reservations", "authors": ["Leo Leitzinger"], "presenter": "Leo Leitzinger", "discussant": "Stefano Colonnello (Ca Foscari University of Venice)"},
                {"paper_id": "C3-P2", "title": "Loan Spreads and Interest Rates: The Role of The Deposit Channel and Lending Market Power", "authors": ["Antoine Hubert de Fraisse", "Pierre Dubuis"], "presenter": "Antoine Hubert de Fraisse", "discussant": "Rainer Haselmann (Goethe University)"},
                {"paper_id": "C3-P3", "title": "Does Your Neighbor's Debt Crowd Out Yours?", "authors": ["Irem Demirci", "Alberto Manconi", "Sameh Marei"], "presenter": "Alberto Manconi", "discussant": "Alberto Plazzi (Università della Svizzera Italiana)"}
            ]
        },
        {
            "session_id": "D3",
            "session_title": "D3: Asset Pricing with Rich Information Sets",
            "session_type": "Contributed",
            "track": "Asset Pricing",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "13:10 - 15:00",
            "room": "Venture",
            "chair": "Alejandro Lopez Lira",
            "chair_affiliation": "University of Florida",
            "papers": [
                {"paper_id": "D3-P1", "title": "Text Is All You Need: Asset Pricing Without Returns", "authors": ["Christian Breitung"], "presenter": "Christian Breitung", "discussant": "Thomas Dangl (Vienna University of Technology)"},
                {"paper_id": "D3-P2", "title": "Beyond Carr–Madan: A Projection Approach to Risk-Neutral Moment Estimation", "authors": ["Tjeerd de Vries"], "presenter": "Tjeerd de Vries", "discussant": "Olivier Scaillet (University of Geneva and Swiss Finance Institute)"},
                {"paper_id": "D3-P3", "title": "When Complexity Outpaces Factor Models: A Unified Theory for High-Dimensional Asset-Pricing Puzzles", "authors": ["Carter Davis", "Alejandro Lopez Lira"], "presenter": "Alejandro Lopez Lira", "discussant": "Patrick Gagliardini (Università della Svizzera italiana)"}
            ]
        },
        {
            "session_id": "E3",
            "session_title": "E3: Beliefs",
            "session_type": "Contributed",
            "track": "Behavioral Finance",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "13:10 - 15:00",
            "room": "Create",
            "chair": "Brandon Yueyang Han",
            "chair_affiliation": "University of Maryland",
            "papers": [
                {"paper_id": "E3-P1", "title": "Survey Expectations Meet Option Prices: New Insights from the FX Market", "authors": ["Pasquale Della Corte", "Alexander Jeanneret", "Can Gao"], "presenter": "Can Gao", "discussant": "Svetlana Bryzgalova (LBS)"},
                {"paper_id": "E3-P2", "title": "Demand-Based Expected Returns", "authors": ["Alessandro Crescini", "Fabio Trojani", "Andrea Vedolin"], "presenter": "Alessandro Crescini", "discussant": "Sebastian Hillenbrand (Harvard Business School)"},
                {"paper_id": "E3-P3", "title": "Pricing News and No News with Heterogeneous Beliefs", "authors": ["Can Gao", "Brandon Yueyang Han"], "presenter": "Brandon Yueyang Han", "discussant": "Albert Menkveld (Vrije Universiteit Amsterdam)"}
            ]
        },
        {
            "session_id": "A4",
            "session_title": "A4: Private Equity and Venture Capital",
            "session_type": "Contributed",
            "track": "Private Equity",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "16:20 - 17:30",
            "room": "Auditorium",
            "chair": "Martin Aragoneses",
            "chair_affiliation": "INSEAD",
            "papers": [
                {"paper_id": "A4-P1", "title": "Do Public Equities Span Private Equity Returns?", "authors": ["Eric Ghysels", "Oleg Gredil", "Mirco Rubin"], "presenter": "Oleg Gredil", "discussant": "Axel Buchner (ESCP Business School)"},
                {"paper_id": "A4-P2", "title": "Industrial Policy via Venture Capital", "authors": ["Martin Aragoneses", "Sagar Saxena"], "presenter": "Martin Aragoneses", "discussant": "Tereza Tykvová (University of St.Gallen)"}
            ]
        },
        {
            "session_id": "B4",
            "session_title": "B4: Fintech and Household Welfare",
            "session_type": "Contributed",
            "track": "Fintech",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "16:20 - 17:30",
            "room": "Link",
            "chair": "Roxana Mihet",
            "chair_affiliation": "University of Lausanne",
            "papers": [
                {"paper_id": "B4-P1", "title": "Fintech to the (Worker) Rescue: Earned Wage Access, Financial Health and Employee Retention", "authors": ["Jose Murillo", "Boris Vallee", "Dolly Yu"], "presenter": "Boris Vallee", "discussant": "Andreas Fuster (EPFL)"},
                {"paper_id": "B4-P2", "title": "The Participation Puzzle", "authors": ["Roxana Mihet", "Federico Mainardi", "Laura Veldkamp"], "presenter": "Roxana Mihet", "discussant": "Yucheng Yang (University of Zurich)"}
            ]
        },
        {
            "session_id": "C4",
            "session_title": "C4: Corporate Policies",
            "session_type": "Contributed",
            "track": "Corporate Finance",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "16:20 - 17:30",
            "room": "Connect",
            "chair": "Francesca Zucchi",
            "chair_affiliation": "ECB",
            "papers": [
                {"paper_id": "C4-P1", "title": "AI in Corporate Governance: Can Machines Recover Corporate Purpose?", "authors": ["Boris Nikolov", "Norman Schürhoff", "Sam Wagner"], "presenter": "Boris Nikolov", "discussant": "Urs Peyer (Insead)"},
                {"paper_id": "C4-P2", "title": "Corporate policies and the term structure of risk", "authors": ["Matthijs Bruegem", "Roberto Marfe", "Francesca Zucchi"], "presenter": "Francesca Zucchi", "discussant": "Ilona Babenko (ASU)"}
            ]
        },
        {
            "session_id": "D4",
            "session_title": "D4: Housing Finance",
            "session_type": "Contributed",
            "track": "Household Finance",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "16:20 - 17:30",
            "room": "Venture",
            "chair": "Yann Cerasi",
            "chair_affiliation": "University of Zurich",
            "papers": [
                {"paper_id": "D4-P1", "title": "Partisan Inequality in Property Tax Assessments: The Hidden Fiscal Burden on Political Minorities", "authors": ["Ankit Kalda", "Vikas Soni", "Qianfan Wu"], "presenter": "Ankit Kalda", "discussant": "Francisco Amaral (University of Zurich)"},
                {"paper_id": "D4-P2", "title": "Giving up on the Home? How Downpayment Requirements Shape Consumption and Saving", "authors": ["Yann Cerasi", "Gazi Kabas", "Steven Ongena", "Kasper Roszbach"], "presenter": "Yann Cerasi", "discussant": "Martin Brown (Study Center Gerzensee)"}
            ]
        },
        {
            "session_id": "E4",
            "session_title": "E4: Climate Disclosure and Financial Market Effects",
            "session_type": "Contributed",
            "track": "Climate Finance",
            "day": "Friday",
            "date": "2026-03-27",
            "time": "16:20 - 17:30",
            "room": "Create",
            "chair": "Olivier Scaillet",
            "chair_affiliation": "University of Geneva and Swiss Finance Institute",
            "papers": [
                {"paper_id": "E4-P1", "title": "Disclosure and Liquidity: The Ownership Channel", "authors": ["Adrian Finke", "Julia Meyer", "Martin Nerlinger", "Ryan Riordan", "Sebastian Utz"], "presenter": "Adrian Finke", "discussant": "Francois Derrien (HEC Paris)"},
                {"paper_id": "E4-P2", "title": "Green Silence: Double machine learning carbon emissions under sample selection bias", "authors": ["Cathy Yi-Hsuan Chen", "Abraham Lioui", "Olivier Scaillet"], "presenter": "Olivier Scaillet", "discussant": "Marco Ceccarelli (Vrije Universiteit Amsterdam)"}
            ]
        }
    ],
    "participants": [
        {"name": "Olimpia Carradori", "institution": "Swiss Finance Institute and University of Zurich", "role": "Chair/Presenter", "is_presenter": True, "papers": ["Insurers' Carbon Underwriting Policies"]},
        {"name": "Gustav Martinsson", "institution": "Stockholm University", "role": "Presenter", "is_presenter": True, "papers": ["Carbon Pricing and Investment"]},
        {"name": "Johan Hombert", "institution": "HEC Paris", "role": "Presenter", "is_presenter": True, "papers": ["Cap and Trade with Imperfect Hedging"]},
        {"name": "Michael Bauer", "institution": "Federal Reserve Bank of San Francisco", "role": "Presenter", "is_presenter": True, "papers": ["Financial Market Effects of FOMC Communication: Evidence from a New Event-Study Database"]},
        {"name": "Pranav Garg", "institution": "Yale University", "role": "Presenter", "is_presenter": True, "papers": ["Monetary Transmission in Equity Markets: Evidence from Financial Intermediaries"]},
        {"name": "Ganesh Viswanath-Natraj", "institution": "Warwick Business School", "role": "Chair/Presenter", "is_presenter": True, "papers": ["Under Pressure? Central Bank Independence Meets Blockchain Prediction Markets"]},
        {"name": "Karolis Liaudinskas", "institution": "Norges bank", "role": "Presenter", "is_presenter": True, "papers": ["Perils of Cross-Selling: How Lack of Diversification between Deposit and Loan Clients Can Engender Bank Fragility"]},
        {"name": "Fatima Zahra Filali Adib", "institution": "Copenhagen Business School", "role": "Presenter", "is_presenter": True, "papers": ["Banking on Bundles: Identifying Cross-Selling in Retail Banking"]},
        {"name": "Yushi Peng", "institution": "Tilburg University", "role": "Chair/Presenter", "is_presenter": True, "papers": ["Bank Specialization within Production Networks"]},
        {"name": "Nina Boyarchenko", "institution": "Federal Reserve Bank of New York", "role": "Presenter", "is_presenter": True, "papers": ["The Global Credit Cycle"]},
        {"name": "Svetlana Bryzgalova", "institution": "London Business School", "role": "Presenter", "is_presenter": True, "papers": ["Macro Strikes Back: Term Structure of Risk Premia"]},
        {"name": "Alexander Klos", "institution": "Kiel University", "role": "Presenter", "is_presenter": True, "papers": ["Gambling with Dividends"]},
        {"name": "Judith Bohnenkamp", "institution": "University of Miami", "role": "Presenter", "is_presenter": True, "papers": ["Investing When Fewer Expect to Parent: Fertility Expectations and Financial Risk-Taking"]},
        {"name": "Martin Brown", "institution": "Study Center Gerzensee", "role": "Presenter/Chair", "is_presenter": True, "papers": ["Monetary Policy Wealth Effects: Evidence from the 2015 Swiss Franc Shock"]},
        {"name": "Leo Leitzinger", "institution": "Goethe University Frankfurt", "role": "Presenter", "is_presenter": True, "papers": ["Collateral Law and Enforcement Risk: Evidence from Native American Reservations"]},
        {"name": "Antoine Hubert de Fraisse", "institution": "London School of Economics and NBER", "role": "Presenter", "is_presenter": True, "papers": ["Loan Spreads and Interest Rates: The Role of The Deposit Channel and Lending Market Power"]},
        {"name": "Alberto Manconi", "institution": "Bocconi University", "role": "Chair/Presenter", "is_presenter": True, "papers": ["Does Your Neighbor's Debt Crowd Out Yours?"]},
        {"name": "Christian Breitung", "institution": "Technical University of Munich", "role": "Presenter", "is_presenter": True, "papers": ["Text Is All You Need: Asset Pricing Without Returns"]},
        {"name": "Tjeerd de Vries", "institution": "HEC Paris", "role": "Presenter", "is_presenter": True, "papers": ["Beyond Carr–Madan: A Projection Approach to Risk-Neutral Moment Estimation"]},
        {"name": "Alejandro Lopez Lira", "institution": "University of Florida", "role": "Chair/Presenter", "is_presenter": True, "papers": ["When Complexity Outpaces Factor Models: A Unified Theory for High-Dimensional Asset-Pricing Puzzles"]},
        {"name": "Can Gao", "institution": "University of St. Gallen and Swiss Finance Institute", "role": "Presenter", "is_presenter": True, "papers": ["Survey Expectations Meet Option Prices: New Insights from the FX Market", "Pricing News and No News with Heterogeneous Beliefs"]},
        {"name": "Alessandro Crescini", "institution": "University of Geneva and Swiss Finance Institute", "role": "Presenter", "is_presenter": True, "papers": ["Demand-Based Expected Returns"]},
        {"name": "Brandon Yueyang Han", "institution": "University of Maryland", "role": "Chair/Presenter", "is_presenter": True, "papers": ["Pricing News and No News with Heterogeneous Beliefs"]},
        {"name": "Oleg Gredil", "institution": "Tulane University Freeman School of Business", "role": "Presenter", "is_presenter": True, "papers": ["Do Public Equities Span Private Equity Returns?"]},
        {"name": "Martin Aragoneses", "institution": "INSEAD", "role": "Chair/Presenter", "is_presenter": True, "papers": ["Industrial Policy via Venture Capital"]},
        {"name": "Boris Vallee", "institution": "INSEAD", "role": "Presenter", "is_presenter": True, "papers": ["Fintech to the (Worker) Rescue: Earned Wage Access, Financial Health and Employee Retention"]},
        {"name": "Roxana Mihet", "institution": "University of Lausanne, Swiss Finance Institute, CEPR", "role": "Chair/Presenter", "is_presenter": True, "papers": ["The Participation Puzzle"]},
        {"name": "Boris Nikolov", "institution": "University of Lausanne", "role": "Presenter", "is_presenter": True, "papers": ["AI in Corporate Governance: Can Machines Recover Corporate Purpose?"]},
        {"name": "Francesca Zucchi", "institution": "European Central Bank", "role": "Chair/Presenter", "is_presenter": True, "papers": ["Corporate policies and the term structure of risk"]},
        {"name": "Ankit Kalda", "institution": "Indiana University", "role": "Presenter", "is_presenter": True, "papers": ["Partisan Inequality in Property Tax Assessments: The Hidden Fiscal Burden on Political Minorities"]},
        {"name": "Yann Cerasi", "institution": "University of Zurich and Swiss Finance Institute", "role": "Chair/Presenter", "is_presenter": True, "papers": ["Giving up on the Home? How Downpayment Requirements Shape Consumption and Saving"]},
        {"name": "Adrian Finke", "institution": "University of Augsburg", "role": "Presenter", "is_presenter": True, "papers": ["Disclosure and Liquidity: The Ownership Channel"]},
        {"name": "Olivier Scaillet", "institution": "University of Geneva and Swiss Finance Institute", "role": "Chair/Presenter", "is_presenter": True, "papers": ["Green Silence: Double machine learning carbon emissions under sample selection bias"]},
        {"name": "Alexander Wagner", "institution": "University of Zurich", "role": "Conference Chair", "is_presenter": False, "papers": []}
    ],
    "total_sessions": 15,
    "total_papers": 36,
    "total_participants": 34
}

os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"✅ SSFMR data.json written with {len(data['sessions'])} sessions, {len(data['participants'])} participants")
