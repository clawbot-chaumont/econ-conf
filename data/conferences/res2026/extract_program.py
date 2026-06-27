#!/usr/bin/env python3
"""Extract the full RES 2026 Annual Conference program from Oxford Abstracts."""

import asyncio
import json
import re
from playwright.async_api import async_playwright

TARGET_URL = "https://virtual.oxfordabstracts.com/event/76093/program"
OUTPUT_PATH = "/root/economics-conferences/res2026/data.json"


async def extract_full_program():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        print(f"Navigating to {TARGET_URL}...")
        await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(5)

        # Get the full rendered text content
        body_text = await page.evaluate("() => document.body.innerText")
        
        # Also get the HTML to find structured elements
        html = await page.content()

        # Try to extract structured data via DOM queries
        sessions = await page.evaluate("""
        () => {
            const results = [];
            // Look for session cards/entries - they may have various structures
            const allElements = document.querySelectorAll('*');
            const textContents = new Set();
            
            // Find elements that contain session info - look for date headers and time blocks
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, [role="heading"]');
            const headingTexts = [];
            headings.forEach(h => {
                const text = h.textContent.trim();
                if (text) headingTexts.push(text);
            });
            
            return { headingTexts };
        }
        """)

        print(f"Heading texts: {json.dumps(sessions.get('headingTexts', []), indent=2)[:2000]}")

        # The data seems to be in the text content - let's parse it more carefully
        # First, save the full text
        with open("/root/economics-conferences/res2026/full_program_text.txt", "w") as f:
            f.write(body_text)

        print(f"\nFull body text length: {len(body_text)}")
        
        # Try clicking on different days to get all sessions
        # First, let's see what day buttons exist
        day_buttons = await page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('button, [role="tab"]');
            const dayButtons = [];
            buttons.forEach(b => {
                const text = b.textContent.trim();
                if (text.match(/mon|tue|wed|\\d+\\s+july|6\\s|7\\s|8\\s/i)) {
                    dayButtons.push(text);
                }
            });
            return dayButtons;
        }
        """)
        print(f"Day buttons found: {day_buttons}")

        # Try clicking on Day 2 (Tuesday) and Day 3 (Wednesday) to load their content
        for day_idx, day_label in enumerate([("Tue", "7"), ("Wed", "8")]):
            try:
                # Look for the day tab/button
                day_btn = page.locator(f'button:has-text("{day_label[0]}")').first()
                if await day_btn.is_visible():
                    await day_btn.click()
                    await asyncio.sleep(3)
                    day_text = await page.evaluate("() => document.body.innerText")
                    with open(f"/root/economics-conferences/res2026/full_program_text_day{day_idx+2}.txt", "w") as f:
                        f.write(day_text)
                    print(f"Day {day_label[0]} text saved ({len(day_text)} chars)")
            except Exception as e:
                print(f"Error clicking day {day_label}: {e}")

        # Switch back to Mon view and try to click on sessions to expand them
        try:
            mon_btn = page.locator('button:has-text("Mon")').first()
            if await mon_btn.is_visible():
                await mon_btn.click()
                await asyncio.sleep(2)
        except:
            pass

        # Click on all expandable session items to reveal paper details
        clickable_items = await page.evaluate("""
        () => {
            // Find items that look like they expand on click
            const items = document.querySelectorAll('[role="button"], .cursor-pointer, [class*="expand"], [class*="accordion"]');
            return items.length;
        }
        """)
        print(f"Potentially clickable items: {clickable_items}")

        # Try clicking elements that contain session titles
        # Look for elements with time patterns
        time_elements = await page.evaluate("""
        () => {
            const allElements = document.querySelectorAll('*');
            const timeElements = [];
            const timeRegex = /^\\d{2}:\\d{2}/;
            allElements.forEach(el => {
                if (el.children.length === 0 || el.children.length === 1) {
                    const text = el.textContent.trim();
                    if (timeRegex.test(text) && text.length < 20) {
                        timeElements.push(text);
                    }
                }
            });
            return [...new Set(timeElements)].slice(0, 50);
        }
        """)
        print(f"Time elements found: {time_elements[:20]}")

        # Get the raw HTML with class names to understand structure
        relevant_html = await page.evaluate("""
        () => {
            // Find the main content area
            const main = document.querySelector('main') || document.querySelector('[class*="content"]') || document.querySelector('#root');
            if (main) return main.innerHTML.slice(0, 10000);
            return document.body.innerHTML.slice(0, 10000);
        }
        """)
        with open("/root/economics-conferences/res2026/relevant_html.html", "w") as f:
            f.write(relevant_html)

        await browser.close()

    # Now parse the text data to build a structured JSON
    # Read all day texts
    all_text = body_text
    
    # Parse into structured data
    program = parse_program_text(all_text)

    # Save
    with open(OUTPUT_PATH, "w") as f:
        json.dump(program, f, indent=2, default=str)
    
    print(f"\nFinal output saved to {OUTPUT_PATH}")
    print(f"Total sessions parsed: {len(program.get('sessions', []))}")
    print(f"Total days: {len(program.get('days', []))}")
    return program


def parse_program_text(text):
    """Parse the program text into structured JSON."""
    lines = text.split('\n')
    
    program = {
        "conference": "RES 2026 Annual Conference",
        "dates": "6-8 July 2026",
        "venue": "Newcastle University (Frederick Douglass Centre, Urban Sciences Building, Business School)",
        "days": [],
        "sessions": [],
        "keynotes": [],
        "raw_lines": lines
    }

    # Simple line-based parsing
    current_day = None
    current_stream = None
    current_session = None
    current_papers = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Detect day headers
        if re.match(r'^\d+\s+July\s+2026', line, re.IGNORECASE):
            current_day = line
            program["days"].append(line)
        
        # Detect stream headers
        elif line.startswith("Stream ") and current_day:
            current_stream = line
        
        # Detect time entries (HH:MM or HH:MM-HH:MM)
        time_match = re.match(r'^(\d{2}:\d{2})(?:-(\d{2}:\d{2}))?\s*$', line)
        if time_match:
            if current_session and current_papers:
                current_session["papers"] = current_papers
                program["sessions"].append(current_session)
                current_papers = []
            
            start_time = time_match.group(1)
            end_time = time_match.group(2) if time_match.group(2) else None
            
            # Check next lines for venue and title
            j = i + 1
            venue = ""
            title = ""
            session_type = ""
            chair = ""
            
            # Read the next few lines to get venue and title
            while j < len(lines) and j < i + 10:
                next_line = lines[j].strip()
                if not next_line:
                    j += 1
                    continue
                # Skip action buttons
                if next_line in ["Add to calendar", "Bookmark session"]:
                    j += 1
                    continue
                if next_line.startswith("Presentation type:"):
                    session_type = next_line.replace("Presentation type:", "").strip()
                    j += 1
                    continue
                if next_line.startswith("Chair:"):
                    chair = next_line.replace("Chair:", "").strip()
                    j += 1
                    continue
                # If we have a venue (contains building info)
                if not venue and ("Centre" in next_line or "Building" in next_line or "Boardroom" in next_line):
                    venue = next_line
                    j += 1
                    continue
                # First non-venue, non-action line that looks like a title
                if not title and not next_line.startswith("Add") and not next_line.startswith("Bookmark") and not next_line.startswith("Presentation") and not next_line.startswith("Chair") and not next_line.startswith("Move") and not re.match(r'^\d', next_line):
                    title = next_line
                    j += 1
                    continue
                break
            
            current_session = {
                "day": current_day,
                "stream": current_stream,
                "start_time": start_time,
                "end_time": end_time,
                "title": title,
                "venue": venue,
                "session_type": session_type,
                "chair": chair,
                "presentations": []
            }
        
        i += 1
    
    # Add last session
    if current_session and current_papers:
        current_session["papers"] = current_papers
        program["sessions"].append(current_session)
    
    return program


if __name__ == "__main__":
    result = asyncio.run(extract_full_program())
