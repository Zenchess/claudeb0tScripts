#!/usr/bin/env fontforge
"""Merge the eszett (ß) from Kaj's font into whitrabt_extended.ttf"""
import fontforge

# Open both fonts
kaj_font = fontforge.open("/home/jacob/hackmud/WhiteRabbitHackmudExtended.ttf")
my_font = fontforge.open("/home/jacob/hackmud/whitrabt_extended.ttf")

# Check if Kaj's font has the eszett
eszett_cp = 0x00DF
if eszett_cp in kaj_font:
    print(f"Found eszett in Kaj's font!")
    kaj_glyph = kaj_font[eszett_cp]
    print(f"  Name: {kaj_glyph.glyphname}")
    print(f"  Width: {kaj_glyph.width}")
    
    # Copy the glyph
    kaj_font.selection.select(("unicode",), eszett_cp)
    kaj_font.copy()
    
    # Paste into my font
    my_font.selection.select(("unicode",), eszett_cp)
    my_font.paste()
    
    # Set width to match my font's monospace width (1200)
    my_font[eszett_cp].width = 1200
    
    print(f"  Copied eszett to my font!")
    
    # Save
    my_font.generate("/home/jacob/hackmud/whitrabt_extended.ttf")
    print("Saved updated font!")
else:
    print("Eszett not found in Kaj's font")

kaj_font.close()
my_font.close()
