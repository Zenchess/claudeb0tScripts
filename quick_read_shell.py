#!/usr/bin/env python3
"""Quick script to read hackmud shell output"""
import sys
sys.path.insert(0, 'python_lib')

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()

# Read last 30 lines from shell
lines = scanner.read_window('shell', lines=30)
for line in lines:
    print(line)
