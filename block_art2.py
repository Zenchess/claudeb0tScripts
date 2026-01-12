#!/usr/bin/env python3
"""
Block character converter - proper escaping for hackmud
"""

from PIL import Image
import sys

COLORS = {
    (0,0,0): '0',
    (63,63,63): '0',
    (155,155,155): 'C',
    (255,255,255): '1',
    (255,0,0): '4',
    (255,128,0): 'F',
    (251,200,3): 'F',  # yellow -> orange
    (176,53,238): '5',  # purple
    (255,0,236): '5',   # magenta -> purple
    (0,112,221): '3',   # blue
    (0,255,255): 'N',   # cyan
    (30,255,0): '2',    # green
}

def nearest(r, g, b, a):
    if a < 128:
        return None
    best = 'C'
    best_dist = float('inf')
    for (cr, cg, cb), code in COLORS.items():
        d = (r-cr)**2 + (g-cg)**2 + (b-cb)**2
        if d < best_dist:
            best_dist = d
            best = code
    return best

def convert(image_path):
    img = Image.open(image_path).convert('RGBA')
    w, h = img.size
    pixels = img.load()

    lines = []
    for y in range(0, h - 1, 2):
        line = ''
        cur = None
        for x in range(w):
            r1, g1, b1, a1 = pixels[x, y]
            r2, g2, b2, a2 = pixels[x, y + 1]
            tc = nearest(r1, g1, b1, a1)
            bc = nearest(r2, g2, b2, a2)

            if tc is None and bc is None:
                ch = ' '
                c = None
            elif tc is None:
                ch = '\u2584'  # ▄
                c = bc
            elif bc is None:
                ch = '\u2580'  # ▀
                c = tc
            elif tc == bc:
                ch = '\u2588'  # █
                c = tc
            else:
                ch = '\u2580'  # ▀
                c = tc

            if c and c != cur:
                line += '`' + c
                cur = c
            line += ch
        lines.append(line.rstrip())

    return '\n'.join(lines)

def to_script(art):
    # Escape for JS string - but keep backticks as literal backticks
    escaped = art.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    return 'function(c,a){return"' + escaped + '"}'

if __name__ == '__main__':
    art = convert(sys.argv[1])

    if '-o' in sys.argv:
        script = to_script(art)
        idx = sys.argv.index('-o')
        with open(sys.argv[idx + 1], 'w') as f:
            f.write(script)
        print(f"Size: {len(script)}")
    else:
        print(art)
