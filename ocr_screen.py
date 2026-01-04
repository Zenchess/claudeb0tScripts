#!/usr/bin/env python3
"""
OCR the hackmud game window and return the text content.
Uses maim for screenshot and tesseract for OCR.
"""

import subprocess
import sys
import tempfile
import os

def get_hackmud_window_id():
    """Find the hackmud window ID"""
    try:
        result = subprocess.run(
            ['xdotool', 'search', '--name', 'hackmud'],
            capture_output=True, text=True, timeout=5
        )
        windows = result.stdout.strip().split('\n')
        if windows and windows[0]:
            return windows[0]
    except:
        pass

    # Try alternative names
    for name in ['HACKMUD', 'Hackmud']:
        try:
            result = subprocess.run(
                ['xdotool', 'search', '--name', name],
                capture_output=True, text=True, timeout=5
            )
            windows = result.stdout.strip().split('\n')
            if windows and windows[0]:
                return windows[0]
        except:
            pass

    return None

def capture_window(window_id, output_path):
    """Capture a screenshot of the specified window"""
    try:
        result = subprocess.run(
            ['maim', '-i', window_id, output_path],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Screenshot error: {e}", file=sys.stderr)
        return False

def ocr_image(image_path):
    """Run OCR on an image and return the text"""
    try:
        result = subprocess.run(
            ['tesseract', image_path, 'stdout', '-l', 'eng', '--psm', '6'],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout
    except Exception as e:
        print(f"OCR error: {e}", file=sys.stderr)
        return ""

def main():
    # Find hackmud window
    window_id = get_hackmud_window_id()
    if not window_id:
        print("Error: Could not find hackmud window", file=sys.stderr)
        sys.exit(1)

    # Create temp file for screenshot
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        temp_path = f.name

    try:
        # Capture screenshot
        if not capture_window(window_id, temp_path):
            print("Error: Failed to capture screenshot", file=sys.stderr)
            sys.exit(1)

        # OCR the image
        text = ocr_image(temp_path)

        # Output the text
        print(text)

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    main()
