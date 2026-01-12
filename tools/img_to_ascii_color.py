#!/usr/bin/env python3
"""
Image to COLORED ASCII converter for hackmud
Converts images to ASCII art with hackmud color codes
"""

import sys
from PIL import Image
import argparse
import math

# Hackmud color palette: code -> (R, G, B)
HACKMUD_COLORS = {
    'a': (0x00, 0x00, 0x00),      # black
    'b': (0x3F, 0x3F, 0x3F),      # dark gray
    'c': (0x67, 0x67, 0x67),      # medium gray
    'C': (0x9B, 0x9B, 0x9B),      # light gray
    'B': (0xCA, 0xCA, 0xCA),      # lighter gray
    '1': (0xFF, 0xFF, 0xFF),      # white
    'd': (0x7D, 0x00, 0x00),      # dark red
    'D': (0xFF, 0x00, 0x00),      # red
    'e': (0x8E, 0x34, 0x34),      # dark salmon
    'E': (0xFF, 0x83, 0x83),      # light red/pink
    'f': (0xA3, 0x4F, 0x00),      # dark orange
    'F': (0xFF, 0x80, 0x00),      # orange
    'g': (0x72, 0x54, 0x37),      # brown
    'G': (0xF3, 0xAA, 0x6F),      # tan
    'h': (0xA8, 0x86, 0x00),      # dark yellow
    'H': (0xFB, 0xC8, 0x03),      # yellow
    'i': (0xB2, 0x93, 0x4A),      # khaki
    'I': (0xFF, 0xD8, 0x63),      # light yellow
    'j': (0x93, 0x95, 0x00),      # olive
    'J': (0xFF, 0xF4, 0x04),      # bright yellow
    'k': (0x49, 0x52, 0x25),      # dark olive
    'K': (0xF3, 0xF9, 0x98),      # pale yellow
    'l': (0x29, 0x94, 0x00),      # dark green
    'L': (0x1E, 0xFF, 0x00),      # bright green
    'm': (0x23, 0x38, 0x1B),      # very dark green
    'M': (0xB3, 0xFF, 0x9B),      # light green
    'n': (0x00, 0x53, 0x5B),      # dark cyan
    'N': (0x00, 0xFF, 0xFF),      # cyan
    'o': (0x32, 0x4A, 0x4C),      # dark teal
    'O': (0x8F, 0xE6, 0xFF),      # light cyan
    'p': (0x00, 0x73, 0xA6),      # dark blue
    'P': (0x00, 0x70, 0xDD),      # blue
    'q': (0x38, 0x5A, 0x6C),      # slate
    'Q': (0xA4, 0xE3, 0xFF),      # light blue
    'r': (0x01, 0x00, 0x67),      # dark blue
    'R': (0x00, 0x00, 0xFF),      # pure blue
    's': (0x50, 0x7A, 0xA1),      # steel blue
    'S': (0x7A, 0xB2, 0xF4),      # sky blue
    't': (0x60, 0x1C, 0x81),      # dark purple
    'T': (0xB0, 0x35, 0xEE),      # purple
    'u': (0x43, 0x31, 0x4C),      # dark violet
    'U': (0xE6, 0xC4, 0xFF),      # lavender
    'v': (0x8C, 0x00, 0x69),      # dark magenta
    'V': (0xFF, 0x00, 0xEC),      # magenta
    'w': (0x97, 0x39, 0x84),      # dark pink
    'W': (0xFF, 0x96, 0xE0),      # pink
    'x': (0x88, 0x00, 0x24),      # dark rose
    'X': (0xFF, 0x00, 0x70),      # rose
    'y': (0x76, 0x2E, 0x4A),      # dark mauve
    'Y': (0xFF, 0x6A, 0x98),      # light rose
}

# Brightness characters (dark to light) - clean high-contrast set
BRIGHTNESS_CHARS = ' .:+*#@'

def color_distance(c1, c2):
    """Calculate color distance using weighted RGB (human perception)"""
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    # Weighted by human color perception
    return math.sqrt(2*(r1-r2)**2 + 4*(g1-g2)**2 + 3*(b1-b2)**2)

def find_nearest_color(rgb):
    """Find the nearest hackmud color code for an RGB value"""
    min_dist = float('inf')
    nearest = '1'  # default white

    for code, color in HACKMUD_COLORS.items():
        dist = color_distance(rgb, color)
        if dist < min_dist:
            min_dist = dist
            nearest = code

    return nearest

def get_brightness_char(brightness):
    """Get ASCII char based on brightness (0-255)"""
    idx = int(brightness / 256 * len(BRIGHTNESS_CHARS))
    idx = min(idx, len(BRIGHTNESS_CHARS) - 1)
    return BRIGHTNESS_CHARS[idx]

def image_to_colored_ascii(image_path, width=80, height=None, invert=False):
    """Convert image to colored ASCII art string with hackmud color codes"""

    # Load image
    img = Image.open(image_path)

    # Convert to RGBA to handle transparency
    img = img.convert('RGBA')

    # Calculate dimensions
    orig_width, orig_height = img.size

    if height is None:
        aspect = orig_height / orig_width
        height = int(width * aspect * 0.5)  # chars are ~2x tall as wide

    # Resize image
    img = img.resize((width, height), Image.Resampling.LANCZOS)

    pixels = list(img.getdata())

    result_lines = []
    current_color = None

    for y in range(height):
        line = ''
        for x in range(width):
            r, g, b, a = pixels[y * width + x]

            # Handle transparency - use black/space for transparent
            if a < 128:
                if current_color != 'a':
                    line += '`a'
                    current_color = 'a'
                line += ' '
                continue

            # Find nearest hackmud color
            color_code = find_nearest_color((r, g, b))

            # Calculate brightness for character selection
            brightness = int(0.299 * r + 0.587 * g + 0.114 * b)
            if invert:
                brightness = 255 - brightness

            char = get_brightness_char(brightness)

            # Only add color code if it changed
            if color_code != current_color:
                line += '`' + color_code
                current_color = color_code

            line += char

        result_lines.append(line)
        current_color = None  # Reset at line end for safety

    return '\n'.join(result_lines)

def image_to_hackmud_script(image_path, **kwargs):
    """Generate a hackmud script that returns colored ASCII art"""

    ascii_art = image_to_colored_ascii(image_path, **kwargs)

    # Escape for JavaScript string
    escaped = ascii_art.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

    script = f'function(c,a){{return"{escaped}"}}'

    return script, len(script)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert image to COLORED ASCII art for hackmud')
    parser.add_argument('image', help='Input image path')
    parser.add_argument('-w', '--width', type=int, default=80, help='Output width in characters')
    parser.add_argument('-H', '--height', type=int, default=None, help='Output height (auto if not set)')
    parser.add_argument('-i', '--invert', action='store_true', help='Invert brightness')
    parser.add_argument('-s', '--script', action='store_true', help='Output as hackmud script')
    parser.add_argument('-o', '--output', help='Output file path')

    args = parser.parse_args()

    if args.script:
        script, size = image_to_hackmud_script(
            args.image,
            width=args.width,
            height=args.height,
            invert=args.invert
        )
        print(f"Script size: {size} chars", file=sys.stderr)
        if size > 3500:
            print(f"WARNING: Exceeds 3500 char limit by {size-3500}!", file=sys.stderr)
        output = script
    else:
        output = image_to_colored_ascii(
            args.image,
            width=args.width,
            height=args.height,
            invert=args.invert
        )

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)
