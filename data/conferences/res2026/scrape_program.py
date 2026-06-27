#!/usr/bin/env python3
"""Scrape the RES 2026 Annual Conference program from Oxford Abstracts."""

import asyncio
import json
import re
import sys
from playwright.async_api import async_playwright

TARGET_URL = "https://virtual.oxfordabstracts.com/event/76093/program"
OUTPUT_PATH = "/root/economics-conferences/res2026/data.json"


async def scrape_program():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Capture network requests to find API calls
        api_responses = {}

        async def handle_response(response):
            url = response.url
            if "api" in url.lower() or "program" in url.lower() or "session" in url.lower() or "76093" in url:
                try:
                    body = await response.text()
                    api_responses[url] = body[:2000]
                except:
                    pass

        page.on("response", handle_response)

        print(f"Navigating to {TARGET_URL}...")
        await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)

        # Wait a bit for dynamic content to load
        await asyncio.sleep(3)

        # Check for loading state and wait for content
        try:
            await page.wait_for_selector(".startup-loading-container", state="hidden", timeout=10000)
        except:
            pass

        await asyncio.sleep(2)

        # Try to get the page title and main content
        title = await page.title()
        print(f"Page title: {title}")

        # Get all text content
        body_text = await page.evaluate("() => document.body.innerText")
        print(f"Body text length: {len(body_text)}")
        print(f"First 3000 chars:\n{body_text[:3000]}")

        # Try to find any structured data in the page
        # Check if there's a JSON payload in the HTML
        json_data = await page.evaluate("""
        () => {
            // Look for JSON-LD
            const scripts = document.querySelectorAll('script[type="application/ld+json"]');
            const results = [];
            scripts.forEach(s => {
                try {
                    results.push(JSON.parse(s.textContent));
                } catch(e) {}
            });
            return results;
        }
        """)
        print(f"JSON-LD found: {len(json_data)}")

        # Look for program data in window object or React state
        window_data = await page.evaluate("""
        () => {
            const results = {};
            // Check common data containers
            if (window.__INITIAL_STATE__) results.initialState = JSON.stringify(window.__INITIAL_STATE__).slice(0, 5000);
            if (window.__PRELOADED_STATE__) results.preloadedState = JSON.stringify(window.__PRELOADED_STATE__).slice(0, 5000);
            if (window.__DATA__) results.data = JSON.stringify(window.__DATA__).slice(0, 5000);
            if (window.__APOLLO_STATE__) results.apolloState = JSON.stringify(window.__APOLLO_STATE__).slice(0, 5000);
            return results;
        }
        """)
        print(f"Window data keys: {list(window_data.keys())}")
        for k, v in window_data.items():
            print(f"  {k}: {v[:500]}")

        # Save API responses info
        print(f"\nAPI responses captured: {len(api_responses)}")
        for url, body in api_responses.items():
            print(f"  URL: {url[:120]}")
            print(f"  Body: {body[:300]}")
            print()

        # Get full HTML for analysis
        html = await page.content()
        with open("/root/economics-conferences/res2026/full_page.html", "w") as f:
            f.write(html)

        await browser.close()

    # Build the output data
    output = {
        "source_url": TARGET_URL,
        "page_title": title,
        "body_text_preview": body_text[:5000],
        "api_responses": {k: v[:500] for k, v in api_responses.items()},
        "window_data": window_data,
        "json_ld": json_data,
        "note": "Program data may be rendered client-side - check full_page.html and api_responses for details"
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nOutput saved to {OUTPUT_PATH}")
    return output


if __name__ == "__main__":
    result = asyncio.run(scrape_program())
