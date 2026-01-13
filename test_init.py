#!/usr/bin/env python3
"""Test init() implementation"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'python_lib'))

from hackmud.memory import Scanner

print("Testing init() implementation...")
print()

# Test 1: Context manager (auto connect + init)
print("[Test 1] Context manager usage")
start = time.perf_counter()
with Scanner() as scanner:
    lines = scanner.read_window('shell', lines=10)
elapsed = time.perf_counter() - start
print(f"✅ Time: {elapsed*1000:.2f}ms")
print(f"   Read {len(lines)} lines")
print()

# Test 2: Manual connect + init
print("[Test 2] Manual usage")
scanner = Scanner()
start = time.perf_counter()
scanner.connect()  # Should call init() automatically
elapsed = time.perf_counter() - start
print(f"✅ connect() time: {elapsed*1000:.2f}ms (includes init)")

start = time.perf_counter()
lines = scanner.read_window('shell', lines=10)
elapsed = time.perf_counter() - start
print(f"✅ read_window() time: {elapsed*1000:.2f}ms (uses cache)")
print(f"   Read {len(lines)} lines")
scanner.close()
print()

print("All tests passed!")
