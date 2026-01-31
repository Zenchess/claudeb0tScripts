#!/usr/bin/env python3
"""Test address caching feature

This script tests the new address caching in Scanner API:
- First run: Should scan for windows (~5s) and cache addresses
- Second run: Should load from cache (~1ms)
"""

import time
import sys
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / 'python_lib'))

from hackmud.memory import Scanner

def test_caching():
    """Test address caching performance"""
    print("=== Testing Address Caching ===\n")

    # First run - should scan
    print("First connection (should scan)...")
    start = time.perf_counter()

    with Scanner() as scanner:
        # Enable debug to see cache messages
        scanner.set_debug(True)

        # Read shell to verify it works
        lines = scanner.read_window('shell', lines=5)

    elapsed_first = time.perf_counter() - start
    print(f"\n✓ First connection took: {elapsed_first:.3f}s")
    print(f"  Last 5 lines from shell:")
    for line in lines:
        print(f"    {line}")

    # Second run - should use cache
    print("\n\nSecond connection (should use cache)...")
    start = time.perf_counter()

    with Scanner() as scanner:
        scanner.set_debug(True)
        lines = scanner.read_window('shell', lines=5)

    elapsed_second = time.perf_counter() - start
    print(f"\n✓ Second connection took: {elapsed_second:.3f}s")

    # Calculate speedup
    speedup = elapsed_first / elapsed_second if elapsed_second > 0 else 0
    print(f"\n✓ Speedup: {speedup:.1f}x faster")
    print(f"  Time saved: {(elapsed_first - elapsed_second) * 1000:.1f}ms")

    # Check if cache file was created
    cache_file = Path(__file__).parent / 'data' / 'mono_addresses.json'
    if cache_file.exists():
        print(f"\n✓ Cache file created: {cache_file}")
        import json
        with open(cache_file) as f:
            cache = json.load(f)
        print(f"  Cached PID: {cache.get('pid')}")
        print(f"  Cached windows: {len(cache.get('windows', {}))}")
    else:
        print(f"\n✗ Cache file not found: {cache_file}")

if __name__ == '__main__':
    try:
        test_caching()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
