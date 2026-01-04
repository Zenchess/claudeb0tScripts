#!/usr/bin/env python3
"""Convert hackmud terminal color tags to Discord ANSI format.

Reads terminal output with Unity <color=#RRGGBBFF> tags and converts
to Discord's ANSI 16-color format for posting in code blocks.
"""

import re
import sys
import argparse
from read_vtable import VtableReader, get_hackmud_pid

# Discord ANSI color codes (16 basic colors)
# Format: ESC[style;colorCode m (ESC = \x1b)
ANSI_COLORS = {
    'black': '\x1b[2;30m',
    'red': '\x1b[2;31m',
    'green': '\x1b[2;32m',
    'yellow': '\x1b[2;33m',
    'blue': '\x1b[2;34m',
    'magenta': '\x1b[2;35m',
    'cyan': '\x1b[2;36m',
    'white': '\x1b[2;37m',
    'reset': '\x1b[0m',
}

# Hackmud color palette approximations (hex -> nearest ANSI)
def hex_to_rgb(hex_color):
    """Convert #RRGGBB or #RRGGBBFF to (r, g, b)"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) >= 6:
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )
    return (255, 255, 255)

def rgb_to_ansi(r, g, b):
    """Map RGB to nearest ANSI 16-color"""
    # Calculate intensity
    intensity = (r + g + b) / 3

    # Very dark = black
    if intensity < 40:
        return 'black'

    # Check for grayscale
    if abs(r - g) < 30 and abs(g - b) < 30 and abs(r - b) < 30:
        if intensity < 100:
            return 'black'
        elif intensity > 200:
            return 'white'
        else:
            return 'white'  # Discord doesn't have gray, use white

    # Find dominant color(s)
    max_val = max(r, g, b)

    # Normalize
    threshold = max_val * 0.6

    has_r = r >= threshold
    has_g = g >= threshold
    has_b = b >= threshold

    if has_r and has_g and has_b:
        return 'white'
    elif has_r and has_g:
        return 'yellow'
    elif has_r and has_b:
        return 'magenta'
    elif has_g and has_b:
        return 'cyan'
    elif has_r:
        return 'red'
    elif has_g:
        return 'green'
    elif has_b:
        return 'blue'
    else:
        return 'white'

def convert_color_tags(text):
    """Convert Unity <color=#HEX> tags to ANSI codes"""
    result = []
    pos = 0
    current_color = None

    # Pattern for Unity color tags
    color_pattern = re.compile(r'<color=(#[0-9A-Fa-f]{6,8})>')
    close_pattern = re.compile(r'</color>')

    while pos < len(text):
        # Check for opening color tag
        color_match = color_pattern.match(text, pos)
        if color_match:
            hex_color = color_match.group(1)
            r, g, b = hex_to_rgb(hex_color)
            ansi_name = rgb_to_ansi(r, g, b)
            result.append(ANSI_COLORS[ansi_name])
            current_color = ansi_name
            pos = color_match.end()
            continue

        # Check for closing color tag
        close_match = close_pattern.match(text, pos)
        if close_match:
            result.append(ANSI_COLORS['reset'])
            current_color = None
            pos = close_match.end()
            continue

        # Regular character
        result.append(text[pos])
        pos += 1

    # Reset at end if still colored
    if current_color:
        result.append(ANSI_COLORS['reset'])

    return ''.join(result)

def format_for_discord(text):
    """Wrap text in Discord ANSI code block"""
    return f"```ansi\n{text}\n```"

def main():
    parser = argparse.ArgumentParser(description='Convert hackmud colors to Discord ANSI')
    parser.add_argument('lines', nargs='?', type=int, default=30, help='Number of lines')
    parser.add_argument('--chat', '-c', action='store_true', help='Read chat instead of shell')
    parser.add_argument('--raw', action='store_true', help='Output raw ANSI without Discord wrapper')
    args = parser.parse_args()

    pid = get_hackmud_pid()
    if not pid:
        print("Hackmud not running", file=sys.stderr)
        sys.exit(1)

    reader = VtableReader(pid)

    if args.chat:
        text = reader.read_chat()
    else:
        text = reader.read_shell()

    reader.close()

    if not text:
        print("Could not read terminal", file=sys.stderr)
        sys.exit(1)

    # Convert colors
    converted = convert_color_tags(text)

    # Get last N lines
    lines = converted.split('\n')
    output_lines = lines[-args.lines:] if len(lines) > args.lines else lines
    output = '\n'.join(output_lines)

    if args.raw:
        print(output)
    else:
        print(format_for_discord(output))

if __name__ == '__main__':
    main()
