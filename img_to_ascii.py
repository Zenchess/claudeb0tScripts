#!/usr/bin/env python3
"""
Image to ASCII converter for hackmud
Converts images to ASCII art using density ramp
"""

import sys
from PIL import Image
import argparse

# ASCII density ramps (light to dark)
RAMPS = {
    'short': ' .:-=+*#%@',
    'medium': ' .\'`^",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$',
    'simple': ' .-:=+*%#@',
    'blocks': ' ░▒▓█',
}

def image_to_ascii(image_path, width=80, height=None, ramp='simple', invert=False):
    """Convert image to ASCII art string"""

    # Load image
    img = Image.open(image_path)

    # Calculate dimensions
    orig_width, orig_height = img.size

    if height is None:
        # Maintain aspect ratio, account for char height (~2x width)
        aspect = orig_height / orig_width
        height = int(width * aspect * 0.5)  # chars are ~2x tall as wide

    # Resize image
    img = img.resize((width, height), Image.Resampling.LANCZOS)

    # Convert to grayscale
    img = img.convert('L')

    # Get ramp
    chars = RAMPS.get(ramp, RAMPS['simple'])
    if invert:
        chars = chars[::-1]

    num_chars = len(chars)

    # Convert pixels to ASCII
    pixels = list(img.getdata())
    ascii_lines = []

    for y in range(height):
        line = ''
        for x in range(width):
            pixel = pixels[y * width + x]
            # Map 0-255 to character index
            char_idx = int(pixel / 256 * num_chars)
            char_idx = min(char_idx, num_chars - 1)
            line += chars[char_idx]
        ascii_lines.append(line)

    return '\n'.join(ascii_lines)

def image_to_hackmud_script(image_path, script_name='ascii_art', **kwargs):
    """Generate a hackmud script that returns the ASCII art"""

    ascii_art = image_to_ascii(image_path, **kwargs)

    # Escape for JavaScript string
    escaped = ascii_art.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

    script = f'function(c,a){{return"{escaped}"}}'

    return script, len(script)

def image_to_db_format(image_path, **kwargs):
    """Generate ASCII art formatted for hackmud db storage"""

    ascii_art = image_to_ascii(image_path, **kwargs)
    lines = ascii_art.split('\n')

    # Return as array of lines for db storage
    return lines

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert image to ASCII art for hackmud')
    parser.add_argument('image', help='Input image path')
    parser.add_argument('-w', '--width', type=int, default=80, help='Output width in characters')
    parser.add_argument('-H', '--height', type=int, default=None, help='Output height (auto if not set)')
    parser.add_argument('-r', '--ramp', choices=RAMPS.keys(), default='simple', help='ASCII ramp to use')
    parser.add_argument('-i', '--invert', action='store_true', help='Invert colors')
    parser.add_argument('-s', '--script', action='store_true', help='Output as hackmud script')
    parser.add_argument('-o', '--output', help='Output file path')

    args = parser.parse_args()

    if args.script:
        script, size = image_to_hackmud_script(
            args.image,
            width=args.width,
            height=args.height,
            ramp=args.ramp,
            invert=args.invert
        )
        print(f"Script size: {size} chars", file=sys.stderr)
        if size > 3500:
            print(f"WARNING: Exceeds 3500 char limit by {size-3500}!", file=sys.stderr)
        output = script
    else:
        output = image_to_ascii(
            args.image,
            width=args.width,
            height=args.height,
            ramp=args.ramp,
            invert=args.invert
        )

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)
