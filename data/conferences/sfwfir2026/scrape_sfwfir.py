#!/usr/bin/env python3
"""Scrape SFWFIR 2026 from PDF program."""
import json, re, os
from datetime import datetime

PDF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "program.pdf")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# Extract text from PDF
import subprocess
result = subprocess.run(["pdftotext", PDF_PATH, "-"], capture_output=True, text=True)
text = result.stdout

# Parse sessions
# Structure: Session N followed by presenter lines
session_pattern = r"Session (\d+)\s*\n(.*?)(?=\nSession \d+|$)"
sessions_raw = re.findall(session_pattern, text, re.DOTALL)

sessions = []
participant_data = {}

for sess_num, sess_text in sessions_raw:
    sess_num = int(sess_num)
    
    # Find time for this session
    time_match = re.search(r"(\d+:\d+\s*[-–]\s*\d+:\d+)", sess_text)
    session_time = time_match.group(1) if time_match else ""
    
    # Map session number to date based on PDF structure
    if sess_num <= 2:
        session_date = "2026-06-04"
    elif sess_num <= 5:
        session_date = "2026-06-05"
    else:
        session_date = "2026-06-05"  # Session 6 is also Friday
    
    # Find day from text
    if "THURSDAY" in sess_text.upper():
        session_date = "2026-06-04"
    if "FRIDAY" in sess_text.upper():
        session_date = "2026-06-05"
    
    # Extract papers from this session
    # Each paper: PRESENTER (INSTITUTION) on one line, then 'Paper Title' on next
    paper_pattern = r'([A-Z][A-Z\s.]+(?:\s\([^)]+\)))\s*\n\s*[‘\']([^’\']+)[’\']\s*(?:\(with\s*([^)]*)\))?'
    
    papers = []
    # More robust: find lines with presenter in ALL CAPS with institution in parens
    for pm in re.finditer(r'([A-Z][A-Z\s.]+(?:\s\([^)]+\)))\s*\n', sess_text):
        presenter_line = pm.group(1).strip()
        
        # Get text after this match until next presenter or session end
        start = pm.end()
        remaining = sess_text[start:]
        
        # Find next presenter line (all caps + institution) or end
        next_p = re.search(r'[A-Z][A-Z\s.]+(?:\s\([^)]+\))\s*\n', remaining)
        paper_block = remaining[:next_p.start()] if next_p else remaining
        
        # Extract title - find single-quoted string
        title_match = re.search(r'[‘\']([^’\']+)[’\']', paper_block)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        
        # Extract co-authors from "with..." pattern
        coauthors = []
        with_match = re.search(r'\(with\s*(.*?)\)', paper_block)
        if with_match:
            raw = with_match.group(1)
            # Split by "and" or ","
            parts = re.split(r',\s+(?:\band\b\s+)?', raw)
            for part in parts:
                part = part.strip().strip(',').strip()
                if part:
                    # Remove leading "and "
                    part = re.sub(r'^and\s+', '', part).strip()
                    if part:
                        coauthors.append(part)
        
        # Parse presenter name and institution
        pres_match = re.match(r'([A-Z\s.]+?)\s*\((.+?)\)', presenter_line)
        if pres_match:
            presenter = pres_match.group(1).strip().title()
            institution = pres_match.group(2).strip()
        else:
            presenter = presenter_line.strip().title()
            institution = ""
        
        # Extract discussant
        disc_match = re.search(r'Discussant:\s*([A-Za-z\s.]+?)\s*\((.+?)\)', paper_block)
        discussant = ""
        if disc_match:
            discussant = f"{disc_match.group(1).strip()} ({disc_match.group(2).strip()})"
        
        # All authors: presenter + co-authors
        all_authors = [presenter] + coauthors
        
        papers.append({
            "title": title,
            "authors": all_authors,
            "presenter": presenter,
            "discussant": discussant,
        })
        
        # Add participants
        for name in all_authors:
            name_clean = name.strip()
            if name_clean and name_clean not in participant_data:
                participant_data[name_clean] = {
                    "name": name_clean,
                    "institution": institution if name_clean == presenter else "",
                    "is_presenter": name_clean == presenter,
                    "papers": [title],
                }
            elif name_clean in participant_data:
                if title not in participant_data[name_clean]["papers"]:
                    participant_data[name_clean]["papers"].append(title)
    
    if papers:
        sessions.append({
            "session_title": f"Session {sess_num}",
            "date": session_date,
            "time": session_time,
            "papers": [{"title": p["title"], "authors": p["authors"], "presenter": p["presenter"]} for p in papers],
        })

# Now let me also try a more direct parsing approach since the PDF text is clean
# Session times
time_map = {
    1: "14:30 - 16:00",
    2: "16:30 - 18:00",
    3: "09:30 - 11:00",
    4: "11:30 - 13:00",
    5: "14:30 - 16:00",
    6: "16:30 - 18:00",
}

