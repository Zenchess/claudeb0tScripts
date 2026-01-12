#!/usr/bin/env python3
"""
Convert img2txt ANSI output to hackmud color format
Fixed to handle background colors properly
"""

import re
import subprocess
import sys
import argparse

# ANSI color codes to hackmud (handles both fg and bg)
# Normal: 30-37 (fg) / 40-47 (bg)
# Bright: 90-97 (fg) / 100-107 (bg)
ANSI_FG_TO_HACKMUD = {
    30: 'a', 31: 'd', 32: 'l', 33: 'h', 34: 'p', 35: 't', 36: 'n', 37: 'C',
    90: 'b', 91: 'D', 92: 'L', 93: 'H', 94: 'P', 95: 'T', 96: 'N', 97: '1',
}

ANSI_BG_TO_HACKMUD = {
    40: 'a', 41: 'd', 42: 'l', 43: 'h', 44: 'p', 45: 't', 46: 'n', 47: '1',
    100: 'b', 101: 'D', 102: 'L', 103: 'H', 104: 'P', 105: 'T', 106: 'N', 107: '1',
}

# Bold makes colors brighter
BOLD_FG = {
    30: 'b', 31: 'D', 32: 'L', 33: 'H', 34: 'P', 35: 'T', 36: 'N', 37: '1',
}

def parse_ansi_color(seq):
    """Parse ANSI escape sequence and return hackmud color code"""
    nums = [int(n) for n in re.findall(r'\d+', seq)]

    bold = 1 in nums
    blink = 5 in nums  # blink often means bright
    fg_color = None
    bg_color = None

    for n in nums:
        if 30 <= n <= 37 or 90 <= n <= 97:
            fg_color = n
        elif 40 <= n <= 47 or 100 <= n <= 107:
            bg_color = n

    # For img2txt, background color is often more important for the visual
    # Use background if it's not black (40), otherwise use foreground
    if bg_color is not None and bg_color != 40:
        return ANSI_BG_TO_HACKMUD.get(bg_color, 'C')

    if fg_color is not None:
        if (bold or blink) and fg_color in BOLD_FG:
            return BOLD_FG[fg_color]
        return ANSI_FG_TO_HACKMUD.get(fg_color, 'C')

    return None

def convert_ansi_to_hackmud(ansi_text):
    """Convert ANSI colored text to hackmud format"""
    ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')

    result = []
    current_color = None
    pos = 0

    for match in ansi_pattern.finditer(ansi_text):
        # Add text before this escape sequence
        text_before = ansi_text[pos:match.start()]
        if text_before:
            result.append(text_before)

        # Parse the color
        new_color = parse_ansi_color(match.group())
        if new_color and new_color != current_color:
            result.append('`' + new_color)
            current_color = new_color

        pos = match.end()

    # Add remaining text
    if pos < len(ansi_text):
        result.append(ansi_text[pos:])

    return ''.join(result)

def img2txt_to_hackmud(image_path, width=70, height=35):
    """Run img2txt and convert output to hackmud format"""
    try:
        result = subprocess.run(
            ['img2txt', '-W', str(width), '-H', str(height), image_path],
            capture_output=True,
            text=True
        )
        return convert_ansi_to_hackmud(result.stdout)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def to_hackmud_script(hackmud_text):
    """Wrap in hackmud script function"""
    escaped = hackmud_text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    return f'function(c,a){{return"{escaped}"}}'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert image to hackmud ASCII art via img2txt')
    parser.add_argument('image', help='Input image path')
    parser.add_argument('-w', '--width', type=int, default=70, help='Output width')
    parser.add_argument('-H', '--height', type=int, default=35, help='Output height')
    parser.add_argument('-s', '--script', action='store_true', help='Output as hackmud script')
    parser.add_argument('-o', '--output', help='Output file path')

    args = parser.parse_args()

    hackmud_art = img2txt_to_hackmud(args.image, args.width, args.height)

    if hackmud_art is None:
        sys.exit(1)

    if args.script:
        output = to_hackmud_script(hackmud_art)
        print(f"Script size: {len(output)} chars", file=sys.stderr)
        if len(output) > 3500:
            print(f"WARNING: Exceeds 3500 char limit by {len(output)-3500}!", file=sys.stderr)
    else:
        output = hackmud_art

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)
