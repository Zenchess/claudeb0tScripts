#!/usr/bin/env python3
"""
Use ascii-magic library and convert to hackmud format
"""

import re
import sys
import argparse
from ascii_magic import AsciiArt

# ANSI to hackmud color mapping
ANSI_TO_HACKMUD = {
    30: 'a',   # black
    31: 'D',   # red
    32: 'L',   # green
    33: 'H',   # yellow
    34: 'P',   # blue
    35: 'T',   # magenta
    36: 'N',   # cyan
    37: '1',   # white
    90: 'b',   # bright black (dark gray)
    91: 'D',   # bright red
    92: 'L',   # bright green
    93: 'H',   # bright yellow
    94: 'P',   # bright blue
    95: 'T',   # bright magenta
    96: 'N',   # bright cyan
    97: '1',   # bright white
    39: 'C',   # default
}

def ansi_to_hackmud(ansi_text):
    """Convert ANSI colored text to hackmud backtick format"""
    # Pattern for ANSI escape codes
    ansi_pattern = re.compile(r'\x1b\[([0-9;]*)m')

    result = []
    current_color = None
    pos = 0

    for match in ansi_pattern.finditer(ansi_text):
        # Add text before escape sequence
        text = ansi_text[pos:match.start()]
        if text:
            result.append(text)

        # Parse color code
        codes = match.group(1).split(';')
        for code in codes:
            if code.isdigit():
                num = int(code)
                if num in ANSI_TO_HACKMUD:
                    new_color = ANSI_TO_HACKMUD[num]
                    if new_color != current_color:
                        result.append('`' + new_color)
                        current_color = new_color

        pos = match.end()

    # Add remaining text
    result.append(ansi_text[pos:])

    return ''.join(result)

def image_to_hackmud(image_path, columns=60):
    """Convert image to hackmud ASCII art using ascii-magic"""
    art = AsciiArt.from_image(image_path)

    # Get terminal output (with ANSI colors)
    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    with redirect_stdout(f):
        art.to_terminal(columns=columns)
    ansi_output = f.getvalue()

    # Convert to hackmud format
    return ansi_to_hackmud(ansi_output)

def to_script(hackmud_text):
    """Wrap in hackmud script"""
    # Remove trailing whitespace from lines
    lines = [line.rstrip() for line in hackmud_text.split('\n')]
    clean = '\n'.join(lines)

    escaped = clean.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    return f'function(c,a){{return"{escaped}"}}'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert image to hackmud ASCII art')
    parser.add_argument('image', help='Input image path')
    parser.add_argument('-c', '--columns', type=int, default=60, help='Width in columns')
    parser.add_argument('-s', '--script', action='store_true', help='Output as hackmud script')
    parser.add_argument('-o', '--output', help='Output file')

    args = parser.parse_args()

    hackmud_art = image_to_hackmud(args.image, args.columns)

    if args.script:
        output = to_script(hackmud_art)
        print(f"Script size: {len(output)} chars", file=sys.stderr)
        if len(output) > 3500:
            print(f"WARNING: Exceeds limit by {len(output)-3500}!", file=sys.stderr)
    else:
        output = hackmud_art

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)
