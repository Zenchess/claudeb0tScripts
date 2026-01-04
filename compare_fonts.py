#!/usr/bin/env fontforge
"""
Font Comparison Script - Compare two font files and report differences

Usage: fontforge -script compare_fonts.py original.ttf modified.ttf

Reports:
- Added glyphs (in modified but not original)
- Removed glyphs (in original but not modified)
- Modified glyphs (different contour count, bounding box, or width)
- Metadata differences (font name, em size, etc.)
"""

import fontforge
import sys

def get_glyph_info(glyph):
    """Get comparable info about a glyph."""
    try:
        bbox = glyph.boundingBox()
        return {
            'width': glyph.width,
            'contours': len(glyph.layers[glyph.activeLayer]),
            'bbox': bbox,
            'name': glyph.glyphname
        }
    except:
        return None

def compare_fonts(orig_path, mod_path):
    """Compare two fonts and print differences."""

    print(f"=" * 60)
    print(f"FONT COMPARISON REPORT")
    print(f"=" * 60)
    print(f"\nOriginal: {orig_path}")
    print(f"Modified: {mod_path}")
    print()

    # Open fonts
    try:
        orig = fontforge.open(orig_path)
        mod = fontforge.open(mod_path)
    except Exception as e:
        print(f"Error opening fonts: {e}")
        return

    # Compare metadata
    print("-" * 60)
    print("METADATA COMPARISON")
    print("-" * 60)

    metadata_fields = [
        ('familyname', 'Family Name'),
        ('fullname', 'Full Name'),
        ('fontname', 'Font Name'),
        ('em', 'Em Size'),
        ('ascent', 'Ascent'),
        ('descent', 'Descent'),
    ]

    for field, label in metadata_fields:
        orig_val = getattr(orig, field, None)
        mod_val = getattr(mod, field, None)
        if orig_val != mod_val:
            print(f"  {label}: '{orig_val}' -> '{mod_val}' [CHANGED]")
        else:
            print(f"  {label}: {orig_val}")

    # Get all glyphs from both fonts
    orig_glyphs = set()
    mod_glyphs = set()

    for glyph in orig.glyphs():
        if glyph.unicode != -1:
            orig_glyphs.add(glyph.unicode)

    for glyph in mod.glyphs():
        if glyph.unicode != -1:
            mod_glyphs.add(glyph.unicode)

    # Find added, removed, common
    added = mod_glyphs - orig_glyphs
    removed = orig_glyphs - mod_glyphs
    common = orig_glyphs & mod_glyphs

    # Report added glyphs
    print()
    print("-" * 60)
    print(f"ADDED GLYPHS ({len(added)} new)")
    print("-" * 60)

    if added:
        for cp in sorted(added):
            glyph = mod[cp]
            info = get_glyph_info(glyph)
            if info:
                print(f"  + U+{cp:04X} '{chr(cp)}' ({info['name']}) width={info['width']}")
    else:
        print("  (none)")

    # Report removed glyphs
    print()
    print("-" * 60)
    print(f"REMOVED GLYPHS ({len(removed)} removed)")
    print("-" * 60)

    if removed:
        for cp in sorted(removed):
            glyph = orig[cp]
            print(f"  - U+{cp:04X} '{chr(cp)}' ({glyph.glyphname})")
    else:
        print("  (none)")

    # Check for modified glyphs
    print()
    print("-" * 60)
    print("MODIFIED GLYPHS (checking common glyphs)")
    print("-" * 60)

    modified_count = 0
    width_mismatches = []

    for cp in sorted(common):
        orig_glyph = orig[cp]
        mod_glyph = mod[cp]

        orig_info = get_glyph_info(orig_glyph)
        mod_info = get_glyph_info(mod_glyph)

        if orig_info and mod_info:
            changes = []

            if orig_info['width'] != mod_info['width']:
                changes.append(f"width: {orig_info['width']} -> {mod_info['width']}")
                width_mismatches.append((cp, orig_info['width'], mod_info['width']))

            if orig_info['contours'] != mod_info['contours']:
                changes.append(f"contours: {orig_info['contours']} -> {mod_info['contours']}")

            # Check bounding box (with some tolerance)
            if orig_info['bbox'] and mod_info['bbox']:
                orig_bbox = orig_info['bbox']
                mod_bbox = mod_info['bbox']
                bbox_diff = max(
                    abs(orig_bbox[0] - mod_bbox[0]),
                    abs(orig_bbox[1] - mod_bbox[1]),
                    abs(orig_bbox[2] - mod_bbox[2]),
                    abs(orig_bbox[3] - mod_bbox[3])
                )
                if bbox_diff > 10:  # tolerance of 10 units
                    changes.append(f"bbox changed (diff={bbox_diff:.0f})")

            if changes:
                modified_count += 1
                char_repr = chr(cp) if 32 <= cp < 127 else f"U+{cp:04X}"
                print(f"  ~ '{char_repr}' ({orig_glyph.glyphname}): {', '.join(changes)}")

    if modified_count == 0:
        print("  (no modifications to existing glyphs)")

    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Original glyphs: {len(orig_glyphs)}")
    print(f"  Modified glyphs: {len(mod_glyphs)}")
    print(f"  Added: {len(added)}")
    print(f"  Removed: {len(removed)}")
    print(f"  Changed: {modified_count}")

    # Monospace check
    print()
    print("-" * 60)
    print("MONOSPACE CHECK")
    print("-" * 60)

    widths = {}
    for cp in mod_glyphs:
        glyph = mod[cp]
        w = glyph.width
        if w not in widths:
            widths[w] = []
        widths[w].append(cp)

    if len(widths) == 1:
        print(f"  All glyphs have same width: {list(widths.keys())[0]} - MONOSPACE OK")
    else:
        print(f"  WARNING: Multiple widths found:")
        for w, cps in sorted(widths.items()):
            print(f"    Width {w}: {len(cps)} glyphs")
            if len(cps) <= 10:
                chars = [f"'{chr(cp)}'" if 32 <= cp < 127 else f"U+{cp:04X}" for cp in cps[:10]]
                print(f"      Examples: {', '.join(chars)}")

    print()
    print("=" * 60)
    print("END OF REPORT")
    print("=" * 60)

    orig.close()
    mod.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: fontforge -script compare_fonts.py original.ttf modified.ttf")
        sys.exit(1)

    compare_fonts(sys.argv[1], sys.argv[2])
