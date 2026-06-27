#!/usr/bin/env python3
"""
Parse the MoFiR 2026 program PDF text into structured JSON (v2 schema).
Outputs correct field names directly.
"""
import json
import re
from datetime import datetime

# Read the raw text
with open('raw_text.txt', 'r') as f:
    lines = [l.rstrip('\n') for l in f.readlines()]

text = '\n'.join(lines)

sessions = []
all_participants = []
participant_names = set()

def add_participant(name, institution, role='author'):
    """Add participant if not already present."""
    key = (name.strip(), institution.strip())
    if key not in participant_names:
        participant_names.add(key)
        all_participants.append({
            'name': name.strip(),
            'institution': institution.strip(),
            'role': role
        })

def make_author(name, institution):
    """Create an author dict with institution string."""
    return {'name': name.strip(), 'institution': institution.strip()}

# ---------- MONDAY 6 JULY ----------

# Session 1 | Geopolitics and financial interconnections (14:00-15:00)
s1 = {
    'session_title': 'Geopolitics and financial interconnections',
    'day': 'Monday 6 July',
    'time': '14:00-15:00',
    'chair': None,
    'papers': [
        {
            'title': 'The Pricing of Geopolitical Tensions over a Century',
            'authors': [make_author('Alessandro Melone', 'Ohio State University')],
            'discussant': None
        },
        {
            'title': 'CBDCs, Payment Firms, and Geopolitics',
            'authors': [make_author('Jan Keil', 'Humboldt University of Berlin')],
            'discussant': None
        }
    ]
}
add_participant('Alessandro Melone', 'Ohio State University', 'author')
add_participant('Jan Keil', 'Humboldt University of Berlin', 'author')
sessions.append(s1)

# Session 2 | Conflicts and banks (15:00-16:00)
s2 = {
    'session_title': 'Conflicts and banks',
    'day': 'Monday 6 July',
    'time': '15:00-16:00',
    'chair': None,
    'papers': [
        {
            'title': 'A Geopolitical Shock to Bank Assets and Monetary Policy Transmission',
            'authors': [make_author('Björn Imbierowicz', 'Deutsche Bundesbank')],
            'discussant': None
        },
        {
            'title': 'Violent Conflict and Cross-Border Lending',
            'authors': [make_author('Ralph De Haas', 'EBRD')],
            'discussant': None
        }
    ]
}
add_participant('Björn Imbierowicz', 'Deutsche Bundesbank', 'author')
add_participant('Ralph De Haas', 'EBRD', 'author')
sessions.append(s2)

# Policy and Industry Panel (16:30-18:00)
panel = {
    'session_title': 'Policy and Industry Panel: Geopolitical Risks and the Financial Sector',
    'day': 'Monday 6 July',
    'time': '16:30-18:00',
    'chair': None,
    'papers': [
        {
            'title': 'Panel Discussion',
            'authors': [
                make_author('Stephan Fahr', 'European Central Bank'),
                make_author('Andrea Presbitero', 'International Monetary Fund and CEPR'),
                make_author('Davide Alfonsi', 'Intesa Sanpaolo'),
                make_author('Aurelio Maccario', 'UniCredit')
            ],
            'discussant': None
        }
    ]
}
add_participant('Stephan Fahr', 'European Central Bank', 'panelist')
add_participant('Andrea Presbitero', 'International Monetary Fund and CEPR', 'panelist')
add_participant('Davide Alfonsi', 'Intesa Sanpaolo', 'panelist')
add_participant('Aurelio Maccario', 'UniCredit', 'panelist')
sessions.append(panel)

# ---------- TUESDAY 7 JULY ----------

# Session 1 | Mortgage Market (09:00-10:40)
s3 = {
    'session_title': 'Mortgage Market',
    'day': 'Tuesday 7 July',
    'time': '09:00-10:40',
    'chair': None,
    'papers': [
        {
            'title': 'Inflation Through the Mortgage Market',
            'authors': [make_author('Arpit Gupta', 'New York University Stern School of Business')],
            'discussant': make_author('Pedro Gete', 'IE University')
        },
        {
            'title': 'Interest Rate Pass-Through With Adjustable Rate Mortgages',
            'authors': [make_author('Miguel Ferreira', 'Nova School of Business')],
            'discussant': make_author('Giulio Cornelli', 'BIS')
        }
    ]
}
add_participant('Arpit Gupta', 'New York University Stern School of Business', 'author')
add_participant('Miguel Ferreira', 'Nova School of Business', 'author')
add_participant('Pedro Gete', 'IE University', 'discussant')
add_participant('Giulio Cornelli', 'BIS', 'discussant')
sessions.append(s3)

