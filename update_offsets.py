#!/usr/bin/env python3
"""Update mono_reader offsets when hackmud recompiles

This script decompiles Core.dll and extracts the current obfuscated class names
for the terminal output structures. Run this after a game update to keep the
memory scanner working.

Usage:
    python3 update_offsets.py

Requirements:
    - ilspycmd (dotnet tool install -g ilspycmd)
    - Core.dll at the expected path
"""

import subprocess
import re
import json
import os
from pathlib import Path

# Paths
CORE_DLL = Path.home() / ".local/share/Steam/steamapps/common/hackmud/hackmud_lin_Data/Managed/Core.dll"
OUTPUT_DIR = Path("/tmp/hackmud_decompiled")
OFFSETS_FILE = Path(__file__).parent / "mono_offsets.json"

def decompile_dll():
    """Decompile Core.dll using ilspycmd"""
    import shutil
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / "Core.decompiled.cs"

    print(f"Decompiling {CORE_DLL}...")
    # ilspycmd is in ~/.dotnet/tools
    ilspycmd = Path.home() / ".dotnet/tools/ilspycmd"
    if not ilspycmd.exists():
        ilspycmd = "ilspycmd"  # Try PATH

    result = subprocess.run(
        [str(ilspycmd), str(CORE_DLL), "-o", str(output_file)],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None

    # ilspycmd creates a directory with the same name, containing the .cs file
    actual_file = output_file / "Core.decompiled.cs"
    if actual_file.exists():
        print(f"Decompiled to {actual_file}")
        return actual_file
    elif output_file.is_file():
        print(f"Decompiled to {output_file}")
        return output_file
    else:
        print(f"Error: Could not find decompiled file")
        return None

def find_window_class(code: str) -> dict:
    """Find the Window class and its output field type"""
    offsets = {}

    # Find the Window class with gui_text field
    window_match = re.search(
        r'public class (\w+)\s*:\s*MonoBehaviour.*?public TextMeshProUGUI gui_text;.*?public (\w+) output;',
        code, re.DOTALL
    )

    if window_match:
        offsets['window_class'] = window_match.group(1)
        offsets['output_class'] = window_match.group(2)
        print(f"Found Window class: {offsets['window_class']}")
        print(f"Found output type: {offsets['output_class']}")
    else:
        # Try alternative pattern
        gui_text_match = re.search(r'public TextMeshProUGUI gui_text;', code)
        if gui_text_match:
            # Find the class containing it
            start = code.rfind('public class ', 0, gui_text_match.start())
            class_match = re.search(r'public class (\w+)', code[start:start+100])
            if class_match:
                offsets['window_class'] = class_match.group(1)
                print(f"Found Window class: {offsets['window_class']}")

    return offsets

def find_queue_class(code: str, output_class: str) -> dict:
    """Find the Queue<string> field in the output class"""
    offsets = {}

    # Find the output class definition
    pattern = rf'public class {output_class}\s*\{{.*?public Queue<string> (\w+)\s*='
    match = re.search(pattern, code, re.DOTALL)

    if match:
        offsets['queue_field'] = match.group(1)
        print(f"Found Queue<string> field: {offsets['queue_field']}")

    return offsets

def main():
    # Check if Core.dll exists
    if not CORE_DLL.exists():
        print(f"Error: Core.dll not found at {CORE_DLL}")
        print("Make sure hackmud is installed")
        return

    # Decompile
    output_file = decompile_dll()
    if not output_file or not output_file.exists():
        print("Decompilation failed")
        return

    # Read decompiled code
    code = output_file.read_text()

    # Find class names
    offsets = {}
    offsets.update(find_window_class(code))

    if 'output_class' in offsets:
        offsets.update(find_queue_class(code, offsets['output_class']))

    # Add metadata
    offsets['core_dll_path'] = str(CORE_DLL)
    offsets['decompiled_file'] = str(output_file)

    # Save offsets
    with open(OFFSETS_FILE, 'w') as f:
        json.dump(offsets, f, indent=2)

    print(f"\nOffsets saved to {OFFSETS_FILE}:")
    print(json.dumps(offsets, indent=2))

    print("\nTo use these in mono_reader.py, load the JSON and use the class names.")

if __name__ == '__main__':
    main()
