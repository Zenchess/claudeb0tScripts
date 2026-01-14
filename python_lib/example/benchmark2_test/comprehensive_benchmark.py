#!/usr/bin/env python3
"""
Comprehensive Scanner API Benchmark - Tests ALL scenarios

Tests:
1. Normal Operations (all methods)
2. Error Conditions (game not found, invalid window, etc.)
3. Game Update Detection (checksum mismatch)
4. Cache Behavior (invalidation, persistence)
5. All Windows (shell, chat, badge, breach, scratch, binlog, binmat)
6. Context Manager vs Manual
7. Debug Mode
8. Multiple Scanner Instances
"""

import sys
import json
import time
from pathlib import Path
from typing import Callable, Any, Tuple

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hackmud.memory import Scanner
from hackmud.memory.exceptions import (
    GameNotFoundError,
    ConfigError,
    MemoryReadError,
    WindowNotFoundError
)

# Color codes
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
GRAY = '\033[90m'
RESET = '\033[0m'

def format_time(ms: float) -> str:
    """Format milliseconds with color"""
    if ms < 1:
        return f'{GREEN}{ms:8.2f}ms{RESET}'
    elif ms < 20:
        return f'{YELLOW}{ms:8.2f}ms{RESET}'
    else:
        return f'{RED}{ms:8.2f}ms{RESET}'

def benchmark_method(
    name: str,
    func: Callable,
    *args,
    **kwargs
) -> Tuple[float, bool, Any]:
    """Benchmark a single method call

    Returns:
        (elapsed_ms, success, result)
    """
    try:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        return elapsed, True, result
    except Exception as e:
        elapsed = 0
        return elapsed, False, str(e)

def test_normal_operations():
    """Test all normal API operations"""
    print("\n" + "="*80)
    print("TEST 1: NORMAL OPERATIONS")
    print("="*80)

    results = {}

    # Connection
    scanner = Scanner()
    elapsed, success, _ = benchmark_method("connect", scanner.connect)
    print(f"\n[1.1] Connection:")
    print(f"  connect()                     {format_time(elapsed)}  {'✓' if success else '✗'}")
    results['connect'] = (elapsed, success)

    if not success:
        print(f"{RED}  ERROR: Cannot connect to game - remaining tests skipped{RESET}")
        return results

    print(f"    PID: {scanner.pid}")

    # Version detection
    print(f"\n[1.2] Version Detection:")
    for i in range(3):
        elapsed, success, version = benchmark_method("get_version", scanner.get_version)
        print(f"  get_version() - run {i+1}       {format_time(elapsed)}  {'✓' if success else '✗'} {version if success else ''}")
        results[f'version_{i+1}'] = (elapsed, success)

    # Window reading - all windows
    print(f"\n[1.3] Window Reading (all windows):")
    windows = ['shell', 'chat', 'badge', 'breach', 'scratch', 'binlog', 'binmat']
    for window in windows:
        elapsed, success, lines = benchmark_method("read_window", scanner.read_window, window, lines=10)
        line_count = len(lines) if success else 0
        print(f"  read_window('{window:8s}', 10)  {format_time(elapsed)}  {'✓' if success else '✗'} [{line_count} lines]")
        results[f'read_{window}'] = (elapsed, success)

    # Rapid sequential reads
    print(f"\n[1.4] Rapid Sequential Reads (10x shell):")
    total_time = 0
    success_count = 0
    for i in range(10):
        elapsed, success, _ = benchmark_method("rapid_read", scanner.read_window, 'shell', lines=5)
        total_time += elapsed
        if success:
            success_count += 1

    avg_time = total_time / 10
    print(f"  Total time:   {format_time(total_time)}")
    print(f"  Average:      {format_time(avg_time)}")
    print(f"  Success rate: {success_count}/10 ({success_count*10}%)")
    results['rapid_reads'] = (avg_time, success_count == 10)

    # Context manager test
    print(f"\n[1.5] Context Manager:")
    elapsed, success, _ = benchmark_method(
        "context_manager",
        lambda: list(__context_manager_test())
    )
    print(f"  with Scanner() as s:          {format_time(elapsed)}  {'✓' if success else '✗'}")
    results['context_manager'] = (elapsed, success)

    # Debug mode
    print(f"\n[1.6] Debug Mode:")
    scanner.set_debug(True)
    elapsed, success, _ = benchmark_method("debug_read", scanner.read_window, 'shell', lines=5)
    print(f"  read_window() with debug      {format_time(elapsed)}  {'✓' if success else '✗'}")
    scanner.set_debug(False)
    results['debug_mode'] = (elapsed, success)

    # Cleanup
    scanner.close()

    return results

