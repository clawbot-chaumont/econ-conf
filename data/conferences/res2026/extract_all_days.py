#!/usr/bin/env python3
"""Extract full RES 2026 program for all 3 days from Oxford Abstracts - fixed."""

import asyncio
import json
import re
from playwright.async_api import async_playwright

TARGET_URL = "https://virtual.oxfordabstracts.com/event/76093/program"
OUTPUT_PATH = "/root/economics-conferences/res2026/data.json"


async def extract_all_days():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        print(f"Loading {TARGET_URL}...")
        await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(5)

        all_day_texts = {}

        # Get all day tab texts by evaluating JS directly
        day_tabs_info = await page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('button');
            const dayTabs = [];
            buttons.forEach(b => {
                const text = b.textContent.trim();
                if (text.match(/Mon|Tue|Wed/i) && text.match(/\\d/)) {
                    const rect = b.getBoundingClientRect();
                    dayTabs.push({text, x: rect.x, y: rect.y, width: rect.width, height: rect.height});
                }
            });
            return dayTabs;
        }
        """)
        print(f"Day tabs found: {[t['text'] for t in day_tabs_info]}")

        # If no day tabs found via buttons, try other elements
        if not day_tabs_info:
            day_tabs_info = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                const tabs = [];
                all.forEach(el => {
                    const text = el.textContent.trim();
                    if ((text === 'Mon' || text === 'Tue' || text === 'Wed') && el.children.length === 0) {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            tabs.push({text, x: rect.x, y: rect.y});
                        }
                    }
                    if ((text === '6' || text === '7' || text === '8') && el.children.length === 0) {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            tabs.push({text: 'Num-'+text, x: rect.x, y: rect.y});
                        }
                    }
                });
                return tabs;
            }
            """)
            print(f"Alternative elements: {day_tabs_info[:10]}")

        # The day buttons were found as "Mon6", "Tue7", "Wed8" earlier
        # Let me try clicking by text content
        day_labels = ["Mon6", "Tue7", "Wed8"]
        day_names = {0: "monday", 1: "tuesday", 2: "wednesday"}
        
        for idx, label in enumerate(day_labels):
            day_name = day_names[idx]
            print(f"\n--- Clicking {label} ({day_name}) ---")
            
            try:
                clicked = await page.evaluate(f"""
                () => {{
                    const buttons = document.querySelectorAll('button');
                    for (const b of buttons) {{
                        if (b.textContent.trim() === '{label}') {{
                            b.click();
                            return true;
                        }}
                    }}
                    // Try partial match
                    for (const b of buttons) {{
                        if (b.textContent.trim().includes('{label[:3]}') && b.textContent.trim().includes('{label[3:]}')) {{
                            b.click();
                            return 'partial:' + b.textContent.trim();
                        }}
                    }}
                    return false;
                }}
                """)
                print(f"  Click result: {clicked}")
                await asyncio.sleep(3)
                
                # Scroll to load content
                for _ in range(8):
                    await page.evaluate("window.scrollBy(0, 600)")
                    await asyncio.sleep(0.5)
                await asyncio.sleep(2)
                
                text = await page.evaluate("() => document.body.innerText")
                all_day_texts[f"{day_name}_expanded"] = text
                print(f"  Text length: {len(text)}")
                
            except Exception as e:
                print(f"  Error: {e}")

        await browser.close()

    # If we didn't get all 3 days, try a fallback - reload and try harder
    if len(all_day_texts) < 3:
        print("\n--- Fallback: reloading and trying again ---")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()
            await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)
            
            # Try clicking different selectors
            selectors = [
                "button:has-text(\"Mon6\")",
                "button:has-text(\"Tue7\")", 
                "button:has-text(\"Wed8\")",
                "text=Mon6 >> visible=true",
                "text=Tue7 >> visible=true",
                "text=Wed8 >> visible=true"
            ]
            
            for day_idx, label in enumerate(["Mon6", "Tue7", "Wed8"]):
                day_name = ["monday", "tuesday", "wednesday"][day_idx]
                if day_name + "_expanded" in all_day_texts:
                    continue
                    
                try:
                    el = page.locator(f"text={label}").first
                    if await el.is_visible():
                        await el.click()
                        await asyncio.sleep(3)
                        for _ in range(5):
                            await page.evaluate("window.scrollBy(0, 400)")
                            await asyncio.sleep(0.3)
                        await asyncio.sleep(2)
                        text = await page.evaluate("() => document.body.innerText")
                        all_day_texts[f"{day_name}_expanded"] = text
                        print(f"  Fallback: got {label} text ({len(text)} chars)")
                except Exception as e:
                    print(f"  Fallback error for {label}: {e}")
            
            await browser.close()

    # Extract all text
    all_program_text = ""
    for day_name in ["monday", "tuesday", "wednesday"]:
        text = all_day_texts.get(f"{day_name}_expanded", "")
        all_program_text += f"\n\n=== {day_name.upper()} ===\n\n{text}"

    # Save raw text
    with open("/root/economics-conferences/res2026/all_days_text.txt", "w") as f:
        f.write(all_program_text)

    # Parse program
    program = parse_program(all_day_texts)
    
    with open(OUTPUT_PATH, "w") as f:
        json.dump(program, f, indent=2, default=str)

    print(f"\n=== SUMMARY ===")
    print(f"Days captured: {list(all_day_texts.keys())}")
    
    for s in program.get("sessions", []):
        print(f"  {s.get('day', '?')} | {s.get('time', '?')} | {s.get('title', '?')}")
    for s in program.get("keynotes", []):
        print(f"  KEYNOTE: {s.get('day', '?')} | {s.get('time', '?')} | {s.get('title', '?')}")
    for s in program.get("special_sessions", []):
        print(f"  SPECIAL: {s.get('day', '?')} | {s.get('time', '?')} | {s.get('title', '?')}")
    
    return program


