#!/usr/bin/env fontforge
"""
FontForge script to add extended Latin characters to whitrabt.ttf

This script adds common European characters with diacritical marks:
- Swedish: å ä ö Å Ä Ö
- German: ü Ü ß
- French: é è ê ë à â ç É È Ê Ë À Â Ç
- Spanish: ñ Ñ
- And other common accented characters

Run with: fontforge -script add_extended_chars.py

The approach:
1. Copy base glyph (a, e, i, o, u, n, c, etc.)
2. Draw diacritical marks above/below using the glyphPen
3. Save as new font file
"""

import fontforge
import math

# Input/output files
INPUT_FONT = "/home/jacob/hackmud/whitrabt.ttf"
OUTPUT_FONT = "/home/jacob/hackmud/whitrabt_extended.ttf"

def draw_square_dot(pen, cx, cy, size):
    """Draw a square dot at (cx, cy)."""
    half = size / 2
    pen.moveTo((cx - half, cy - half))
    pen.lineTo((cx - half, cy + half))
    pen.lineTo((cx + half, cy + half))
    pen.lineTo((cx + half, cy - half))
    pen.closePath()

def draw_ring_as_polygon(pen, cx, cy, outer_r, inner_r, segments=12):
    """Draw a ring as a polygon."""
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

def draw_acute(pen, cx, cy, size):
    """Draw acute accent (/) at position."""
    pen.moveTo((cx - size*0.3, cy - size*0.3))
    pen.lineTo((cx - size*0.1, cy - size*0.3))
    pen.lineTo((cx + size*0.3, cy + size*0.3))
    pen.lineTo((cx + size*0.1, cy + size*0.3))
    pen.closePath()

def draw_grave(pen, cx, cy, size):
    """Draw grave accent (\\) at position."""
    pen.moveTo((cx + size*0.3, cy - size*0.3))
    pen.lineTo((cx + size*0.1, cy - size*0.3))
    pen.lineTo((cx - size*0.3, cy + size*0.3))
    pen.lineTo((cx - size*0.1, cy + size*0.3))
    pen.closePath()

def draw_circumflex(pen, cx, cy, size):
    """Draw circumflex (^) at position."""
    pen.moveTo((cx, cy + size*0.3))
    pen.lineTo((cx - size*0.4, cy - size*0.2))
    pen.lineTo((cx - size*0.2, cy - size*0.2))
    pen.lineTo((cx, cy + size*0.1))
    pen.lineTo((cx + size*0.2, cy - size*0.2))
    pen.lineTo((cx + size*0.4, cy - size*0.2))
    pen.closePath()

def draw_tilde(pen, cx, cy, size):
    """Draw tilde (~) as a wavy line."""
    # Simplified tilde as two curved segments
    hw = size * 0.4
    hh = size * 0.15
    thick = size * 0.12

    # Top edge
    pen.moveTo((cx - hw, cy))
    pen.lineTo((cx - hw*0.3, cy + hh))
    pen.lineTo((cx + hw*0.3, cy - hh))
    pen.lineTo((cx + hw, cy))
    # Bottom edge
    pen.lineTo((cx + hw*0.3, cy - hh - thick))
    pen.lineTo((cx - hw*0.3, cy + hh - thick))
    pen.closePath()

def draw_cedilla(pen, cx, cy, size):
    """Draw cedilla (,) below character."""
    # Simple hook shape
    pen.moveTo((cx - size*0.1, cy))
    pen.lineTo((cx + size*0.1, cy))
    pen.lineTo((cx + size*0.15, cy - size*0.3))
    pen.lineTo((cx, cy - size*0.5))
    pen.lineTo((cx - size*0.2, cy - size*0.4))
    pen.lineTo((cx - size*0.1, cy - size*0.3))
    pen.closePath()

def draw_caron(pen, cx, cy, size):
    """Draw caron/hacek (v shape) at position."""
    pen.moveTo((cx, cy - size*0.3))
    pen.lineTo((cx - size*0.4, cy + size*0.2))
    pen.lineTo((cx - size*0.2, cy + size*0.2))
    pen.lineTo((cx, cy - size*0.1))
    pen.lineTo((cx + size*0.2, cy + size*0.2))
    pen.lineTo((cx + size*0.4, cy + size*0.2))
    pen.closePath()

