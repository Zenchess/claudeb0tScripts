#!/usr/bin/env fontforge
"""
FontForge script to add Swedish characters (å ä ö Å Ä Ö) to whitrabt.ttf

This script:
1. Opens the font
2. Copies base glyphs (a, o, A, O)
3. Creates composite glyphs with diacritical marks using glyph pen
4. Saves the modified font

Run with: fontforge -script add_swedish_chars.py

Documentation:
- Swedish characters needed: å (U+00E5), ä (U+00E4), ö (U+00F6), Å (U+00C5), Ä (U+00C4), Ö (U+00D6)
- Method: Draw diacritical marks using glyphPen
- For umlauts (ä, ö, Ä, Ö): base + two dots above
- For ring (å, Å): base + ring above
"""

import fontforge
import math

# Input/output files
INPUT_FONT = "/home/jacob/hackmud/whitrabt.ttf"
OUTPUT_FONT = "/home/jacob/hackmud/whitrabt_swedish.ttf"

def draw_square_dot(pen, cx, cy, size):
    """Draw a square dot at (cx, cy)."""
    half = size / 2
    pen.moveTo((cx - half, cy - half))
    pen.lineTo((cx - half, cy + half))
    pen.lineTo((cx + half, cy + half))
    pen.lineTo((cx + half, cy - half))
    pen.closePath()

def draw_ring_as_polygon(pen, cx, cy, outer_r, inner_r, segments=12):
    """Draw a ring as a polygon (since curves have issues)."""
    import math

    # Outer circle (clockwise)
    pen.moveTo((cx + outer_r, cy))
    for i in range(1, segments + 1):
        angle = 2 * math.pi * i / segments
        x = cx + outer_r * math.cos(angle)
        y = cy + outer_r * math.sin(angle)
        pen.lineTo((x, y))
    pen.closePath()

    # Inner circle (counter-clockwise for hole)
    pen.moveTo((cx + inner_r, cy))
    for i in range(segments, 0, -1):
        angle = 2 * math.pi * i / segments
        x = cx + inner_r * math.cos(angle)
        y = cy + inner_r * math.sin(angle)
        pen.lineTo((x, y))
    pen.closePath()

def create_swedish_chars(font):
    """Create Swedish characters from base glyphs."""

    chars_to_create = [
        # (base, target_codepoint, name, diacritic_type)
        ('a', 0x00E4, 'adieresis', 'dieresis'),  # ä
        ('a', 0x00E5, 'aring', 'ring'),          # å
        ('o', 0x00F6, 'odieresis', 'dieresis'),  # ö
        ('A', 0x00C4, 'Adieresis', 'dieresis'),  # Ä
        ('A', 0x00C5, 'Aring', 'ring'),          # Å
        ('O', 0x00D6, 'Odieresis', 'dieresis'),  # Ö
    ]

    for base, target_cp, name, dia_type in chars_to_create:
        print(f"Creating {name} (U+{target_cp:04X}) from '{base}'...")

        # Copy base glyph to target
        font.selection.select(base)
        font.copy()
        font.selection.select(("unicode",), target_cp)
        font.paste()

        glyph = font[target_cp]
        glyph.glyphname = name

        # Get metrics from base glyph
        base_glyph = font[base]
        width = base_glyph.width
        bbox = glyph.boundingBox()  # (xmin, ymin, xmax, ymax)

        center_x = (bbox[0] + bbox[2]) / 2
        top_y = bbox[3]

        # Get a pen to draw on the glyph
        pen = glyph.glyphPen()

        if dia_type == 'dieresis':
            # Two dots above the letter
            dot_size = width * 0.12  # Size of each dot
            dot_spacing = width * 0.18  # Distance between dot centers
            dot_y = top_y + width * 0.14

            left_x = center_x - dot_spacing
            right_x = center_x + dot_spacing

            draw_square_dot(pen, left_x, dot_y, dot_size)
            draw_square_dot(pen, right_x, dot_y, dot_size)

        elif dia_type == 'ring':
            # Ring above the letter
            outer_r = width * 0.13
            inner_r = width * 0.06
            ring_y = top_y + width * 0.19

            draw_ring_as_polygon(pen, center_x, ring_y, outer_r, inner_r)

        # Close the pen
        pen = None

        # Set correct width
        glyph.width = width
        print(f"  Created {name}")

def main():
    print(f"Opening font: {INPUT_FONT}")
    font = fontforge.open(INPUT_FONT)

    print(f"\nFont info:")
    print(f"  Family: {font.familyname}")
    print(f"  Full name: {font.fullname}")
    print(f"  Em size: {font.em}")

    # Check which glyphs exist
    print(f"\nChecking base glyphs...")
    for char in ['a', 'o', 'A', 'O']:
        if ord(char) in font:
            g = font[ord(char)]
            print(f"  '{char}' exists: width={g.width}, bbox={g.boundingBox()}")
        else:
            print(f"  '{char}' MISSING!")

    # Create Swedish characters
    print(f"\nCreating Swedish characters...")
    create_swedish_chars(font)

    # Save the modified font
    print(f"\nSaving to: {OUTPUT_FONT}")
    font.generate(OUTPUT_FONT)

    print(f"\nDone! Swedish characters added:")
    print("  ä (U+00E4) - a with dieresis")
    print("  å (U+00E5) - a with ring above")
    print("  ö (U+00F6) - o with dieresis")
    print("  Ä (U+00C4) - A with dieresis")
    print("  Å (U+00C5) - A with ring above")
    print("  Ö (U+00D6) - O with dieresis")

    font.close()

if __name__ == "__main__":
    main()
