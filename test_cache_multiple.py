#!/usr/bin/env python3
"""Test address caching with multiple rapid connections

This verifies caching works well for typical usage patterns
where you connect, read, disconnect many times.
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'python_lib'))

from hackmud.memory import Scanner

def test_multiple_connections(n=5):
    """Test multiple rapid connections"""
    print(f"=== Testing {n} Rapid Connections ===\n")

    times = []

    for i in range(n):
        print(f"Connection {i+1}/{n}...", end=' ', flush=True)
        start = time.perf_counter()

        with Scanner() as scanner:
            lines = scanner.read_window('shell', lines=3)
            # Verify we got data
            assert len(lines) > 0, "Failed to read shell"

        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"{elapsed:.3f}s")

    # Statistics
    avg = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"\n✓ Statistics:")
    print(f"  Average: {avg:.3f}s")
    print(f"  Min:     {min_time:.3f}s")
    print(f"  Max:     {max_time:.3f}s")
    print(f"  Total:   {sum(times):.3f}s")

    # All should be fast (< 0.5s) after first scan
    if all(t < 0.5 for t in times[1:]):
        print(f"\n✓ All connections after first used cache (< 0.5s)")
    else:
        print(f"\n✗ Some connections were slow:")
        for i, t in enumerate(times):
            if t >= 0.5:
                print(f"    Connection {i+1}: {t:.3f}s")

if __name__ == '__main__':
    try:
        test_multiple_connections(10)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