def create_char_with_diacritic(font, base, target_cp, name, diacritic, is_uppercase=False):
    """Create a character with the specified diacritic."""
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
    bottom_y = bbox[1]

    # Get a pen to draw on the glyph (replace=False preserves existing contours)
    pen = glyph.glyphPen(replace=False)

    # Position and size adjustments
    accent_y = top_y + width * 0.14
    accent_size = width * 0.15 if is_uppercase else width * 0.12

    if diacritic == 'dieresis':
        dot_size = width * 0.12
        dot_spacing = width * 0.18
        dot_y = accent_y
        draw_square_dot(pen, center_x - dot_spacing, dot_y, dot_size)
        draw_square_dot(pen, center_x + dot_spacing, dot_y, dot_size)

    elif diacritic == 'ring':
        outer_r = width * 0.13
        inner_r = width * 0.06
        ring_y = top_y + width * 0.19
        draw_ring_as_polygon(pen, center_x, ring_y, outer_r, inner_r)

    elif diacritic == 'acute':
        draw_acute(pen, center_x, accent_y, accent_size)

    elif diacritic == 'grave':
        draw_grave(pen, center_x, accent_y, accent_size)

    elif diacritic == 'circumflex':
        draw_circumflex(pen, center_x, accent_y, accent_size)

    elif diacritic == 'tilde':
        draw_tilde(pen, center_x, accent_y, accent_size)

    elif diacritic == 'cedilla':
        draw_cedilla(pen, center_x, bottom_y, accent_size)

    elif diacritic == 'caron':
        draw_caron(pen, center_x, accent_y, accent_size)

    # Close the pen
    pen = None

    # Set correct width
    glyph.width = width
    print(f"  Created {name}")

def create_eszett(font):
    """Create German eszett (ß) based on Kaj's whitrabt-style reference image.

    Looking at Kaj's image carefully:
    - Tall left vertical stem
    - Top horizontal bar extending right
    - From top-right, diagonal going DOWN-LEFT toward the stem
    - Then horizontal going RIGHT at bottom portion
    - Creates an angular "ß" shape
    """
    print("Creating eszett (U+00DF) based on Kaj's reference...")

    if ord('s') not in font or ord('f') not in font:
        print("  Missing base glyphs, skipping")
        return

    target_cp = 0x00DF

    # Create glyph slot by copying 's'
    font.selection.select('s')
    font.copy()
    font.selection.select(("unicode",), target_cp)
    font.paste()

    glyph = font[target_cp]
    glyph.clear()  # Clear - we'll draw from scratch
    glyph.glyphname = "germandbls"

    # Get metrics from reference glyphs
    f_glyph = font[ord('f')]
    s_glyph = font[ord('s')]
    width = s_glyph.width

    # Use f's ascender height for the tall part
    f_bbox = f_glyph.boundingBox()
    tall_h = f_bbox[3]  # Ascender height (like f)
    base = 0  # Baseline

    pen = glyph.glyphPen(replace=False)

    # Stroke thickness
    t = width * 0.16

    # Key positions based on Kaj's design
    left = width * 0.12          # Left stem edge
    stem_right = left + t        # Right edge of stem
    top_bar_right = width * 0.78 # Where top bar ends
    mid_y = tall_h * 0.45        # Middle horizontal level
    bot_y = tall_h * 0.18        # Bottom bar level

    # Part 1: Left vertical stem (baseline to top)
    pen.moveTo((left, base))
    pen.lineTo((left, tall_h))
    pen.lineTo((stem_right, tall_h))
    pen.lineTo((stem_right, base))
    pen.closePath()

    # Part 2: Top horizontal bar
    pen.moveTo((stem_right, tall_h))
    pen.lineTo((top_bar_right, tall_h))
    pen.lineTo((top_bar_right, tall_h - t))
    pen.lineTo((stem_right, tall_h - t))
    pen.closePath()

    # Part 3: Diagonal from top-right down-left to middle
    diag_top_x = top_bar_right - t * 0.5
    diag_top_y = tall_h - t
    diag_bot_x = stem_right + t * 0.5
    diag_bot_y = mid_y + t

    pen.moveTo((diag_top_x, diag_top_y))
    pen.lineTo((top_bar_right, diag_top_y))
    pen.lineTo((diag_bot_x + t, diag_bot_y))
    pen.lineTo((diag_bot_x, diag_bot_y))
    pen.closePath()

    # Part 4: Middle horizontal going right
    pen.moveTo((stem_right, mid_y + t))
    pen.lineTo((width * 0.65, mid_y + t))
    pen.lineTo((width * 0.65, mid_y))
    pen.lineTo((stem_right, mid_y))
    pen.closePath()

    # Part 5: Second diagonal from middle-right down-left
    pen.moveTo((width * 0.65 - t * 0.5, mid_y))
    pen.lineTo((width * 0.65, mid_y))
    pen.lineTo((stem_right + t * 1.5, bot_y + t))
    pen.lineTo((stem_right + t * 0.5, bot_y + t))
    pen.closePath()

    # Part 6: Bottom horizontal going right
    pen.moveTo((stem_right, bot_y + t))
    pen.lineTo((width * 0.75, bot_y + t))
    pen.lineTo((width * 0.75, bot_y))
    pen.lineTo((stem_right, bot_y))
    pen.closePath()

    pen = None
    glyph.width = width
    glyph.correctDirection()

    print("  Created germandbls (Kaj's design v2)")