def parse_program(all_day_texts):
    program = {
        "conference": "RES 2026 Annual Conference (Royal Economic Society)",
        "dates": "6-8 July 2026",
        "venue": "Newcastle University, UK (Frederick Douglass Centre, Urban Sciences Building, Business School)",
        "website": "https://res.org.uk/event-listing/res-2026-annual-conference/",
        "program_url": "https://virtual.oxfordabstracts.com/event/76093/program",
        "day_tabs": ["Mon 6", "Tue 7", "Wed 8"],
        "sessions": [],
        "keynotes": [],
        "special_sessions": [],
        "other_events": [],
        "streams": []
    }

    day_map = {
        "monday_expanded": "6 July 2026",
        "tuesday_expanded": "7 July 2026",
        "wednesday_expanded": "8 July 2026"
    }

    seen_sessions = set()
    
    for key, text in all_day_texts.items():
        date_label = day_map.get(key, key)
        lines = text.split('\n')
        
        i = 0
        current_session = None
        session_lines = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Detect time ranges
            time_range_match = re.match(r'^(\d{2}:\d{2})-(\d{2}:\d{2})$', line)
            
            if time_range_match:
                # Save previous session
                if session_lines and current_session:
                    parsed = parse_session_block(session_lines, date_label, current_session)
                    if parsed and parsed.get('title'):
                        sig = f"{parsed['day']}|{parsed['time']}|{parsed['title']}"
                        if sig not in seen_sessions:
                            seen_sessions.add(sig)
                            cat = classify_session(parsed['title'])
                            program[cat].append(parsed)
                
                current_session = {
                    "day": date_label,
                    "time": line,
                    "start_time": time_range_match.group(1),
                    "end_time": time_range_match.group(2),
                    "title": "",
                    "venue": "",
                    "session_type": "",
                    "chair": "",
                    "presentations": []
                }
                session_lines = [line]
            elif current_session:
                session_lines.append(line)
            
            i += 1
        
        # Last session
        if session_lines and current_session:
            parsed = parse_session_block(session_lines, date_label, current_session)
            if parsed and parsed.get('title'):
                sig = f"{parsed['day']}|{parsed['time']}|{parsed['title']}"
                if sig not in seen_sessions:
                    seen_sessions.add(sig)
                    cat = classify_session(parsed['title'])
                    program[cat].append(parsed)

    # Extract stream info
    stream_set = set()
    for s in program["sessions"] + program["keynotes"] + program["special_sessions"] + program["other_events"]:
        title = s.get("title", "")
        m = re.match(r'(G\d+|S\d+):\s*(.+)', title)
        if m:
            stream_set.add(m.group(1))
    
    program["streams"] = sorted(list(stream_set))
    
    return program


def classify_session(title):
    t = title.lower()
    if any(w in t for w in ["keynote", "presidential address", "headline lecture"]):
        return "keynotes"
    if "special session" in t:
        return "special_sessions"
    if any(w in t for w in ["registration", "coffee", "lunch", "welcome reception", 
                             "poster", "move", "networking", "exhibition", "chude"]):
        return "other_events"
    return "sessions"


def parse_session_block(lines, date_label, session):
    time_str = lines[0] if lines else ""
    
    content_lines = [l for l in lines[1:] if l.strip() and l.strip() not in 
                     ["Add to calendar", "Bookmark session"]]
    
    venue = ""
    title = ""
    session_type = ""
    chair = ""
    papers = []
    
    for line in content_lines:
        if line in ["Move", "Lunch and Exhibition", "Coffee & Exhibition",
                     "PhD Student Networking Break", "Welcome Reception & Poster Presentations",
                     "Conference Registration and Coffee"]:
            if not title:
                title = line
            continue
        
        if re.match(r'^\d+$', line):
            continue
        
        if line.startswith("Presentation type:"):
            session_type = line.replace("Presentation type:", "").strip()
            continue
        
        if line.startswith("Chair:"):
            chair = line.replace("Chair:", "").strip()
            continue
        
        if any(term in line for term in ["Frederick Douglass Centre", "Urban Sciences Building",
                                           "Business School", "Boardroom", "FDC Building", "FDC"]):
            venue = line
            continue
        
        if line in ["Invited speaker", "Invited"]:
            continue
        
        if not title:
            title = line
    
    session["title"] = title or session.get("title", "")
    session["venue"] = venue
    session["session_type"] = session_type
    session["chair"] = chair
    
    return session


if __name__ == "__main__":
    result = asyncio.run(extract_all_days())
