#!/usr/bin/env python3
"""
Collect all public scripts from hackmud sectors
Stores them in a JSON database for the webui script browser
"""

import sys
import json
import time
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / 'python_lib'))
from hackmud.memory import Scanner

# Security levels to scan
SEC_LEVELS = ['fullsec', 'highsec', 'midsec', 'lowsec', 'nullsec']

def send_command(cmd):
    """Send command to hackmud"""
    import subprocess
    subprocess.run(['python3', 'send_command.py', cmd], capture_output=True)
    time.sleep(2)  # Wait for command to execute

def read_shell_output(scanner, lines=30):
    """Read and return shell output"""
    output = scanner.read_window('shell', lines=lines, preserve_colors=False)
    return [line.replace('\\\\', '\\') for line in output]

def parse_sector_list(lines):
    """Parse sector names from script output"""
    sectors = []
    # Look for lines after the command that contain sector codes
    # Sectors are typically formatted like: SEC_1234
    for line in lines:
        words = line.split()
        for word in words:
            if '_' in word and len(word) > 3:
                sectors.append(word)
    return list(set(sectors))  # Remove duplicates

def parse_script_list(lines):
    """Parse script names from sector listing"""
    scripts = []
    # Scripts are user.scriptname format
    for line in lines:
        words = line.split()
        for word in words:
            if '.' in word and not word.startswith('>>'):
                scripts.append(word)
    return list(set(scripts))

def collect_all_scripts():
    """Main function to collect all public scripts"""
    print("Starting public script collection...")
    print("=" * 60)

    scanner = Scanner()
    scanner.connect()
    print(f"Connected to hackmud (PID: {scanner.pid})")

    all_scripts = {}

    for sec_level in SEC_LEVELS:
        print(f"\nScanning {sec_level.upper()}...")

        # Get sectors for this security level
        send_command(f"scripts.{sec_level}")
        time.sleep(1)
        output = read_shell_output(scanner, lines=100)

        sectors = parse_sector_list(output)
        print(f"Found {len(sectors)} sectors in {sec_level}")

        # Scan each sector
        for i, sector in enumerate(sectors, 1):  # Scan ALL sectors
            print(f"  [{i}/{len(sectors)}] Scanning sector {sector}...")

            # Join the sector channel
            send_command(f"chats.join{{channel:\"{sector}\"}}")
            time.sleep(1)

            # List scripts in sector
            send_command(f"scripts.{sec_level}{{sector:\"{sector}\"}}")
            time.sleep(2)
            output = read_shell_output(scanner, lines=100)

            scripts = parse_script_list(output)

            for script in scripts:
                if script not in all_scripts:
                    all_scripts[script] = {
                        'name': script,
                        'security': sec_level,
                        'sector': sector,
                        'description': ''  # Will need to get this separately
                    }

            print(f"    Found {len(scripts)} scripts (total: {len(all_scripts)})")

            # Leave the sector channel
            send_command(f"chats.leave{{channel:\"{sector}\"}}")
            time.sleep(1)

    # Save to JSON
    output_file = Path(__file__).parent / 'public_scripts.json'
    with open(output_file, 'w') as f:
        json.dump(all_scripts, f, indent=2)

    print("\n" + "=" * 60)
    print(f"Collection complete!")
    print(f"Total scripts found: {len(all_scripts)}")
    print(f"Saved to: {output_file}")

    return all_scripts

if __name__ == '__main__':
    try:
        scripts = collect_all_scripts()
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