def main():
    print(f"Opening font: {INPUT_FONT}")
    font = fontforge.open(INPUT_FONT)

    print(f"\nFont info:")
    print(f"  Family: {font.familyname}")
    print(f"  Em size: {font.em}")

    # Define all characters to create
    chars_to_create = [
        # Swedish (lowercase)
        ('a', 0x00E4, 'adieresis', 'dieresis', False),  # ä
        ('a', 0x00E5, 'aring', 'ring', False),          # å
        ('o', 0x00F6, 'odieresis', 'dieresis', False),  # ö
        # Swedish (uppercase)
        ('A', 0x00C4, 'Adieresis', 'dieresis', True),   # Ä
        ('A', 0x00C5, 'Aring', 'ring', True),           # Å
        ('O', 0x00D6, 'Odieresis', 'dieresis', True),   # Ö

        # German
        ('u', 0x00FC, 'udieresis', 'dieresis', False),  # ü
        ('U', 0x00DC, 'Udieresis', 'dieresis', True),   # Ü

        # French/Spanish vowels with accents
        ('a', 0x00E0, 'agrave', 'grave', False),        # à
        ('a', 0x00E2, 'acircumflex', 'circumflex', False), # â
        ('e', 0x00E8, 'egrave', 'grave', False),        # è
        ('e', 0x00E9, 'eacute', 'acute', False),        # é
        ('e', 0x00EA, 'ecircumflex', 'circumflex', False), # ê
        ('e', 0x00EB, 'edieresis', 'dieresis', False),  # ë
        ('i', 0x00EC, 'igrave', 'grave', False),        # ì
        ('i', 0x00ED, 'iacute', 'acute', False),        # í
        ('i', 0x00EE, 'icircumflex', 'circumflex', False), # î
        ('i', 0x00EF, 'idieresis', 'dieresis', False),  # ï
        ('o', 0x00F2, 'ograve', 'grave', False),        # ò
        ('o', 0x00F3, 'oacute', 'acute', False),        # ó
        ('o', 0x00F4, 'ocircumflex', 'circumflex', False), # ô
        ('u', 0x00F9, 'ugrave', 'grave', False),        # ù
        ('u', 0x00FA, 'uacute', 'acute', False),        # ú
        ('u', 0x00FB, 'ucircumflex', 'circumflex', False), # û
        ('y', 0x00FD, 'yacute', 'acute', False),        # ý
        ('y', 0x00FF, 'ydieresis', 'dieresis', False),  # ÿ

        # Uppercase versions
        ('A', 0x00C0, 'Agrave', 'grave', True),         # À
        ('A', 0x00C2, 'Acircumflex', 'circumflex', True), # Â
        ('E', 0x00C8, 'Egrave', 'grave', True),         # È
        ('E', 0x00C9, 'Eacute', 'acute', True),         # É
        ('E', 0x00CA, 'Ecircumflex', 'circumflex', True), # Ê
        ('E', 0x00CB, 'Edieresis', 'dieresis', True),   # Ë
        ('I', 0x00CC, 'Igrave', 'grave', True),         # Ì
        ('I', 0x00CD, 'Iacute', 'acute', True),         # Í
        ('I', 0x00CE, 'Icircumflex', 'circumflex', True), # Î
        ('I', 0x00CF, 'Idieresis', 'dieresis', True),   # Ï
        ('O', 0x00D2, 'Ograve', 'grave', True),         # Ò
        ('O', 0x00D3, 'Oacute', 'acute', True),         # Ó
        ('O', 0x00D4, 'Ocircumflex', 'circumflex', True), # Ô
        ('U', 0x00D9, 'Ugrave', 'grave', True),         # Ù
        ('U', 0x00DA, 'Uacute', 'acute', True),         # Ú
        ('U', 0x00DB, 'Ucircumflex', 'circumflex', True), # Û
        ('Y', 0x00DD, 'Yacute', 'acute', True),         # Ý

        # Spanish tilde
        ('n', 0x00F1, 'ntilde', 'tilde', False),        # ñ
        ('N', 0x00D1, 'Ntilde', 'tilde', True),         # Ñ

        # Cedilla
        ('c', 0x00E7, 'ccedilla', 'cedilla', False),    # ç
        ('C', 0x00C7, 'Ccedilla', 'cedilla', True),     # Ç

        # Nordic/Baltic
        ('a', 0x00E3, 'atilde', 'tilde', False),        # ã
        ('o', 0x00F5, 'otilde', 'tilde', False),        # õ
        ('A', 0x00C3, 'Atilde', 'tilde', True),         # Ã
        ('O', 0x00D5, 'Otilde', 'tilde', True),         # Õ
    ]

    print(f"\nCreating {len(chars_to_create)} characters...")
    for base, target_cp, name, diacritic, is_upper in chars_to_create:
        if ord(base) in font:
            create_char_with_diacritic(font, base, target_cp, name, diacritic, is_upper)
        else:
            print(f"  Skipping {name} - base '{base}' not found")

    # Create eszett
    create_eszett(font)

    # Save the modified font
    print(f"\nSaving to: {OUTPUT_FONT}")
    font.generate(OUTPUT_FONT)

    print(f"\nDone! Extended characters added.")
    print(f"Total new glyphs: {len(chars_to_create) + 1}")

    font.close()

if __name__ == "__main__":
    main()