# Keynote lecture
keynote = {
    'session_title': 'Keynote Lecture',
    'day': 'Tuesday 7 July',
    'time': '11:00-12:30',
    'chair': None,
    'papers': [
        {
            'title': 'Keynote Address',
            'authors': [make_author('Steven Ongena', 'University of Zurich')],
            'discussant': None
        }
    ]
}
add_participant('Steven Ongena', 'University of Zurich', 'keynote speaker')
sessions.append(keynote)

# Session 2 | Networks and Shock Transmission (13:30-15:10)
s4 = {
    'session_title': 'Networks and Shock Transmission',
    'day': 'Tuesday 7 July',
    'time': '13:30-15:10',
    'chair': None,
    'papers': [
        {
            'title': 'Bank Specialization within Production Networks',
            'authors': [make_author('Yushi Peng', 'Tilburg University')],
            'discussant': make_author('David Martizez Miera', 'Universidad Carlos III de Madrid')
        },
        {
            'title': 'Banks, Firms, and Households: Credit Shock Amplification and Real Effects',
            'authors': [make_author('Cédric Huylebroek', 'KU Leuven')],
            'discussant': make_author('Roman Goncharenko', 'Central Bank of Ireland')
        }
    ]
}
add_participant('Yushi Peng', 'Tilburg University', 'author')
add_participant('Cédric Huylebroek', 'KU Leuven', 'author')
add_participant('David Martizez Miera', 'Universidad Carlos III de Madrid', 'discussant')
add_participant('Roman Goncharenko', 'Central Bank of Ireland', 'discussant')
sessions.append(s4)

# Session 3 | (no title) (15:30-17:30)
s5 = {
    'session_title': 'Session 3',
    'day': 'Tuesday 7 July',
    'time': '15:30-17:30',
    'chair': None,
    'papers': [
        {
            'title': 'Common Investors Across the Capital Structure: Private Debt Funds as Dual Holders',
            'authors': [make_author('Tatyana Marchuk', 'Nova School of Business & Economics, CEPR')],
            'discussant': None
        },
        {
            'title': 'The Interoperability of Financial Data',
            'authors': [make_author('Elif Cansu Akoguz', 'KU Leuven')],
            'discussant': make_author('Ben Charoenwong', 'Insead')
        },
        {
            'title': 'Quantitative Tightening: The Bank Liquidity-Duration Nexus',
            'authors': [make_author('Alba Patozi', 'Bank of England')],
            'discussant': make_author('Raoul Minetti', 'MSU')
        }
    ]
}
add_participant('Tatyana Marchuk', 'Nova School of Business & Economics, CEPR', 'author')
add_participant('Elif Cansu Akoguz', 'KU Leuven', 'author')
add_participant('Alba Patozi', 'Bank of England', 'author')
add_participant('Ben Charoenwong', 'Insead', 'discussant')
add_participant('Raoul Minetti', 'MSU', 'discussant')
sessions.append(s5)

# ---------- WEDNESDAY 8 JULY ----------

# Session 1 | PhD Student Presentations (09:00-10:00)
s6 = {
    'session_title': 'PhD Student Presentations',
    'day': 'Wednesday 8 July',
    'time': '09:00-10:00',
    'chair': {'name': 'Alberto Zazzaro', 'institution': 'University of Naples Federico II'},
    'papers': [
        {
            'title': 'Green or Brown, Small or Big? How Nonbanks Reshape Monetary Transmission and Credit Allocation',
            'authors': [make_author('Francesco Febbraro', 'University of Groningen')],
            'discussant': None
        },
        {
            'title': 'Political Shifts, Mortgage Drifts: Evidence from U.S. Special Elections',
            'authors': [make_author('Ioannis Moustakis', 'University of Southern California')],
            'discussant': None
        },
        {
            'title': 'Tight Capital, Loose Money: How Stress-Tested Banks Responded to Quantitative Easing',
            'authors': [make_author('Chiara Vergeat', 'London Business School')],
            'discussant': None
        },
        {
            'title': 'Down Payments, Deferred Homes: How LTV Restrictions Reshape Household Consumption',
            'authors': [make_author('Yann Cerasi', 'University of Zurich')],
            'discussant': None
        },
        {
            'title': 'Pioneering Unbanked Markets: The Catalytic Role of a Public Commercial Bank',
            'authors': [make_author('Roberto Melis', 'University of Agder')],
            'discussant': None
        }
    ]
}
add_participant('Alberto Zazzaro', 'University of Naples Federico II', 'chair')
add_participant('Francesco Febbraro', 'University of Groningen', 'author')
add_participant('Ioannis Moustakis', 'University of Southern California', 'author')
add_participant('Chiara Vergeat', 'London Business School', 'author')
add_participant('Yann Cerasi', 'University of Zurich', 'author')
add_participant('Roberto Melis', 'University of Agder', 'author')
sessions.append(s6)