# Direct parsing from the text I saw
all_papers_data = [
    # (session, date, time, presenter, institution, title, coauthors, discussant)
    (1, "2026-06-04", "14:30 - 16:00", "Paolo Fulghieri", "UNC Kenan-Flagler Business School",
     "Multilateral Contracting in Stage Financing", ["Yunzhi Hu", "Felipe Varas"],
     "Vincent Maurin (HEC Paris)"),
    (1, "2026-06-04", "14:30 - 16:00", "Nicole Fleskes", "Rice University",
     "Regulation and Intermediation in Over-the-Counter Markets", [],
     "Ziang Li (Imperial College London)"),
    (2, "2026-06-04", "16:30 - 18:00", "Mete Kilic", "USC Marshall",
     "The Fed Put and Bank Risk-Taking: Evidence from the Loan Book",
     ["Xudong An", "Jan Harren", "Saket Hegde", "Rodney Ramcharan"],
     "Sebastian Doerr (Bank for International Settlements)"),
    (2, "2026-06-04", "16:30 - 18:00", "Christian Eufinger", "IESE Business School",
     "Common Lenders and Borrower Return Comovement",
     ["Luca Lin", "Valentina Raponi", "Haorui Wang"],
     "Alex Osberghaus (Swiss Finance Institute)"),
    (3, "2026-06-05", "09:30 - 11:00", "Sitong Ding", "London School of Economics",
     "Who Moves the Long End? The Dynamics of Bond Market Segmentation",
     ["Robert Czech"],
     "Egemen Eren (Bank for International Settlements)"),
    (3, "2026-06-05", "09:30 - 11:00", "Nicola Limodio", "Bocconi University",
     "Household Portfolio and Deposit Insurance: implications for the Supply of Safe Assets",
     ["Pulak Ghosh", "Nishant Vats"],
     "Virginia Gianinazzi (Nova School of Business and Economics)"),
    (4, "2026-06-05", "11:30 - 13:00", "Antonio Coppola", "Stanford Graduate School of Business",
     "Financial Regulation and AI: A Faustian Bargain?", ["Christopher Clayton"],
     "Ansgar Walther (Oxford Saïd Business School)"),
    (4, "2026-06-05", "11:30 - 13:00", "Jing Zhou", "IMF",
     "Liquidity Support Effects of the U.S. Treasury Buyback Program", [],
     "Felix Corell (VU Amsterdam)"),
    (5, "2026-06-05", "14:30 - 16:00", "Deniz Aydin", "MIT",
     "Uniform Pricing and Capital Allocation", ["Ernest Liu", "Janis Skrastins"],
     "Kim Fe Cramer (London School of Economics)"),
    (5, "2026-06-05", "14:30 - 16:00", "Piero Gottardi", "University of Essex",
     "Bills of Exchange in a Supply Chain", ["Shengxing Zhang"],
     "Sergio Vicente (University of Luxembourg)"),
    # THE MISSING SESSION 6!
    (6, "2026-06-05", "16:30 - 18:00", "Paulina Verhoff", "Frankfurt School of Finance & Management",
     "Do Institutional Investors Trade on Covenant Violations?",
     ["Anthony Saunders", "Sascha Steffen"],
     "Ralf Meisenzahl (Federal Reserve Bank of Chicago)"),
    (6, "2026-06-05", "16:30 - 18:00", "Jamie Coen", "Imperial College London",
     "Whose Asset Sales Matter?", ["Rhys Bidder", "Caterina Lepore", "Laura Silvestri"],
     "Nicholas Hirschey (Nova School of Business and Economics)"),
]

# Build output
v2_sessions = []
participants = {}

current_session = None
sess_data = {}

for sess, date, time, pres, inst, title, coauthors, disc in all_papers_data:
    if sess != current_session:
        if current_session is not None:
            v2_sessions.append(sess_data)
        current_session = sess
        sess_data = {
            "session_title": f"Session {sess}",
            "date": date,
            "time": time,
            "papers": [],
        }
    
    all_authors = [pres] + coauthors
    sess_data["papers"].append({
        "title": title,
        "authors": all_authors,
        "presenter": pres,
    })
    
    for name in all_authors:
        if name not in participants:
            participants[name] = {"name": name, "institution": inst if name == pres else "", "is_presenter": name == pres, "papers": [title]}
        else:
            if title not in participants[name]["papers"]:
                participants[name]["papers"].append(title)

# Don't forget the last session
if sess_data:
    v2_sessions.append(sess_data)

# Add organizers
for name, inst in [("Fred Malherbe", "UCL and CEPR"), ("Björn Richter", "Nova SBE, UPF and BSE"), ("Gabriela Stockler", "UPF and BSE")]:
    if name not in participants:
        participants[name] = {"name": name, "institution": inst, "is_presenter": False, "papers": []}

output = {
    "conference": {
        "name": "BSE Summer Forum Workshop on Financial Intermediation and Risk",
        "short_name": "SFWFIR",
        "year": 2026,
        "start_date": "2026-06-04",
        "end_date": "2026-06-05",
        "location": "Barcelona, Spain",
    },
    "scrape_metadata": {
        "scraped_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "source_url": "https://events.bse.eu/live/files/6394-sf2026-program-financial-intermediation-and-risk",
        "program_available": True,
        "program_type": "pdf",
        "errors": [],
    },
    "sessions": v2_sessions,
    "participants": sorted(participants.values(), key=lambda x: x["name"]),
}

print(f"Sessions: {len(v2_sessions)}")
for s in v2_sessions:
    print(f"  {s['session_title']} ({s.get('time','')}): {len(s['papers'])} papers")
    for p in s['papers']:
        print(f"    {p['title'][:60]:60s} | {', '.join(p['authors'])[:50]}")
print(f"\nParticipants: {len(output['participants'])}")
has_inst = sum(1 for p in output["participants"] if p.get("institution","").strip())
print(f"With institution: {has_inst}")

with open(OUTPUT_PATH, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {OUTPUT_PATH}")
