#!/usr/bin/env python3
"""
Comprehensive benchmark for the hackmud memory Scanner API

Tests:
1. Connection time (cold start + warm start)
2. get_version() performance
3. read_window() with different line counts
4. Multiple sequential reads
5. Context manager vs manual
"""

import sys
import time
from pathlib import Path
from typing import List, Tuple

# Add python_lib to path (go up 3 levels to project root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hackmud.memory import Scanner


def time_function(func, *args, **kwargs) -> Tuple[float, any]:
    """Time a function call and return (duration_ms, result)"""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    duration_ms = (end - start) * 1000
    return duration_ms, result


def benchmark_connection():
    """Test connection establishment time"""
    print("=" * 70)
    print("1. CONNECTION BENCHMARK")
    print("=" * 70)

    # Cold start (includes config generation if needed)
    scanner = Scanner()
    duration, _ = time_function(scanner.connect)
    print(f"Cold start connection: {duration:.2f}ms")
    pid = scanner.pid
    scanner.close()

    # Warm start (configs already exist)
    scanner = Scanner()
    duration, _ = time_function(scanner.connect)
    print(f"Warm start connection: {duration:.2f}ms")
    print(f"Connected to PID: {pid}")
    scanner.close()
    print()


def benchmark_version():
    """Test get_version() performance"""
    print("=" * 70)
    print("2. VERSION DETECTION BENCHMARK")
    print("=" * 70)

    scanner = Scanner()
    scanner.connect()

    # Single call
    duration, version = time_function(scanner.get_version)
    print(f"Single get_version() call: {duration:.2f}ms")
    print(f"Version detected: {version}")

    # Multiple calls (check caching behavior)
    durations = []
    for i in range(5):
        duration, _ = time_function(scanner.get_version)
        durations.append(duration)

    avg = sum(durations) / len(durations)
    print(f"Average over 5 calls: {avg:.2f}ms")
    print(f"Min: {min(durations):.2f}ms, Max: {max(durations):.2f}ms")

    scanner.close()
    print()


def benchmark_read_window():
    """Test read_window() with different line counts"""
    print("=" * 70)
    print("3. READ WINDOW BENCHMARK")
    print("=" * 70)

    scanner = Scanner()
    scanner.connect()

    line_counts = [10, 20, 30, 50, 100]

    for lines in line_counts:
        duration, result = time_function(scanner.read_window, 'shell', lines=lines)
        actual_lines = len(result)
        print(f"read_window('shell', lines={lines:3d}): {duration:6.2f}ms (got {actual_lines} lines)")

    print()

    # Test chat window
    duration, result = time_function(scanner.read_window, 'chat', lines=20)
    actual_lines = len(result)
    print(f"read_window('chat', lines=20): {duration:6.2f}ms (got {actual_lines} lines)")

    scanner.close()
    print()


def benchmark_sequential_reads():
    """Test multiple sequential read operations"""
    print("=" * 70)
    print("4. SEQUENTIAL READS BENCHMARK")
    print("=" * 70)

    scanner = Scanner()
    scanner.connect()

    total_start = time.perf_counter()
    operations = []

    # Perform a realistic sequence of operations
    ops = [
        ('version', lambda: scanner.get_version()),
        ('shell_30', lambda: scanner.read_window('shell', lines=30)),
        ('chat_20', lambda: scanner.read_window('chat', lines=20)),
        ('version', lambda: scanner.get_version()),
        ('shell_10', lambda: scanner.read_window('shell', lines=10)),
    ]

    for op_name, op_func in ops:
        duration, _ = time_function(op_func)
        operations.append((op_name, duration))
        print(f"{op_name:12s}: {duration:6.2f}ms")

    total_end = time.perf_counter()
    total_duration = (total_end - total_start) * 1000

    print(f"\nTotal sequence time: {total_duration:.2f}ms")
    print(f"Average per operation: {total_duration/len(ops):.2f}ms")

    scanner.close()
    print()


def benchmark_context_manager():
    """Compare context manager vs manual usage"""
    print("=" * 70)
    print("5. CONTEXT MANAGER vs MANUAL")
    print("=" * 70)

    # Context manager
    def use_context_manager():
        with Scanner() as scanner:
            version = scanner.get_version()
            lines = scanner.read_window('shell', lines=20)
            return version, lines

    duration_cm, _ = time_function(use_context_manager)
    print(f"Context manager (with Scanner()): {duration_cm:.2f}ms")

    # Manual
    def use_manual():
        scanner = Scanner()
        scanner.connect()
        version = scanner.get_version()
        lines = scanner.read_window('shell', lines=20)
        scanner.close()
        return version, lines

    duration_manual, _ = time_function(use_manual)
    print(f"Manual (connect/close):           {duration_manual:.2f}ms")

    print(f"\nDifference: {abs(duration_cm - duration_manual):.2f}ms")
    print()


def benchmark_persistent_connection():
    """Test performance with persistent connection vs recreating"""
    print("=" * 70)
    print("6. PERSISTENT CONNECTION vs RECREATE")
    print("=" * 70)

    # Persistent connection (keep scanner alive)
    scanner = Scanner()
    scanner.connect()

    persistent_times = []
    for i in range(10):
        duration, _ = time_function(scanner.read_window, 'shell', lines=30)
        persistent_times.append(duration)

    scanner.close()

    avg_persistent = sum(persistent_times) / len(persistent_times)
    print(f"Persistent connection (10 reads): {avg_persistent:.2f}ms avg")
    print(f"  Min: {min(persistent_times):.2f}ms, Max: {max(persistent_times):.2f}ms")

    # Recreate each time
    recreate_times = []
    for i in range(10):
        def read_once():
            scanner = Scanner()
            scanner.connect()
            result = scanner.read_window('shell', lines=30)
            scanner.close()
            return result

        duration, _ = time_function(read_once)
        recreate_times.append(duration)

    avg_recreate = sum(recreate_times) / len(recreate_times)
    print(f"\nRecreate each time (10 reads):    {avg_recreate:.2f}ms avg")
    print(f"  Min: {min(recreate_times):.2f}ms, Max: {max(recreate_times):.2f}ms")

    speedup = avg_recreate / avg_persistent
    print(f"\nSpeedup with persistent connection: {speedup:.1f}x faster")
    print()


def main():
    """Run all benchmarks"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "HACKMUD MEMORY SCANNER API BENCHMARK" + " " * 16 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    try:
        benchmark_connection()
        benchmark_version()
        benchmark_read_window()
        benchmark_sequential_reads()
        benchmark_context_manager()
        benchmark_persistent_connection()

        print("=" * 70)
        print("BENCHMARK COMPLETE")
        print("=" * 70)
        print()
        print("Key Takeaways:")
        print("- Use persistent connections for multiple operations")
        print("- Context manager (with Scanner()) is convenient with no overhead")
        print("- Config auto-generation adds ~5-10s on first run only")
        print()

    except Exception as e:
        print(f"✗ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
