#!/usr/bin/env python3
"""Quick script to read hackmud version"""
import sys
sys.path.insert(0, 'python_lib')

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()

version = scanner.get_version()
print(f"Hackmud version: {version}")