# Session 2 | Bank Funding (10:20-12:00)
s7 = {
    'session_title': 'Bank Funding',
    'day': 'Wednesday 8 July',
    'time': '10:20-12:00',
    'chair': None,
    'papers': [
        {
            'title': 'Large Depositors, Retail Depositors, and the Deposits Channel of Monetary Policy',
            'authors': [make_author('Yevhenii Usenko', 'MIT Sloan')],
            'discussant': make_author('Christopher Basten', 'European Central Bank')
        },
        {
            'title': 'Wholesale Funding Crises since 1800',
            'authors': [make_author('Rustam Jamilov', 'University of Oxford')],
            'discussant': None
        }
    ]
}
add_participant('Yevhenii Usenko', 'MIT Sloan', 'author')
add_participant('Rustam Jamilov', 'University of Oxford', 'author')
add_participant('Christopher Basten', 'European Central Bank', 'discussant')
sessions.append(s7)

# Session 6 | (no title) (13:00-14:40) — note: labeled Session 6 in program
s8 = {
    'session_title': 'Session 6',
    'day': 'Wednesday 8 July',
    'time': '13:00-14:40',
    'chair': None,
    'papers': [
        {
            'title': 'Competing for Loan Informal Seniority: Theory and Evidence',
            'authors': [make_author('Bernardo Ricca', 'Insper')],
            'discussant': make_author('Nicola Limodio', 'Bocconi University')
        },
        {
            'title': 'Debt Flexibility',
            'authors': [make_author('Rhys Bidder', "King's Business School")],
            'discussant': None
        }
    ]
}
add_participant('Bernardo Ricca', 'Insper', 'author')
add_participant('Rhys Bidder', "King's Business School", 'author')
add_participant('Nicola Limodio', 'Bocconi University', 'discussant')
sessions.append(s8)

# Also add organizers as participants
organizers = [
    {'name': 'Andrea Bellucci', 'institution': "Università degli Studi dell'Insubria", 'role': 'organizer'},
    {'name': 'Serena Fatica', 'institution': 'European Commission', 'role': 'organizer'},
    {'name': 'Rossella Locatelli', "institution": "Università degli Studi dell'Insubria", 'role': 'organizer'},
    {'name': 'Andrea Presbitero', 'institution': 'International Monetary Fund and CEPR', 'role': 'organizer'},
    {'name': 'Alberto Zazzaro', 'institution': 'University of Naples Federico II', 'role': 'organizer'}
]
for o in organizers:
    key = (o['name'], o['institution'])
    if key not in participant_names:
        participant_names.add(key)
        all_participants.append(o)

# Count total papers
total_papers = sum(len(s['papers']) for s in sessions)
total_participants = len(all_participants)

now_iso = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

data = {
    'conference': {
        'name': 'MoFiR 2026 - 15th MoFiR Workshop on Banking',
        'short_name': 'MOFIR',
        'year': 2026,
        'start_date': '2026-07-06',
        'end_date': '2026-07-08',
        'location': "Università degli Studi dell'Insubria, Varese, Italy",
        'extras': {
            'dates': '6-8 July 2026',
            'venue': "Università degli Studi dell'Insubria, Varese",
            'organizers': ['Andrea Bellucci', 'Serena Fatica', 'Rossella Locatelli', 'Andrea Presbitero', 'Alberto Zazzaro'],
            'url': 'https://cepr.org/events/15th-mofir-workshop-banking'
        }
    },
    'scrape_metadata': {
        'scraped_at': now_iso,
        'source_url': 'https://cepr.org/events/15th-mofir-workshop-banking',
        'program_available': True,
        'program_type': 'pdf',
        'errors': []
    },
    'sessions': sessions,
    'participants': all_participants
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Done! Total papers: {total_papers}, Total participants: {total_participants}")
print(f"Sessions: {len(sessions)}")
for s in sessions:
    print(f"  {s['day']} | {s['time']} | {s['session_title']} ({len(s['papers'])} paper(s))")

# Validate
print("\n=== VALIDATION ===")
errors = []
for i, s in enumerate(sessions):
    if not s.get('session_title'):
        errors.append(f"Session {i}: session_title is empty!")
    if 'papers' not in s:
        errors.append(f"Session {i}: papers key missing!")
    for j, p in enumerate(s.get('papers', [])):
        for a in p.get('authors', []):
            if 'institution' not in a or not a['institution']:
                errors.append(f"Session {i}, paper {j}, author '{a.get('name', '?')}': missing institution!")
if errors:
    print("ERRORS:")
    for e in errors:
        print(f"  - {e}")
else:
    print("All validations passed! ✓")
