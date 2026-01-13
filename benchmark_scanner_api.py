#!/usr/bin/env python3
"""
Comprehensive benchmark of the hackmud memory scanner API.

Measures performance of all Scanner methods:
- connect()
- get_version()
- read_terminal() - shell
- read_terminal() - chat
- close()
"""

import sys
import time
import traceback
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

def benchmark_method(name, method, *args, **kwargs):
    """Benchmark a single method call"""
    print(f"  {name:<30} ", end='', flush=True)

    try:
        start = time.time()
        result = method(*args, **kwargs)
        elapsed = time.time() - start

        # Format result for display
        if isinstance(result, str):
            result_str = result[:50] + '...' if len(result) > 50 else result
        elif isinstance(result, list):
            result_str = f"[{len(result)} items]"
        else:
            result_str = str(result)[:50]

        print(f"{format_time(elapsed)}  ✓ {result_str}")
        return elapsed, True

    except Exception as e:
        elapsed = time.time() - start
        print(f"{format_time(elapsed)}  ✗ {str(e)[:50]}")
        return elapsed, False

def run_benchmark():
    """Run full API benchmark"""
    print("=" * 80)
    print("HACKMUD MEMORY SCANNER API BENCHMARK")
    print("=" * 80)
    print()

    results = {}
    scanner = Scanner()

    # Benchmark 1: Connection
    print("[1] Connection:")
    elapsed, success = benchmark_method("connect()", scanner.connect)
    results['connect'] = (elapsed, success)

    if not success:
        print("\n✗ Connection failed. Cannot continue benchmark.")
        return results

    print(f"    PID: {scanner.pid}")
    print()

    # Benchmark 2: Version Detection
    print("[2] Version Detection:")
    for i in range(3):
        elapsed, success = benchmark_method(f"get_version() - run {i+1}", scanner.get_version)
        results[f'get_version_{i+1}'] = (elapsed, success)
    print()

    # Benchmark 3: Terminal Reading (Shell)
    print("[3] Terminal Reading (Shell):")
    for lines in [10, 20, 40]:
        elapsed, success = benchmark_method(
            f"read_terminal(lines={lines})",
            scanner.read_terminal,
            lines=lines
        )
        results[f'read_terminal_shell_{lines}'] = (elapsed, success)
    print()

    # Benchmark 4: Terminal Reading (Chat)
    print("[4] Terminal Reading (Chat):")
    for lines in [10, 20, 40]:
        elapsed, success = benchmark_method(
            f"read_terminal(lines={lines}, chat)",
            scanner.read_terminal,
            lines=lines,
            window_name='chat'
        )
        results[f'read_terminal_chat_{lines}'] = (elapsed, success)
    print()

    # Benchmark 5: Multiple Rapid Reads
    print("[5] Rapid Sequential Reads (10x):")
    start = time.time()
    success_count = 0
    for i in range(10):
        try:
            scanner.read_terminal(lines=20)
            success_count += 1
        except:
            pass
    elapsed = time.time() - start
    avg_time = elapsed / 10
    print(f"  Total time:   {format_time(elapsed)}")
    print(f"  Average:      {format_time(avg_time)}")
    print(f"  Success rate: {success_count}/10 ({success_count*10}%)")
    results['rapid_reads'] = (avg_time, success_count == 10)
    print()

    # Benchmark 6: Disconnect
    print("[6] Disconnection:")
    elapsed, success = benchmark_method("close()", scanner.close)
    results['close'] = (elapsed, success)
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    # Calculate statistics
    successful = sum(1 for _, success in results.values() if success)
    total = len(results)

    # Find fastest/slowest
    sorted_results = sorted(results.items(), key=lambda x: x[1][0])
    fastest_name, (fastest_time, _) = sorted_results[0]
    slowest_name, (slowest_time, _) = sorted_results[-1]

    # Average times
    connect_time = results['connect'][0]
    version_times = [results[f'get_version_{i}'][0] for i in range(1, 4)]
    avg_version_time = sum(version_times) / len(version_times)
    shell_times = [results[f'read_terminal_shell_{lines}'][0] for lines in [10, 20, 40]]
    avg_shell_time = sum(shell_times) / len(shell_times)
    chat_times = [results[f'read_terminal_chat_{lines}'][0] for lines in [10, 20, 40]]
    avg_chat_time = sum(chat_times) / len(chat_times)

    print(f"Success Rate:  {successful}/{total} ({successful*100//total}%)")
    print()
    print(f"Connection:    {format_time(connect_time)}")
    print(f"Version Avg:   {format_time(avg_version_time)}")
    print(f"Shell Avg:     {format_time(avg_shell_time)}")
    print(f"Chat Avg:      {format_time(avg_chat_time)}")
    print()
    print(f"Fastest:       {fastest_name:<30} {format_time(fastest_time)}")
    print(f"Slowest:       {slowest_name:<30} {format_time(slowest_time)}")
    print()

    # Performance assessment
    if avg_shell_time < 0.05:  # < 50ms
        assessment = "EXCELLENT"
        color = '\033[32m'
    elif avg_shell_time < 0.1:  # < 100ms
        assessment = "GOOD"
        color = '\033[33m'
    else:
        assessment = "NEEDS OPTIMIZATION"
        color = '\033[31m'

    print(f"Overall Performance: {color}{assessment}\033[0m")
    print()

    return results

if __name__ == "__main__":
    try:
        results = run_benchmark()
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Benchmark failed: {e}")
        traceback.print_exc()
        sys.exit(1)
