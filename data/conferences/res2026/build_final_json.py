#!/usr/bin/env python3
"""Build the final clean data.json for RES 2026 conference."""

import json

program = {
    "conference": "RES 2026 Annual Conference (Royal Economic Society)",
    "dates": "6-8 July 2026",
    "venue": "Newcastle University, UK",
    "website": "https://res.org.uk/event-listing/res-2026-annual-conference/",
    "program_url": "https://virtual.oxfordabstracts.com/event/76093/program",
    "source": "Scraped from Oxford Abstracts virtual conference platform via Playwright",
    "scrape_date": "2026-06-11",
    "notes": "The poster gallery and individual paper titles within sessions are in the JS-rendered UI and may require additional interaction to fully expand. The session-level schedule is complete.",
    
    "keynotes": [
        {
            "day": "6 July 2026",
            "time": "10:45-11:00",
            "title": "Welcome to Conference: Professor Imran Rasul, RES Past-President"
        },
        {
            "day": "6 July 2026",
            "time": "11:00-12:00",
            "title": "Presidential Address: Professor Sir Chris Pissarides",
            "speaker": "Christopher Pissarides",
            "affiliation": "Regius Professor of Economics at the London School of Economics",
            "type": "Keynote/Plenary",
            "chair": "Professor Imran Rasul",
            "venue": "Frederick Douglass Centre - Main Lecture Theatre (0.41)"
        },
        {
            "day": "7 July 2026",
            "time": "09:15-10:15",
            "title": "RES Sargan Lecture: Repairing Locally Misspecified GMM: An Empirical Bayes Approach",
            "speaker": "Patrick Kline",
            "affiliation": "Professor of Economics at UC Berkeley, National Bureau of Economic Research",
            "type": "Keynote/Plenary",
            "chair": "Professor Dennis Kristensen",
            "venue": "Frederick Douglass Centre - Main Lecture Theatre (0.41)"
        },
        {
            "day": "7 July 2026",
            "time": "16:15-17:15",
            "title": "The Economic Journal Lecture: Internet and political outcomes",
            "speaker": "Ekaterina Zhuravskaya",
            "affiliation": "Professor of Economics at the Paris School of Economics, EHESS",
            "type": "Keynote/Plenary",
            "chair": "Associate Professor Damian Clarke",
            "venue": "Frederick Douglass Centre - Main Lecture Theatre (0.41)"
        },
        {
            "day": "7 July 2026",
            "time": "17:15-18:15",
            "title": "The challenges and opportunities of leadership in Economics and the wider Economy",
            "speakers": ["Sarah Davidson (Carnegie UK)", "Professor Rachel Griffith (University of Manchester/IFS)", "Catherine L Mann (Bank of England)", "Jo Swaffield (University of Southampton)"],
            "type": "Keynote/Plenary",
            "chair": "Professor Jo Swaffield",
            "venue": "Frederick Douglass Centre - Main Lecture Theatre (0.41)"
        },
        {
            "day": "8 July 2026",
            "time": "09:15-10:15",
            "title": "RES Hahn Lecture: Designing the Social Safety Net",
            "speaker": "Manasi Deshpande",
            "affiliation": "Associate Professor of Economics, University of Chicago, National Bureau of Economic Research",
            "type": "Keynote/Plenary",
            "chair": "Professor Imran Rasul",
            "venue": "Frederick Douglass Centre - Main Lecture Theatre (0.41)"
        },
        {
            "day": "8 July 2026",
            "time": "16:15-17:15",
            "title": "Productivity, Innovation, and the Future of Growth (RES Headline Lecture 2026)",
            "speaker": "John Van Reenen",
            "affiliation": "London School of Economics, Massachusetts Institute for Technology (MIT)",
            "type": "Keynote/Plenary",
            "chair": "Ms Frances Haque",
            "venue": "Frederick Douglass Centre - Main Lecture Theatre (0.41)"
        }
    ],

    "special_sessions": [
        {
            "day": "6 July 2026",
            "time": "14:30-15:45",
            "title": "Special Session 1: How Norms, Transparency, and Infrastructure Shape Economic Behaviour",
            "type": "Special Session"
        },
        {
            "day": "6 July 2026",
            "time": "14:30-15:45",
            "title": "Special Session 2: Global Inequality",
            "type": "Special Session"
        },
        {
            "day": "6 July 2026",
            "time": "14:30-15:45",
            "title": "Special Session 3: Monetary Policy: New Tools in an Evolving Financial Landscape",
            "type": "Special Session"
        },
        {
            "day": "6 July 2026",
            "time": "14:30-15:45",
            "title": "Special Session 4: Pedagogy Review",
            "type": "Special Session"
        },
        {
            "day": "6 July 2026",
            "time": "14:30-15:45",
            "title": "Special Session 5: Transforming Working Lives — Evidence from Two ESRC Projects",
            "type": "Special Session"
        },
        {
            "day": "7 July 2026",
            "time": "10:30-11:45",
            "title": "Special Session 6: Econometrics Journal - Bayesian Econometrics",
            "type": "Special Session"
        },
        {
            "day": "7 July 2026",
            "time": "10:30-11:45",
            "title": "Special Session 7: The growth mission 12 months on: a research hackathon",
            "type": "Special Session"
        },
        {
            "day": "7 July 2026",
            "time": "10:30-11:45",
            "title": "Special Session 8: Behavioural and Experimental Economists UK (BEE-UK): Building a UK-wide Experimental Community",
            "chairs": ["Dr Matteo Gallizzi", "Dr Fabio Tufano"],
            "type": "Special Session"
        },
        {
            "day": "7 July 2026",
            "time": "10:30-11:45",
            "title": "Special Session 9: A Conversation About Diversity: Priorities, Tools and the Economics Pipeline",
            "type": "Special Session"
        },
        {
            "day": "7 July 2026",
            "time": "10:30-11:45",
            "title": "Special Session 10: Economics of Football Regulation",
            "chair": "Dr Luke Garrod",
            "type": "Special Session"
        },
        {
            "day": "8 July 2026",
            "time": "10:30-11:45",
            "title": "Special Session 11: The Economic Journal Special Session — Replicability in Economics – Experiences of Past and Current RES Data Editors",
            "chair": "Associate Professor Damian Clarke",
            "type": "Special Session"
        },
        {
            "day": "8 July 2026",
            "time": "10:30-11:45",
            "title": "Special Session 12: Fiscal sustainability in the UK",
            "chair": "Professor David Miles OBE",
            "type": "Special Session"
        },
        {
            "day": "8 July 2026",
            "time": "10:30-11:45",
            "title": "Special Session 13: The impact of migration on the UK economy",
            "chair": "Dr John Morrow",
            "type": "Special Session"
        },
        {
            "day": "8 July 2026",
            "time": "10:30-11:45",
            "title": "Special Session 14: Expanding possibilities for economic research with linked administrative data",
            "type": "Special Session"
        },
        {
            "day": "8 July 2026",
            "time": "10:30-11:45",
            "title": "Special Session 15: Contributions to the Economics of Creativity. The origin of creatives and creative ideas: peer effects, family background, and the impact of Artificial Intelligence",
            "chair": "Professor Giorgio Fazio",
            "type": "Special Session"
        }
    ],

    "general_sessions": {
        "6 July 2026": {
            "morning_1": {
                "time": "10:00-10:45",
                "events": ["Conference Registration and Coffee (Frederick Douglass Centre - Foyer)"]
            },
            "morning_2": {
                "time": "12:00-12:15",
                "events": ["Move between sessions"]
            },
            "session_1": {
                "time": "12:15-13:30",
                "sessions": [
                    {"code": "G09", "title": "General Economics", "venue": "Frederick Douglass Centre: 1.18"},
                    {"code": "G13", "title": "Labour Economics 1", "venue": "Urban Sciences Building: G.003"},
                    {"code": "G02", "title": "Development Economics 1", "venue": "Frederick Douglass Centre: G.06"},
                    {"code": "S03", "title": "Econometrics (Speed Session)", "venue": "Business School (NUBS) 4.25", "chair": "Professor Mary S. Morgan"},
                    {"code": "S02", "title": "Development (Speed Session)", "venue": "Business School (NUBS) 4.20"},
                    {"code": "G12", "title": "International Economics 1", "venue": "Frederick Douglass Centre: 2.16"},
                    {"code": "G11", "title": "Industrial Organisation 1", "venue": "Frederick Douglass Centre: 1.16"},
                    {"code": "G10", "title": "Health, Education, and Welfare 1", "venue": "Frederick Douglass Centre: 1.17"},
                    {"code": "S01", "title": "Behavioural / Experimental / Culture (Speed Session)", "venue": "Business School (NUBS): 4.06"},
                    {"code": "G03", "title": "Development Economics: Macro / Growth 1", "venue": "Boardroom 3.41 (3rd floor) FDC Building"},
                    {"code": "G14", "title": "Macroeconomics 1", "venue": "Frederick Douglass Centre: 2.14"},
                    {"code": "G05", "title": "Economic History", "venue": "Frederick Douglass Centre: G.56"},
                    {"code": "G04", "title": "Econometrics 1", "venue": "Business School (NUBS): 2.03"},
                    {"code": "G06", "title": "Economic Theory 1", "venue": "Frederick Douglass Centre: 1.15"},
                    {"code": "G07", "title": "Environmental Economics 1", "venue": "Frederick Douglass Centre: G.07"},
                    {"code": "G01", "title": "Behavioural / Experimental Economics 1", "venue": "Urban Sciences Building: G.002"},
                    {"code": "G08", "title": "Finance 1", "venue": "Urban Sciences Building: G.004"},
                    {"extra": "CHUDE Meeting (invitation only)", "venue": "Frederick Douglass Centre: 2.14", "time": "12:15-13:45"}
                ]
            },
            "lunch": {
                "time": "13:30-14:30",
                "events": ["Lunch and Exhibition"]
            },
            "special_sessions_block": {
                "time": "14:30-15:45",
                "events": ["5 Special Sessions running concurrently"]
            },
            "afternoon_break": {
                "time": "15:45-16:15",
                "events": ["PhD Student Networking Break", "Coffee & Exhibition"]
            },
            "session_2": {
                "time": "16:15-17:30",
                "sessions": [
                    {"code": "G25", "title": "Labour Economics 2", "venue": "Frederick Douglass Centre: 1.18"},
                    {"code": "G26", "title": "Macroeconomics 2", "venue": "Urban Sciences Building: G.003"},
                    {"code": "G16", "title": "Development Economics 2"},
                    {"code": "G18", "title": "Econometrics 2"},
                    {"code": "G19", "title": "Economic Theory 2"},
                    {"code": "G20", "title": "Environmental Economics 2"},
                    {"code": "G21", "title": "Finance 2"},
                    {"code": "G22", "title": "Health, Education, and Welfare 2"},
                    {"code": "G23", "title": "Industrial Organisation 2"},
                    {"code": "G24", "title": "International Economics 2"},
                    {"code": "S04", "title": "Economic Theory (Speed Session)"},
                    {"code": "G27", "title": "Macroeconomics: Inflation and Macro Finance"},
                    {"code": "G17", "title": "Development Economics: Macro / Growth 2"},
                    {"code": "G28", "title": "Political Economy 1"},
                    {"code": "S05", "title": "Finance (Speed Session)"},
                    {"code": "S06", "title": "Health (Speed Session)"},
                    {"code": "G15", "title": "Behavioural / Experimental Economics 2"}
                ]
            },
            "evening": {
                "time": "17:30-17:45",
                "events": ["Move"]
            },
            "evening_session": {
                "time": "17:45-18:30",
                "title": "Trusted, Accessible and Connected? The Future of UK Economic Data",
                "speakers": ["James Benford (Office for National Statistics)", "Dr Tanya Wilson (University of Glasgow)", "Catherine L Mann (Bank of England)"],
                "chair": "Dr Catherine L Mann",
                "venue": "Frederick Douglass Centre - Main Lecture Theatre (0.41)"
            },
            "reception": {
                "time": "18:30-20:00",
                "title": "Welcome Reception & Poster Presentations",
                "venue": "Urban Sciences Building",
                "type": "Poster Session"
            }
        },

        "7 July 2026": {
            "morning": {
                "time": "08:15-09:15",
                "title": "Masterclass: Using Storytelling Techniques to Bring Data to Life, delivered by MSB Executive",
                "speaker": "Martyn Barmby (MSB Executive)",
                "venue": "Frederick Douglass Centre: 1.17"
            },
            "registration": {
                "time": "08:45-09:15",
                "events": ["Conference Registration and Coffee (Frederick Douglass Centre - Foyer)"]
            },
            "session_1": {
                "time": "12:15-13:30",
                "sessions": [
                    {"code": "G33", "title": "Financial Economics 1"},
                    {"code": "S08", "title": "International Economics (Speed Session)"},
                    {"code": "G32", "title": "Economic Theory 3"},
                    {"code": "G37", "title": "Labour Economics 3"},
                    {"code": "G39", "title": "Labour Economics: Wages and job search"},
                    {"code": "G38", "title": "Labour Economics: Macro"},
                    {"code": "G41", "title": "Macroeconomics: Business Cycles"},
                    {"code": "G42", "title": "Political Economy 2"},
                    {"code": "G29", "title": "Behavioural / Experimental Economics 3"},
                    {"code": "G30", "title": "Development Economics 3"},
                    {"code": "G34", "title": "Health, Education, and Welfare 3"},
                    {"code": "G31", "title": "Development Economics: Gender 1"},
                    {"code": "G35", "title": "Industrial Organisation 3"},
                    {"code": "G40", "title": "Macroeconomics 3"},
                    {"code": "S09", "title": "Labour Economics (Speed Session)"},
                    {"code": "G36", "title": "International Economics 3"},
                    {"code": "S07", "title": "Industrial Organisation / Public Economics (Speed Session)"}
                ]
            },
            "lunch": {
                "time": "11:45-12:15",
                "events": ["Move and Lunch"]
            },
            "session_2": {
                "time": "14:30-15:45",
                "sessions": [
                    {"code": "G46", "title": "Financial Economics 2"},
                    {"code": "G54", "title": "Political Economy 3"},
                    {"code": "G53", "title": "Macroeconomics: Fiscal Policy and Heterogenous Agents"},
                    {"code": "G52", "title": "Macroeconomics and Monetary Economics 1"},
                    {"code": "G51", "title": "Macroeconomics 4"},
                    {"code": "G49", "title": "Labour Economics 4"},
                    {"code": "G48", "title": "Industrial Organisation 4"},
                    {"code": "G50", "title": "Labour Economics: Migration"},
                    {"code": "G47", "title": "Health, Education, and Welfare 4"},
                    {"code": "G45", "title": "Development Economics: Gender 2"},
                    {"code": "G43", "title": "Behavioural / Experimental Economics 4"},
                    {"code": "G56", "title": "Urban, Rural, Regional, Real Estate 1"},
                    {"code": "S10", "title": "Macroeconomics (Speed Session)"},
                    {"code": "S11", "title": "Political Economics / Law (Speed Session)"},
                    {"code": "G55", "title": "Public Economics 1"},
                    {"code": "G44", "title": "Development Economics 4"},
                    {"code": "S12", "title": "Public Economics (Speed Session)"}
                ]
            },
            "afternoon_break": {
                "time": "15:45-16:15",
                "events": ["Coffee & Exhibition"]
            },
            "gala": {
                "time": "19:00-22:30",
                "title": "Gala Dinner and Awards Evening",
                "venue": "Newcastle Civic Centre"
            }
        },

        "8 July 2026": {
            "morning_run": {
                "time": "07:30-08:30",
                "title": "Run Club! 5k around the city with Jonah Patton, captain of Newcastle University Athletics and Cross Country club"
            },
            "registration": {
                "time": "08:45-09:15",
                "events": ["Conference Registration and Coffee (Frederick Douglass Centre - Foyer)"]
            },
            "session_1": {
                "time": "12:15-13:30",
                "sessions": [
                    {"code": "G58", "title": "Development Economics 5"},
                    {"code": "G57", "title": "Behavioural / Experimental Economics 5"},
                    {"code": "G68", "title": "Political Economy: Voting and Institutions"},
                    {"code": "G66", "title": "Public Economics: Pensions and Savings"},
                    {"code": "S13", "title": "Development 2 (Speed Session)"},
                    {"code": "G65", "title": "Macroeconomics and Monetary Economics 2"},
                    {"code": "G70", "title": "Public Economics: Education"},
                    {"code": "G69", "title": "Public Economics 2"},
                    {"code": "G64", "title": "Labour Economics: Gender"},
                    {"code": "G61", "title": "Financial Economics 3"},
                    {"code": "G60", "title": "Economic Development 1"},
                    {"code": "G59", "title": "Development Economics: Political Economy 1"},
                    {"code": "S14", "title": "Financial Economics (Speed Session)"},
                    {"code": "G63", "title": "Labour Economics: Family and Household Economics 1"},
                    {"code": "G67", "title": "Macroeconomics: Growth"},
                    {"code": "G62", "title": "Labour Economics 5"}
                ]
            },
            "lunch": {
                "time": "11:45-12:15",
                "events": ["Move and Lunch"]
            },
            "session_2": {
                "time": "14:30-15:45",
                "sessions": [
                    {"code": "G75", "title": "Labour Economics: Income Distribution, Inequality and Labour Supply"},
                    {"code": "G77", "title": "Law and Economics"},
                    {"code": "G71", "title": "Development Economics: Political Economy 2"},
                    {"code": "S15", "title": "Labour Economics 2 (Speed Session)"},
                    {"code": "G82", "title": "Effort, Subsidies, Beliefs and AI"},
                    {"code": "G81", "title": "Public Economics: Health"},
                    {"code": "G79", "title": "Macroeconomics and Monetary Economics 3"},
                    {"code": "G76", "title": "Labour Economics, Returns to Education, Unemployment and Gender"},
                    {"code": "G74", "title": "Labour Economics: Programme Evaluation"},
                    {"code": "S16", "title": "Macroeconomics 2 (Speed Session)"},
                    {"code": "G78", "title": "Macroeconomics and Monetary Economics: Monetary Policy, Central Banking, and the Supply of Money and Credit"},
                    {"code": "G80", "title": "Microeconomics"},
                    {"code": "G72", "title": "Economic Development 2"},
                    {"code": "G73", "title": "Labour Economics: Family and Household Economics 2"},
                    {"code": "G83", "title": "Political Economics: Institutions and Lobbying"},
                    {"code": "G84", "title": "Urban, Rural, Regional, Real Estate 2"}
                ]
            },
            "afternoon_break": {
                "time": "15:45-16:15",
                "events": ["Coffee & Exhibition"]
            },
            "evening": {
                "time": "17:15-18:15",
                "title": "Networking Drinks Reception with John Van Reenen (sponsored by Kingston University)",
                "venue": "Frederick Douglass Centre - Foyer"
            }
        }
    },

    "streams": [
        "G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08", "G09", "G10",
        "G11", "G12", "G13", "G14", "G15", "G16", "G17", "G18", "G19", "G20",
        "G21", "G22", "G23", "G24", "G25", "G26", "G27", "G28", "G29", "G30",
        "G31", "G32", "G33", "G34", "G35", "G36", "G37", "G38", "G39", "G40",
        "G41", "G42", "G43", "G44", "G45", "G46", "G47", "G48", "G49", "G50",
        "G51", "G52", "G53", "G54", "G55", "G56", "G57", "G58", "G59", "G60",
        "G61", "G62", "G63", "G64", "G65", "G66", "G67", "G68", "G69", "G70",
        "G71", "G72", "G73", "G74", "G75", "G76", "G77", "G78", "G79", "G80",
        "G81", "G82", "G83", "G84",
        "S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10",
        "S11", "S12", "S13", "S14", "S15", "S16"
    ]
}

with open("/root/economics-conferences/res2026/data.json", "w") as f:
    json.dump(program, f, indent=2)

print(f"Written to /root/economics-conferences/res2026/data.json")
print(f"Total keynote entries: {len(program['keynotes'])}")
print(f"Total special sessions: {len(program['special_sessions'])}")
print(f"Total days with general sessions: {len(program['general_sessions'])}")
print(f"Total streams: {len(program['streams'])}")
