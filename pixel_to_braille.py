#!/usr/bin/env python3
"""
Convert pixel art to Braille Unicode characters for hackmud.
Braille characters (U+2800-U+28FF) encode 8 dots in a 2x4 grid,
allowing much higher resolution than block characters.
"""

from PIL import Image
import sys

# Braille dot positions in Unicode:
# 1 4
# 2 5
# 3 6
# 7 8
# Bit values: dot1=0x01, dot2=0x02, dot3=0x04, dot4=0x08, dot5=0x10, dot6=0x20, dot7=0x40, dot8=0x80
BRAILLE_BASE = 0x2800

def image_to_braille(image_path, width=60, threshold=128, invert=False):
    """Convert image to braille characters."""
    img = Image.open(image_path).convert('L')  # Convert to grayscale

    # Calculate height to maintain aspect ratio
    # Braille chars are 2 wide x 4 tall per cell
    aspect = img.height / img.width
    char_width = width
    char_height = int(width * aspect * 0.5)  # Braille is 2:4 ratio

    # Resize image to fit: each braille char = 2x4 pixels
    pixel_width = char_width * 2
    pixel_height = char_height * 4
    img = img.resize((pixel_width, pixel_height), Image.Resampling.LANCZOS)

    pixels = img.load()

    result = []
    for cy in range(char_height):
        row = ""
        for cx in range(char_width):
            # Get 2x4 pixel block
            px = cx * 2
            py = cy * 4

            # Calculate braille character
            char_code = BRAILLE_BASE

            # Check each dot position
            # Dots 1,2,3 in left column, 4,5,6 in right column, 7,8 at bottom
            dot_positions = [
                (0, 0, 0x01),  # dot 1
                (0, 1, 0x02),  # dot 2
                (0, 2, 0x04),  # dot 3
                (1, 0, 0x08),  # dot 4
                (1, 1, 0x10),  # dot 5
                (1, 2, 0x20),  # dot 6
                (0, 3, 0x40),  # dot 7
                (1, 3, 0x80),  # dot 8
            ]

            for dx, dy, bit in dot_positions:
                x, y = px + dx, py + dy
                if x < pixel_width and y < pixel_height:
                    pixel_val = pixels[x, y]
                    if invert:
                        pixel_val = 255 - pixel_val
                    if pixel_val < threshold:
                        char_code |= bit

            row += chr(char_code)
        result.append(row)

    return '\n'.join(result)

def image_to_braille_colored(image_path, width=60, threshold=128):
    """Convert image to braille with hackmud color codes based on brightness zones."""
    img = Image.open(image_path).convert('RGB')
    gray = img.convert('L')

    # Calculate dimensions
    aspect = img.height / img.width
    char_width = width
    char_height = int(width * aspect * 0.5)

    pixel_width = char_width * 2
    pixel_height = char_height * 4

    img = img.resize((pixel_width, pixel_height), Image.Resampling.LANCZOS)
    gray = gray.resize((pixel_width, pixel_height), Image.Resampling.LANCZOS)

    pixels = img.load()
    gray_pixels = gray.load()

    # Hackmud colors by brightness
    COLORS = [
        ('b', (0, 50)),     # dark gray for very dark
        ('0', (50, 100)),   # gray for dark
        ('D', (100, 150)),  # purple for mid-dark
        ('E', (150, 200)),  # pink for mid-light
        ('1', (200, 256)),  # white for light
    ]

    def get_color(brightness):
        for code, (low, high) in COLORS:
            if low <= brightness < high:
                return code
        return '1'

    result = []
    for cy in range(char_height):
        row = ""
        current_color = None

        for cx in range(char_width):
            px = cx * 2
            py = cy * 4

            # Calculate braille character
            char_code = BRAILLE_BASE
            total_brightness = 0
            dot_count = 0

            dot_positions = [
                (0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04),
                (1, 0, 0x08), (1, 1, 0x10), (1, 2, 0x20),
                (0, 3, 0x40), (1, 3, 0x80),
            ]

            for dx, dy, bit in dot_positions:
                x, y = px + dx, py + dy
                if x < pixel_width and y < pixel_height:
                    gray_val = gray_pixels[x, y]
                    total_brightness += gray_val
                    dot_count += 1
                    if gray_val < threshold:
                        char_code |= bit

            # Get average brightness for color
            avg_brightness = total_brightness // max(dot_count, 1)
            color = get_color(avg_brightness)

            # Add color code if changed
            if color != current_color:
                if current_color is not None:
                    row += "`"
                row += f"`{color}"
                current_color = color

            row += chr(char_code)

        if current_color:
            row += "`"
        result.append(row)

    return '\n'.join(result)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pixel_to_braille.py <image> [width] [threshold] [--color] [--invert]")
        print("  width: character width (default 60)")
        print("  threshold: brightness cutoff 0-255 (default 128)")
        print("  --color: add hackmud color codes")
        print("  --invert: invert brightness")
        sys.exit(1)

    image_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 60
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 128
    use_color = "--color" in sys.argv
    invert = "--invert" in sys.argv

    if use_color:
        result = image_to_braille_colored(image_path, width, threshold)
    else:
        result = image_to_braille(image_path, width, threshold, invert)

    print(result)
    print(f"\n--- Stats ---")
    print(f"Size: {len(result)} bytes")
    print(f"Dimensions: {width}x{len(result.splitlines())} chars")
