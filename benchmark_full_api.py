#!/usr/bin/env python3
"""
Comprehensive benchmark of the hackmud memory scanner full API.

Tests both:
1. Scanner class (low-level API)
2. read_vtable.py (CLI tool / high-level API)
"""

import sys
import time
import subprocess
from pathlib import Path

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / "python_lib"))

from hackmud.memory import Scanner

def format_time(seconds):
    """Format time in ms with color"""
    ms = seconds * 1000
    if ms < 10:
        color = '\033[32m'  # Green - fast
    elif ms < 50:
        color = '\033[33m'  # Yellow - moderate
    else:
        color = '\033[31m'  # Red - slow
    return f"{color}{ms:>8.2f}ms\033[0m"

def benchmark_scanner_class():
    """Benchmark the Scanner class (low-level API)"""
    print("=" * 80)
    print("PART 1: Scanner Class (Low-Level API)")
    print("=" * 80)
    print()

    results = {}
    scanner = Scanner()

    # Connect
    print("[1] Connection:")
    start = time.time()
    scanner.connect()
    elapsed = time.time() - start
    print(f"  connect()           {format_time(elapsed)}  ✓ PID {scanner.pid}")
    results['connect'] = elapsed
    print()

    # Get version (3 runs)
    print("[2] Version Detection:")
    version_times = []
    for i in range(3):
        start = time.time()
        version = scanner.get_version()
        elapsed = time.time() - start
        print(f"  get_version() #{i+1}  {format_time(elapsed)}  ✓ {version}")
        version_times.append(elapsed)
    results['version_avg'] = sum(version_times) / len(version_times)
    print()

    # Close
    print("[3] Disconnection:")
    start = time.time()
    scanner.close()
    elapsed = time.time() - start
    print(f"  close()             {format_time(elapsed)}  ✓")
    results['close'] = elapsed
    print()

    return results

def benchmark_cli_tool():
    """Benchmark read_vtable.py (CLI tool / high-level API)"""
    print("=" * 80)
    print("PART 2: read_vtable.py (CLI Tool / High-Level API)")
    print("=" * 80)
    print()

    results = {}

    # Test shell reading with different line counts
    print("[1] Shell Reading:")
    for lines in [10, 20, 40]:
        start = time.time()
        result = subprocess.run(
            ['python3', 'memory_scanner/read_vtable.py', str(lines)],
            capture_output=True,
            text=True,
            timeout=10
        )
        elapsed = time.time() - start

        if result.returncode == 0:
            line_count = len(result.stdout.strip().split('\n'))
            print(f"  read_vtable.py {lines:<2}   {format_time(elapsed)}  ✓ {line_count} lines")
        else:
            print(f"  read_vtable.py {lines:<2}   {format_time(elapsed)}  ✗ Failed")

        results[f'shell_{lines}'] = elapsed
    print()

    # Test chat reading
    print("[2] Chat Reading:")
    for lines in [10, 20, 40]:
        start = time.time()
        result = subprocess.run(
            ['python3', 'memory_scanner/read_vtable.py', str(lines), '--chat'],
            capture_output=True,
            text=True,
            timeout=10
        )
        elapsed = time.time() - start

        if result.returncode == 0:
            line_count = len(result.stdout.strip().split('\n'))
            print(f"  read_vtable.py {lines:<2}   {format_time(elapsed)}  ✓ {line_count} lines (chat)")
        else:
            print(f"  read_vtable.py {lines:<2}   {format_time(elapsed)}  ✗ Failed")

        results[f'chat_{lines}'] = elapsed
    print()

    # Test with --debug flag
    print("[3] Debug Mode:")
    start = time.time()
    result = subprocess.run(
        ['python3', 'memory_scanner/read_vtable.py', '20', '--debug'],
        capture_output=True,
        text=True,
        timeout=10
    )
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"  read_vtable.py --debug  {format_time(elapsed)}  ✓")
    else:
        print(f"  read_vtable.py --debug  {format_time(elapsed)}  ✗ Failed")
    results['debug_mode'] = elapsed
    print()

    # Test with --colors flag
    print("[4] Color Preservation:")
    start = time.time()
    result = subprocess.run(
        ['python3', 'memory_scanner/read_vtable.py', '20', '--colors'],
        capture_output=True,
        text=True,
        timeout=10
    )
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"  read_vtable.py --colors {format_time(elapsed)}  ✓")
    else:
        print(f"  read_vtable.py --colors {format_time(elapsed)}  ✗ Failed")
    results['colors_mode'] = elapsed
    print()

    return results

def print_summary(scanner_results, cli_results):
    """Print benchmark summary"""
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    # Scanner class stats
    print("Low-Level API (Scanner class):")
    print(f"  Connection:       {format_time(scanner_results['connect'])}")
    print(f"  Version (avg):    {format_time(scanner_results['version_avg'])}")
    print(f"  Disconnection:    {format_time(scanner_results['close'])}")
    print()

    # CLI tool stats
    print("High-Level API (read_vtable.py):")
    shell_avg = sum(cli_results[f'shell_{lines}'] for lines in [10, 20, 40]) / 3
    chat_avg = sum(cli_results[f'chat_{lines}'] for lines in [10, 20, 40]) / 3
    print(f"  Shell read (avg): {format_time(shell_avg)}")
    print(f"  Chat read (avg):  {format_time(chat_avg)}")
    print(f"  Debug mode:       {format_time(cli_results['debug_mode'])}")
    print(f"  Colors mode:      {format_time(cli_results['colors_mode'])}")
    print()

    # Overall assessment
    if shell_avg < 0.1:  # < 100ms
        assessment = "EXCELLENT"
        color = '\033[32m'
    elif shell_avg < 0.5:  # < 500ms
        assessment = "GOOD"
        color = '\033[33m'
    else:
        assessment = "NEEDS OPTIMIZATION"
        color = '\033[31m'

    print(f"Overall Performance: {color}{assessment}\033[0m")
    print()

    # Recommendations
    print("Recommendations:")
    if scanner_results['connect'] > 1.0:
        print("  • Connection is slow (>1s). Check PID detection.")
    if scanner_results['version_avg'] > 0.5:
        print("  • Version detection is slow (>500ms). Pattern search may need optimization.")
    if shell_avg > 0.5:
        print("  • Shell reading is slow (>500ms). Consider caching vtable or reducing memory scans.")
    if all(t < 0.5 for t in [scanner_results['connect'], scanner_results['version_avg'], shell_avg]):
        print("  ✓ All operations are performing well!")
    print()

if __name__ == "__main__":
    try:
        scanner_results = benchmark_scanner_class()
        cli_results = benchmark_cli_tool()
        print_summary(scanner_results, cli_results)

    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
