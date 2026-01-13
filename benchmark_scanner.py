#!/usr/bin/env python3
"""Benchmark and test protocol for Scanner API"""

import sys
import time
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / 'python_lib'))

from hackmud.memory import Scanner
from hackmud.memory.exceptions import GameNotFoundError, WindowNotFoundError


def benchmark(name, func, *args, **kwargs):
    """Run a function and measure its execution time"""
    start = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed, None
    except Exception as e:
        elapsed = time.perf_counter() - start
        return None, elapsed, e


def main():
    print("=" * 70)
    print("Scanner API Benchmark & Test Protocol")
    print("=" * 70)
    print()

    # Test 1: Scanner initialization
    print("[Test 1] Scanner initialization")
    scanner, t_init, err = benchmark("init", Scanner)
    if err:
        print(f"❌ FAIL: {err}")
        return 1
    print(f"✅ PASS - Time: {t_init*1000:.2f}ms")
    print()

    # Test 2: Connect to game
    print("[Test 2] Connect to game process")
    _, t_connect, err = benchmark("connect", scanner.connect)
    if err:
        print(f"❌ FAIL: {err}")
        if isinstance(err, GameNotFoundError):
            print("   Note: Start hackmud first")
        return 1
    print(f"✅ PASS - Time: {t_connect*1000:.2f}ms")
    print(f"   PID: {scanner.pid}")
    print()

    # Test 3: Load configuration
    print("[Test 3] Configuration loading")
    print(f"✅ Offsets loaded: {len(scanner.offsets)} keys")
    print(f"✅ Names loaded: {len(scanner.names)} keys")
    print(f"✅ Fixed names loaded: {len(scanner.names_fixed)} keys")
    print(f"✅ Constants loaded: {len(scanner.constants)} keys")
    print()

    # Test 4: Find window vtable
    print("[Test 4] Find Window vtable (first call)")
    vtable, t_vtable, err = benchmark("find_vtable", scanner._find_window_vtable)
    if err:
        print(f"❌ FAIL: {err}")
    elif not vtable:
        print(f"❌ FAIL: Vtable not found")
    else:
        print(f"✅ PASS - Time: {t_vtable*1000:.2f}ms")
        print(f"   Vtable: 0x{vtable:x}")
    print()

    # Test 5: Scan for all windows
    print("[Test 5] Scan for all windows (first call)")
    _, t_scan, err = benchmark("scan_windows", scanner._scan_windows)
    if err:
        print(f"❌ FAIL: {err}")
    else:
        print(f"✅ PASS - Time: {t_scan*1000:.2f}ms")
        print(f"   Windows found: {list(scanner._windows_cache.keys())}")
    print()

    # Test 6: Read shell window
    print("[Test 6] Read shell window (30 lines)")
    lines, t_read_shell, err = benchmark("read_shell", scanner.read_window, 'shell', 30)
    if err:
        print(f"❌ FAIL: {err}")
    else:
        print(f"✅ PASS - Time: {t_read_shell*1000:.2f}ms")
        print(f"   Lines read: {len(lines)}")
        if lines:
            preview = lines[-1][:60] + '...' if len(lines[-1]) > 60 else lines[-1]
            print(f"   Last line: {preview}")
    print()

    # Test 7: Read shell again (cached)
    print("[Test 7] Read shell window again (cached lookup)")
    lines2, t_read_shell2, err = benchmark("read_shell_cached", scanner.read_window, 'shell', 30)
    if err:
        print(f"❌ FAIL: {err}")
    else:
        print(f"✅ PASS - Time: {t_read_shell2*1000:.2f}ms")
        speedup = t_read_shell / t_read_shell2 if t_read_shell2 > 0 else float('inf')
        print(f"   Speedup from cache: {speedup:.1f}x faster")
    print()

    # Test 8: Read chat window
    print("[Test 8] Read chat window (20 lines)")
    lines, t_read_chat, err = benchmark("read_chat", scanner.read_window, 'chat', 20)
    if err:
        print(f"❌ FAIL: {err}")
    else:
        print(f"✅ PASS - Time: {t_read_chat*1000:.2f}ms")
        print(f"   Lines read: {len(lines)}")
    print()

    # Test 9: Read badge window
    print("[Test 9] Read badge window")
    lines, t_read_badge, err = benchmark("read_badge", scanner.read_window, 'badge', 50)
    if err:
        print(f"❌ FAIL: {err}")
    else:
        print(f"✅ PASS - Time: {t_read_badge*1000:.2f}ms")
        print(f"   Lines read: {len(lines)}")
    print()

    # Test 10: Read with color preservation
    print("[Test 10] Read with color tags preserved")
    lines, t_colors, err = benchmark("read_colors", scanner.read_window, 'shell', 10, True)
    if err:
        print(f"❌ FAIL: {err}")
    else:
        print(f"✅ PASS - Time: {t_colors*1000:.2f}ms")
        has_tags = any('<color' in line for line in lines)
        print(f"   Color tags present: {has_tags}")
    print()

    # Test 11: Read invalid window
    print("[Test 11] Read invalid window (error handling)")
    try:
        scanner.read_window('invalid_window')
        print(f"❌ FAIL: Should have raised ValueError")
    except ValueError as e:
        print(f"✅ PASS - Correctly raised ValueError")
        print(f"   Message: {str(e)[:60]}")
    except Exception as e:
        print(f"❌ FAIL: Wrong exception type: {type(e).__name__}")
    print()

    # Test 12: Close scanner
    print("[Test 12] Close scanner")
    _, t_close, err = benchmark("close", scanner.close)
    if err:
        print(f"❌ FAIL: {err}")
    else:
        print(f"✅ PASS - Time: {t_close*1000:.2f}ms")
    print()

    # Summary
    print("=" * 70)
    print("Benchmark Summary")
    print("=" * 70)
    print(f"Scanner init:         {t_init*1000:>8.2f}ms")
    print(f"Connect to game:      {t_connect*1000:>8.2f}ms")
    print(f"Find vtable:          {t_vtable*1000:>8.2f}ms")
    print(f"Scan windows:         {t_scan*1000:>8.2f}ms")
    print(f"Read shell (first):   {t_read_shell*1000:>8.2f}ms")
    print(f"Read shell (cached):  {t_read_shell2*1000:>8.2f}ms")
    print(f"Read chat:            {t_read_chat*1000:>8.2f}ms")
    print(f"Read badge:           {t_read_badge*1000:>8.2f}ms")
    print(f"Read with colors:     {t_colors*1000:>8.2f}ms")
    print(f"Close scanner:        {t_close*1000:>8.2f}ms")
    print()
    print(f"Total time:           {(t_init + t_connect + t_vtable + t_scan + t_read_shell + t_read_shell2 + t_read_chat + t_read_badge + t_colors + t_close)*1000:.2f}ms")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
