# White Rabbit Font Modification Documentation

## Overview

This document describes how Swedish and extended Latin characters were added to the White Rabbit (whitrabt.ttf) font using FontForge's Python scripting interface.

## Problem

The original `whitrabt.ttf` font only contains basic ASCII characters (U+0000-U+007F). It lacks:
- Swedish characters: å ä ö Å Ä Ö
- German characters: ü Ü ß
- French accented vowels: é è ê ë à â ç
- Spanish: ñ Ñ
- And other Latin-1 supplement characters

## Solution

Use FontForge's Python scripting to:
1. Open the original font
2. Copy base glyphs (a, e, i, o, u, n, c, etc.)
3. Draw diacritical marks on top of the copied glyphs
4. Save as a new font file

## Technical Approach

### Tool Used
- **FontForge** - Open source font editor with Python scripting support
- Run scripts with: `fontforge -script scriptname.py`

### Drawing Method
Since FontForge's curve functions have complex argument requirements, we used:
- **Square dots** for umlauts (dieresis) - simple 4-point polygons
- **Polygon approximation** for rings (12-segment circles)
- **Triangle/trapezoid shapes** for acute, grave, circumflex, tilde, caron
- **Hook shape** for cedilla

### Key Code Pattern

```python
import fontforge

def create_char_with_diacritic(font, base, target_codepoint, name, diacritic):
    # 1. Copy base glyph to target slot
    font.selection.select(base)
    font.copy()
    font.selection.select(("unicode",), target_codepoint)
    font.paste()

    glyph = font[target_codepoint]
    glyph.glyphname = name

    # 2. Get metrics for positioning
    bbox = glyph.boundingBox()  # (xmin, ymin, xmax, ymax)
    center_x = (bbox[0] + bbox[2]) / 2
    top_y = bbox[3]

    # 3. Draw diacritical mark using glyphPen
    pen = glyph.glyphPen()

    if diacritic == 'dieresis':
        # Draw two square dots above the letter
        draw_square_dot(pen, center_x - spacing, top_y + height, size)
        draw_square_dot(pen, center_x + spacing, top_y + height, size)

    pen = None  # Close pen
    glyph.width = original_width
```

### Diacritical Mark Drawing Functions

#### Square Dot (for umlauts)
```python
def draw_square_dot(pen, cx, cy, size):
    half = size / 2
    pen.moveTo((cx - half, cy - half))
    pen.lineTo((cx - half, cy + half))
    pen.lineTo((cx + half, cy + half))
    pen.lineTo((cx + half, cy - half))
    pen.closePath()
```

#### Ring (for å, Å)
```python
def draw_ring_as_polygon(pen, cx, cy, outer_r, inner_r, segments=12):
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
```

## Files Created

| File | Description |
|------|-------------|
| `whitrabt_swedish.ttf` | Original + 6 Swedish characters |
| `whitrabt_extended.ttf` | Original + 52 extended Latin characters |
| `add_swedish_chars.py` | Script for Swedish characters only |
| `add_extended_chars.py` | Script for full Latin-1 supplement |
| `font_preview2.png` | Screenshot showing the new characters |

## Characters Added

### Swedish (6)
- å (U+00E5) - a with ring above
- ä (U+00E4) - a with dieresis
- ö (U+00F6) - o with dieresis
- Å (U+00C5) - A with ring above
- Ä (U+00C4) - A with dieresis
- Ö (U+00D6) - O with dieresis

### German (3)
- ü (U+00FC) - u with dieresis
- Ü (U+00DC) - U with dieresis
- ß (U+00DF) - sharp s (eszett)

### French/European Vowels (40+)
- Grave accents: à è ì ò ù (and uppercase)
- Acute accents: é í ó ú ý (and uppercase)
- Circumflex: â ê î ô û (and uppercase)
- Dieresis: ë ï ÿ (and uppercase)
- Cedilla: ç Ç
- Tilde: ã ñ õ (and uppercase)

## Running the Scripts

```bash
# Install FontForge (Arch Linux)
sudo pacman -S fontforge

# Run Swedish-only script
fontforge -script add_swedish_chars.py

# Run extended script
fontforge -script add_extended_chars.py
```

## Customization

To adjust the size/position of diacritical marks, modify these parameters in the script:

```python
# For umlauts
dot_size = width * 0.12      # Size of each dot
dot_spacing = width * 0.18   # Distance between dot centers
dot_y = top_y + width * 0.14 # Height above letter

# For rings
outer_r = width * 0.13       # Outer radius
inner_r = width * 0.06       # Inner radius (hole)
ring_y = top_y + width * 0.19 # Height above letter
```

## Font Metrics Reference

Original White Rabbit font:
- Em size: 2100
- Glyph width: 1200 (monospace)
- Lowercase height: ~1000 units
- Uppercase height: ~1400 units

## Notes

- The original font has some inconsistencies in Mac vs Windows naming tables (warnings during load are normal)
- The font uses a simple encoding, so adding characters in the Latin-1 supplement range (U+00C0-U+00FF) works well
- For more complex scripts or higher Unicode ranges, additional encoding configuration may be needed

## Author

Created by claudeb0t using FontForge Python scripting
Date: 2026-01-03
