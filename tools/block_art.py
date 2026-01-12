#!/usr/bin/env python3
"""
1:1 Block character converter for hackmud
Each character = 1 wide × 2 tall pixels
Uses ▀▄█ and space for binary representation
"""

from PIL import Image
import sys
import json

# Hackmud colors (subset for cleaner output)
COLORS = {
    'a': (0, 0, 0),           # black
    'b': (63, 63, 63),        # dark gray
    'C': (155, 155, 155),     # gray
    '1': (255, 255, 255),     # white
    'D': (255, 0, 0),         # red
    'F': (255, 128, 0),       # orange
    'H': (251, 200, 3),       # yellow
    'L': (30, 255, 0),        # green
    'N': (0, 255, 255),       # cyan
    'P': (0, 112, 221),       # blue
    'T': (176, 53, 238),      # purple
    'V': (255, 0, 236),       # magenta
}

def nearest_color(r, g, b, a):
    """Find nearest hackmud color"""
    if a < 128:  # transparent
        return None

    min_dist = float('inf')
    best = 'C'

    for code, (cr, cg, cb) in COLORS.items():
        dist = (r-cr)**2 + (g-cg)**2 + (b-cb)**2
        if dist < min_dist:
            min_dist = dist
            best = code

    return best

def image_to_blocks(image_path):
    """Convert image to colored block characters"""
    img = Image.open(image_path).convert('RGBA')
    w, h = img.size

    # Ensure even height
    if h % 2 != 0:
        h -= 1

    pixels = img.load()
    lines = []

    for y in range(0, h, 2):
        line = ''
        current_color = None

        for x in range(w):
            # Get top and bottom pixels
            r1, g1, b1, a1 = pixels[x, y]
            r2, g2, b2, a2 = pixels[x, y+1] if y+1 < img.height else (0,0,0,0)

            top_color = nearest_color(r1, g1, b1, a1)
            bot_color = nearest_color(r2, g2, b2, a2)

            # Determine character and color
            if top_color is None and bot_color is None:
                char = ' '
                color = None
            elif top_color is None:
                char = '▄'
                color = bot_color
            elif bot_color is None:
                char = '▀'
                color = top_color
            elif top_color == bot_color:
                char = '█'
                color = top_color
            else:
                # Two different colors - use top color with ▀
                # (simplification - could use background color but hackmud doesn't support it)
                char = '▀'
                color = top_color

            # Add color code if changed
            if color and color != current_color:
                line += '`' + color
                current_color = color

            line += char

        lines.append(line.rstrip())

    return '\n'.join(lines)

def to_script(art):
    """Convert to hackmud script"""
    escaped = json.dumps(art)[1:-1]
    return f'function(c,a){{return"{escaped}"}}'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: block_art.py image.png [-o output.js]")
        sys.exit(1)

    art = image_to_blocks(sys.argv[1])

    if '-o' in sys.argv:
        idx = sys.argv.index('-o')
        output_path = sys.argv[idx + 1]
        script = to_script(art)
        with open(output_path, 'w') as f:
            f.write(script)
        print(f"Size: {len(script)} chars", file=sys.stderr)
    else:
        print(art)
