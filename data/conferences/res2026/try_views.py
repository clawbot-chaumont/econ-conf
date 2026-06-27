#!/usr/bin/env python3
"""Try different views on the Oxford Abstracts program."""

import asyncio
import json
from playwright.async_api import async_playwright

TARGET_URL = "https://virtual.oxfordabstracts.com/event/76093/program"

async def try_views():
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

        views = {}
        
        # Try clicking "List view"
        for view_name in ["List view", "Titles"]:
            clicked = await page.evaluate(f"""
            () => {{
                const all = document.querySelectorAll('*');
                for (const el of all) {{
                    if (el.textContent.trim() === '{view_name}') {{
                        el.click();
                        return true;
                    }}
                }}
                return false;
            }}
            """)
            print(f"Clicked '{view_name}': {clicked}")
            await asyncio.sleep(3)
            
            # Scroll to load
            for _ in range(8):
                await page.evaluate("window.scrollBy(0, 400)")
                await asyncio.sleep(0.3)
            
            text = await page.evaluate("() => document.body.innerText")
            views[view_name] = text
            print(f"  Text length: {len(text)}")
            with open(f"/root/economics-conferences/res2026/view_{view_name.replace(' ', '_').lower()}.txt", "w") as f:
                f.write(text)

        # Try clicking "Download schedule" 
        clicked = await page.evaluate("""
        () => {
            const all = document.querySelectorAll('*');
            for (const el of all) {
                if (el.textContent.trim() === 'Download schedule') {
                    el.click();
                    return true;
                }
            }
            return false;
        }
        """)
        print(f"Clicked 'Download schedule': {clicked}")
        await asyncio.sleep(2)

        await browser.close()

asyncio.run(try_views())
