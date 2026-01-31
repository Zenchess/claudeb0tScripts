#!/usr/bin/env python3
"""
CLI wrapper for Scanner API - used for CLI vs API benchmarking

Usage: python cli_read.py [window] [lines]
"""

import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hackmud.memory import Scanner

def main():
    window = sys.argv[1] if len(sys.argv) > 1 else 'shell'
    lines = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    with Scanner() as scanner:
        result = scanner.read_window(window, lines=lines)
        for line in result:
            print(line)

if __name__ == '__main__':
    main()
