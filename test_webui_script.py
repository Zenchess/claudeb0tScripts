#!/usr/bin/env python3
"""
Playwright test for the hackmud webui script runner
"""

import asyncio
from playwright.async_api import async_playwright

async def test_script_runner():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Go to the webui
        print("Loading webui...")
        await page.goto('http://localhost:5000')
        await page.wait_for_load_state('networkidle')

        # Click the Script button to open the overlay
        print("Opening script panel...")
        script_btn = page.locator('#scriptToggleBtn')
        await script_btn.click()
        await asyncio.sleep(0.5)

        # Check if overlay is visible
        overlay = page.locator('#scriptOverlay')
        is_visible = await overlay.is_visible()
        print(f"Script overlay visible: {is_visible}")

        # Enter a test script
        print("Entering test script...")
        editor = page.locator('#scriptCode')
        await editor.fill('log("Hello from Playwright test!");')

        # Click Save button
        print("Clicking Save...")
        save_btn = page.locator('button:has-text("Save")')
        await save_btn.click()
        await asyncio.sleep(1)

        # Check status
        status = page.locator('#scriptStatus')
        status_text = await status.text_content()
        print(f"Status after save: {status_text}")

        # Click Start button
        print("Clicking Start...")
        start_btn = page.locator('#startBtn')
        await start_btn.click()
        await asyncio.sleep(2)

        # Switch to Logs tab
        print("Switching to Logs tab...")
        logs_tab = page.locator('button:has-text("Logs")')
        await logs_tab.click()
        await asyncio.sleep(1)

        # Check logs content
        logs_div = page.locator('#scriptLogs')
        logs_text = await logs_div.text_content()
        print(f"Logs content:\n{logs_text}")

        # Check if our log message appears
        if "Hello from Playwright" in logs_text:
            print("\n SUCCESS: Script executed and logged correctly!")
        else:
            print("\n FAILED: Log message not found")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_script_runner())