def __context_manager_test():
    """Helper for context manager test"""
    with Scanner() as s:
        yield s.read_window('shell', lines=5)

def test_error_conditions():
    """Test error handling"""
    print("\n" + "="*80)
    print("TEST 2: ERROR CONDITIONS")
    print("="*80)

    results = {}

    # Invalid window name
    print(f"\n[2.1] Invalid Window Name:")
    scanner = Scanner()
    scanner.connect()
    elapsed, success, error = benchmark_method(
        "invalid_window",
        scanner.read_window,
        'invalid_window'
    )
    expected_error = isinstance(error, str) and 'Invalid window name' in error
    print(f"  read_window('invalid')        {format_time(elapsed)}  {'✓ (error caught)' if not success and expected_error else '✗'}")
    print(f"    Error: {error[:60]}..." if not success else "")
    results['invalid_window'] = (elapsed, not success and expected_error)

    # Operation without connect
    print(f"\n[2.2] Operation Without Connect:")
    scanner2 = Scanner()
    elapsed, success, error = benchmark_method(
        "no_connect",
        scanner2.read_window,
        'shell'
    )
    expected_error = isinstance(error, str) and 'Not connected' in error
    print(f"  read_window() no connect      {format_time(elapsed)}  {'✓ (error caught)' if not success and expected_error else '✗'}")
    print(f"    Error: {error[:60]}..." if not success else "")
    results['no_connect'] = (elapsed, not success and expected_error)

    # Cleanup
    scanner.close()

    return results

def test_game_update_detection():
    """Test game update detection via checksum"""
    print("\n" + "="*80)
    print("TEST 3: GAME UPDATE DETECTION")
    print("="*80)

    results = {}

    print(f"\n[3.1] Current Checksum:")
    config_file = Path(__file__).parent / 'data' / 'scanner_config.json'
    with open(config_file) as f:
        config = json.load(f)

    original_checksum = config['checksum']
    print(f"  Original: {original_checksum[:32]}...")

    # Backup original
    config_backup = config.copy()

    # Simulate game update by changing checksum
    print(f"\n[3.2] Simulating Game Update (checksum change):")
    config['checksum'] = 'fake_checksum_for_testing_game_update_12345678901234567890'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"  Modified: {config['checksum'][:32]}...")

    # Try to connect with mismatched checksum
    print(f"\n[3.3] Connection with Checksum Mismatch:")
    scanner = Scanner()
    elapsed, success, error = benchmark_method("connect_mismatch", scanner.connect)

    # Note: Scanner doesn't validate checksum on connect, it's checked by config module
    print(f"  connect() with bad checksum   {format_time(elapsed)}  {'✓' if success else '✗ (expected)'}")
    if not success:
        print(f"    Error: {str(error)[:60]}...")

    results['checksum_mismatch'] = (elapsed, not success)

    # Restore original config
    print(f"\n[3.4] Restoring Original Config:")
    with open(config_file, 'w') as f:
        json.dump(config_backup, f, indent=2)
    print(f"  Restored: {config_backup['checksum'][:32]}...")

    # Verify connection works again
    scanner2 = Scanner()
    elapsed, success, _ = benchmark_method("connect_restored", scanner2.connect)
    print(f"  connect() after restore       {format_time(elapsed)}  {'✓' if success else '✗'}")
    results['connect_restored'] = (elapsed, success)

    if success:
        scanner2.close()

    return results

def test_cache_behavior():
    """Test address caching and invalidation"""
    print("\n" + "="*80)
    print("TEST 4: CACHE BEHAVIOR")
    print("="*80)

    results = {}

    # First connection (may use cache)
    print(f"\n[4.1] First Connection (cache may exist):")
    scanner1 = Scanner()
    elapsed1, success1, _ = benchmark_method("connect_1", scanner1.connect)
    print(f"  connect() #1                  {format_time(elapsed1)}  {'✓' if success1 else '✗'}")
    results['connect_1'] = (elapsed1, success1)

    if not success1:
        return results

    # Read to ensure cache is populated
    scanner1.read_window('shell', lines=5)
    scanner1.close()

    # Second connection (should use cache)
    print(f"\n[4.2] Second Connection (should use cache):")
    scanner2 = Scanner()
    elapsed2, success2, _ = benchmark_method("connect_2", scanner2.connect)
    print(f"  connect() #2                  {format_time(elapsed2)}  {'✓' if success2 else '✗'}")
    results['connect_2'] = (elapsed2, success2)

    speedup = elapsed1 / elapsed2 if elapsed2 > 0 else 0
    print(f"  Speedup: {speedup:.1f}x {'(cache hit)' if speedup > 2 else '(no cache)'}")

    scanner2.close()

    # Delete cache and reconnect
    print(f"\n[4.3] Connection After Cache Deletion:")
    cache_file = Path(__file__).parent / 'data' / 'mono_addresses.json'
    cache_backup = None
    if cache_file.exists():
        with open(cache_file) as f:
            cache_backup = f.read()
        cache_file.unlink()
        print(f"  Deleted cache file")

    scanner3 = Scanner()
    elapsed3, success3, _ = benchmark_method("connect_3", scanner3.connect)
    print(f"  connect() #3 (no cache)       {format_time(elapsed3)}  {'✓' if success3 else '✗'}")
    results['connect_no_cache'] = (elapsed3, success3)

    # Restore cache
    if cache_backup:
        with open(cache_file, 'w') as f:
            f.write(cache_backup)
        print(f"  Restored cache file")

    scanner3.close()

    return results

