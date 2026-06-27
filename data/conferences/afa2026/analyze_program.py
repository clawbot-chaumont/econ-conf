#!/usr/bin/env python3
"""Scrape AFA 2026 full program and produce v2 data.json."""
import json, re
from datetime import datetime
from bs4 import BeautifulSoup

DATA_DIR = "/root/economics-conferences"
INPUT = f"{DATA_DIR}/afa2026/full_program_2026.html"

with open(INPUT) as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

sessions = []

# The AFA program uses a table-based layout
# Look for session blocks - they're in <div> elements with specific classes
# Let me search for all tables first
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

# Also look for divs with session info
session_containers = soup.find_all(['div', 'table'], class_=lambda c: c and ('session' in c.lower() or 'program' in c.lower()))
print(f"Found {len(session_containers)} session/program containers")

# Let me extract all text and look for patterns
text = soup.get_text(separator='\n')
lines = [l.strip() for l in text.split('\n') if l.strip()]

# Find session days
days = ['Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
found_days = []
current_day = ""
current_date = ""

# Let me look at the raw structure
# Find all rows in tables
all_rows = soup.find_all('tr')
print(f"Found {len(all_rows)} table rows")

# Find all divs with session-like classes
all_divs = soup.find_all('div', class_=True)
session_divs = []
for d in all_divs:
    classes = ' '.join(d.get('class', []))
    if any(kw in classes.lower() for kw in ['session', 'sessionrow', 'session-title', 'paper', 'program']):
        session_divs.append(d)
print(f"Found {len(session_divs)} session-like divs")

# Let me print the first 50 non-empty lines to understand structure
print("\n=== First 100 significant lines ===")
count = 0
for line in lines:
    if len(line) > 3 and count < 100:
        print(f"  {line[:150]}")
        count += 1
