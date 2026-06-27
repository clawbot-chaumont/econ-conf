#!/usr/bin/env python3
"""Try to expand sessions to get individual paper titles."""

import asyncio
import json
from playwright.async_api import async_playwright

TARGET_URL = "https://virtual.oxfordabstracts.com/event/76093/program"

async def expand_and_extract():
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

        # Try clicking session boxes to expand them
        for day_label in ["Mon6", "Tue7", "Wed8"]:
            # Click the day tab
            await page.evaluate(f"""
            () => {{
                const buttons = document.querySelectorAll('button');
                for (const b of buttons) {{
                    if (b.textContent.trim() === '{day_label}') {{
                        b.click();
                        return true;
                    }}
                }}
                return false;
            }}
            """)
            await asyncio.sleep(3)
            
            # Try to find and click all session entries
            clicked = await page.evaluate("""
            () => {
                // Find all elements with time ranges that are clickable
                const allEls = document.querySelectorAll('*');
                let count = 0;
                for (const el of allEls) {
                    const text = el.textContent.trim();
                    // Match time range pattern
                    if (/^\d{2}:\d{2}-\d{2}:\d{2}$/.test(text)) {
                        // Try clicking the parent that is clickable
                        let target = el;
                        for (let p = el; p && p !== document.body; p = p.parentElement) {
                            if (p.getAttribute('role') === 'button' || 
                                p.classList.length > 0 && 
                                window.getComputedStyle(p).cursor === 'pointer') {
                                target = p;
                                break;
                            }
                        }
                        try {
                            target.click();
                            count++;
                        } catch(e) {}
                    }
                }
                return count;
            }
            """)
            print(f"  {day_label}: clicked {clicked} elements")
            await asyncio.sleep(2)
            
            # Get expanded text
            text = await page.evaluate("() => document.body.innerText")
            with open(f"/root/economics-conferences/res2026/expanded_{day_label.lower()}.txt", "w") as f:
                f.write(text)
            print(f"  Saved ({len(text)} chars)")

        await browser.close()
        print("Done!")

asyncio.run(expand_and_extract())