def test_multiple_instances():
    """Test multiple concurrent scanner instances"""
    print("\n" + "="*80)
    print("TEST 5: MULTIPLE SCANNER INSTANCES")
    print("="*80)

    results = {}

    print(f"\n[5.1] Creating 3 Scanner Instances:")

    scanners = []
    for i in range(3):
        scanner = Scanner()
        elapsed, success, _ = benchmark_method(f"scanner_{i+1}_connect", scanner.connect)
        print(f"  Scanner #{i+1} connect()         {format_time(elapsed)}  {'✓' if success else '✗'}")
        results[f'scanner_{i+1}_connect'] = (elapsed, success)

        if success:
            scanners.append(scanner)

    print(f"\n[5.2] Reading from All Instances:")
    for i, scanner in enumerate(scanners):
        elapsed, success, lines = benchmark_method(
            f"scanner_{i+1}_read",
            scanner.read_window,
            'shell',
            lines=10
        )
        line_count = len(lines) if success else 0
        print(f"  Scanner #{i+1} read()            {format_time(elapsed)}  {'✓' if success else '✗'} [{line_count} lines]")
        results[f'scanner_{i+1}_read'] = (elapsed, success)

    # Cleanup
    for scanner in scanners:
        scanner.close()

    return results

def main():
    """Run all benchmarks"""
    print("="*80)
    print("COMPREHENSIVE SCANNER API BENCHMARK")
    print("="*80)
    print("\nTesting all scenarios including game updates, errors, and edge cases")

    all_results = {}

    # Run all tests
    try:
        all_results['normal'] = test_normal_operations()
    except Exception as e:
        print(f"\n{RED}ERROR in normal operations: {e}{RESET}")
        all_results['normal'] = {}

    try:
        all_results['errors'] = test_error_conditions()
    except Exception as e:
        print(f"\n{RED}ERROR in error conditions: {e}{RESET}")
        all_results['errors'] = {}

    try:
        all_results['game_update'] = test_game_update_detection()
    except Exception as e:
        print(f"\n{RED}ERROR in game update detection: {e}{RESET}")
        all_results['game_update'] = {}

    try:
        all_results['cache'] = test_cache_behavior()
    except Exception as e:
        print(f"\n{RED}ERROR in cache behavior: {e}{RESET}")
        all_results['cache'] = {}

    try:
        all_results['multiple'] = test_multiple_instances()
    except Exception as e:
        print(f"\n{RED}ERROR in multiple instances: {e}{RESET}")
        all_results['multiple'] = {}

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    total_tests = 0
    passed_tests = 0
    total_time = 0

    for category, results in all_results.items():
        for test_name, (elapsed, success) in results.items():
            total_tests += 1
            if success:
                passed_tests += 1
            total_time += elapsed

    print(f"\nTotal Tests:   {total_tests}")
    print(f"Passed:        {GREEN}{passed_tests}{RESET}")
    print(f"Failed:        {RED}{total_tests - passed_tests}{RESET}")
    print(f"Success Rate:  {passed_tests}/{total_tests} ({(passed_tests/total_tests*100):.1f}%)")
    print(f"Total Time:    {format_time(total_time)}")

    if passed_tests == total_tests:
        print(f"\n{GREEN}Overall: ALL TESTS PASSED ✓{RESET}")
    elif passed_tests > total_tests * 0.8:
        print(f"\n{YELLOW}Overall: GOOD (some tests failed){RESET}")
    else:
        print(f"\n{RED}Overall: ISSUES DETECTED{RESET}")

if __name__ == '__main__':
    main()
