#!/usr/bin/env python3
"""
Convert pixel art images to hackmud text art using color codes.
Hackmud uses backtick syntax: `Xtext` where X is a color code.
"""

from PIL import Image
import sys
import math

# Hackmud color palette (approximate RGB values)
HACKMUD_COLORS = {
    '0': (155, 155, 155),  # gray
    '1': (255, 255, 255),  # white
    '2': (30, 255, 0),     # green
    '3': (255, 236, 0),    # yellow
    '4': (255, 0, 110),    # red/magenta
    '5': (255, 128, 0),    # orange
    '6': (255, 128, 0),    # orange
    '7': (255, 128, 0),    # orange
    '8': (255, 128, 0),    # orange
    '9': (255, 128, 0),    # orange
    'A': (255, 255, 255),  # white
    'B': (202, 202, 202),  # light gray
    'C': (155, 155, 155),  # gray
    'D': (100, 60, 170),   # purple
    'E': (0, 0, 0),        # black (actually dark)
    'F': (255, 128, 0),    # orange
    'N': (0, 255, 255),    # cyan
    'b': (63, 63, 63),     # dark gray
}

# Block characters for pixel rendering
FULL_BLOCK = '█'
UPPER_HALF = '▀'
LOWER_HALF = '▄'
LIGHT_SHADE = '░'
MED_SHADE = '▒'
DARK_SHADE = '▓'

def color_distance(c1, c2):
    """Calculate color distance using simple Euclidean distance."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def find_closest_hackmud_color(rgb):
    """Find the closest hackmud color code for an RGB value."""
    if len(rgb) == 4:  # RGBA
        if rgb[3] < 128:  # Transparent
            return None
        rgb = rgb[:3]

    # Check for very dark colors (treat as background/transparent)
    if all(c < 20 for c in rgb):
        return None

    min_dist = float('inf')
    closest = '0'

    for code, color in HACKMUD_COLORS.items():
        dist = color_distance(rgb, color)
        if dist < min_dist:
            min_dist = dist
            closest = code

    return closest

def convert_image_to_hackmud(image_path, width=None, use_half_blocks=True):
    """Convert a pixel art image to hackmud text art."""
    img = Image.open(image_path)
    img = img.convert('RGBA')

    # Resize if needed (preserve aspect ratio)
    orig_w, orig_h = img.size
    if width:
        ratio = width / orig_w
        new_h = int(orig_h * ratio)
        img = img.resize((width, new_h), Image.NEAREST)

    w, h = img.size
    pixels = img.load()

    lines = []

    if use_half_blocks:
        # Use half-block technique for double vertical resolution
        for y in range(0, h, 2):
            line = ''
            current_fg = None
            current_bg = None
            buffer = ''

            for x in range(w):
                top_pixel = pixels[x, y] if y < h else (0, 0, 0, 0)
                bot_pixel = pixels[x, y + 1] if y + 1 < h else (0, 0, 0, 0)

                top_color = find_closest_hackmud_color(top_pixel)
                bot_color = find_closest_hackmud_color(bot_pixel)

                if top_color is None and bot_color is None:
                    # Both transparent - use space
                    if buffer:
                        line += f'`{current_fg}{buffer}`' if current_fg else buffer
                        buffer = ''
                        current_fg = None
                    line += ' '
                elif top_color == bot_color:
                    # Same color - use full block
                    if current_fg != top_color:
                        if buffer:
                            line += f'`{current_fg}{buffer}`' if current_fg else buffer
                        buffer = FULL_BLOCK
                        current_fg = top_color
                    else:
                        buffer += FULL_BLOCK
                elif top_color and not bot_color:
                    # Only top - use upper half
                    if current_fg != top_color:
                        if buffer:
                            line += f'`{current_fg}{buffer}`' if current_fg else buffer
                        buffer = UPPER_HALF
                        current_fg = top_color
                    else:
                        buffer += UPPER_HALF
                elif bot_color and not top_color:
                    # Only bottom - use lower half
                    if current_fg != bot_color:
                        if buffer:
                            line += f'`{current_fg}{buffer}`' if current_fg else buffer
                        buffer = LOWER_HALF
                        current_fg = bot_color
                    else:
                        buffer += LOWER_HALF
                else:
                    # Different colors - use upper half with foreground color
                    # (We lose some info here without background color support)
                    if current_fg != top_color:
                        if buffer:
                            line += f'`{current_fg}{buffer}`' if current_fg else buffer
                        buffer = UPPER_HALF
                        current_fg = top_color
                    else:
                        buffer += UPPER_HALF

            if buffer:
                line += f'`{current_fg}{buffer}`' if current_fg else buffer

            lines.append(line.rstrip())
    else:
        # Simple full-block rendering
        for y in range(h):
            line = ''
            current_color = None
            buffer = ''

            for x in range(w):
                pixel = pixels[x, y]
                color = find_closest_hackmud_color(pixel)

                if color is None:
                    if buffer:
                        line += f'`{current_color}{buffer}`' if current_color else buffer
                        buffer = ''
                        current_color = None
                    line += ' '
                elif color != current_color:
                    if buffer:
                        line += f'`{current_color}{buffer}`' if current_color else buffer
                    buffer = FULL_BLOCK
                    current_color = color
                else:
                    buffer += FULL_BLOCK

            if buffer:
                line += f'`{current_color}{buffer}`' if current_color else buffer

            lines.append(line.rstrip())

    # Remove empty trailing lines
    while lines and not lines[-1].strip():
        lines.pop()

    return '\n'.join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python pixel_to_hackmud.py <image.png> [width] [--no-half]")
        print("  width: resize to this width (default: original)")
        print("  --no-half: use full blocks instead of half blocks")
        sys.exit(1)

    image_path = sys.argv[1]
    width = None
    use_half = True

    for arg in sys.argv[2:]:
        if arg == '--no-half':
            use_half = False
        elif arg.isdigit():
            width = int(arg)

    result = convert_image_to_hackmud(image_path, width, use_half)
    print(result)

    # Also save to file
    output_file = image_path.rsplit('.', 1)[0] + '_hackmud.txt'
    with open(output_file, 'w') as f:
        f.write(result)
    print(f"\nSaved to: {output_file}", file=sys.stderr)

if __name__ == '__main__':
    main()
