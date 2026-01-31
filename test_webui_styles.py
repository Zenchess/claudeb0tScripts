#!/usr/bin/env python3
"""
Test the hackmud webui with Playwright to diagnose style issues
"""

from playwright.sync_api import sync_playwright
import time

def test_webui():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)  # Headless mode for automated testing
        page = browser.new_page()

        # Navigate to localhost
        page.goto('http://localhost:5000')

        # Wait for page to load
        time.sleep(2)

        # Find the command input
        input_elem = page.locator('#commandInput')

        # Enable the input for testing (simulate being logged in)
        input_elem.evaluate('el => el.disabled = false')

        # Type some text to trigger the overlay
        input_elem.fill('chats.tell{to:"test",msg:"hello"}')
        time.sleep(0.5)  # Wait for overlay to update

        # Get computed styles including position and z-index
        styles = input_elem.evaluate('''el => {
            const computed = window.getComputedStyle(el);
            return {
                color: computed.color,
                backgroundColor: computed.backgroundColor,
                border: computed.border,
                position: computed.position,
                zIndex: computed.zIndex,
                top: computed.top,
                left: computed.left,
                display: computed.display,
                opacity: computed.opacity
            };
        }''')
        is_disabled = input_elem.evaluate('el => el.disabled')

        # Check autofill pseudo-class
        autofill_color = input_elem.evaluate('el => window.getComputedStyle(el, ":-webkit-autofill").color')

        print("=" * 60)
        print("Command Input Computed Styles:")
        print("=" * 60)
        print(f"Color: {styles['color']}")
        print(f"Background: {styles['backgroundColor']}")
        print(f"Border: {styles['border']}")
        print(f"Position: {styles['position']}")
        print(f"Z-Index: {styles['zIndex']}")
        print(f"Top: {styles['top']}")
        print(f"Left: {styles['left']}")
        print(f"Display: {styles['display']}")
        print(f"Opacity: {styles['opacity']}")
        print(f"Disabled: {is_disabled}")
        print(f"Autofill color: {autofill_color}")
        print("=" * 60)

        # Check if there's an overlay
        try:
            overlay = page.locator('#inputOverlay')
            overlay_exists = overlay.count() > 0
            print(f"\nOverlay element exists: {overlay_exists}")
            if overlay_exists:
                overlay_styles = overlay.evaluate('''el => {
                    const computed = window.getComputedStyle(el);
                    return {
                        color: computed.color,
                        display: computed.display,
                        zIndex: computed.zIndex,
                        position: computed.position,
                        content: el.innerHTML
                    };
                }''')
                print(f"Overlay color: {overlay_styles['color']}")
                print(f"Overlay display: {overlay_styles['display']}")
                print(f"Overlay z-index: {overlay_styles['zIndex']}")
                print(f"Overlay position: {overlay_styles['position']}")
                print(f"Overlay HTML: {overlay_styles['content'][:100]}...")  # First 100 chars
        except:
            print("\nNo overlay element found")

        # Check all elements in command-bar
        print("\nAll elements in .command-bar:")
        command_bar_children = page.locator('.command-bar > *').evaluate_all('''elements => {
            return elements.map(el => {
                const computed = window.getComputedStyle(el);
                return {
                    tag: el.tagName,
                    id: el.id,
                    classes: el.className,
                    position: computed.position,
                    zIndex: computed.zIndex,
                    color: computed.color,
                    display: computed.display
                };
            });
        }''')
        for i, child in enumerate(command_bar_children):
            print(f"\n  Element {i+1}:")
            for key, value in child.items():
                print(f"    {key}: {value}")

        print("=" * 60)

        # Take a screenshot
        page.screenshot(path='/tmp/webui_test.png')
        print("\nScreenshot saved to /tmp/webui_test.png")

        browser.close()

if __name__ == '__main__':
    test_webui()
