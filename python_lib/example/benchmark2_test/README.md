# Comprehensive Scanner API Benchmark

Complete test suite for the hackmud memory scanner that tests **all possible scenarios** including normal operations, error conditions, game updates, cache behavior, and edge cases.

## Test Categories

### 1. Normal Operations
Tests all API methods under normal conditions:
- **Connection**: `connect()` with timing
- **Version Detection**: Multiple calls to verify caching (3 runs)
- **Window Reading**: All 7 windows (shell, chat, badge, breach, scratch, binlog, binmat)
- **Rapid Sequential**: 10 consecutive reads to test performance stability
- **Context Manager**: `with Scanner() as s:` pattern
- **Debug Mode**: Operations with `set_debug(True)`

### 2. Error Conditions
Tests error handling and exceptions:
- **Invalid Window**: Attempts to read non-existent window
- **No Connection**: Attempts operations without calling `connect()`
- Expected behavior: Proper exceptions raised with descriptive messages

### 3. Game Update Detection
Tests checksum-based update detection:
- **Original Checksum**: Read current config checksum
- **Simulate Update**: Modify checksum to simulate game update
- **Connection Attempt**: Try to connect with mismatched checksum
- **Restoration**: Restore original config and verify recovery

This tests the critical path for detecting when hackmud has been updated and offsets may need regeneration.

### 4. Cache Behavior
Tests address caching and invalidation:
- **First Connection**: May use existing cache
- **Second Connection**: Should use cache (faster)
- **Speedup Calculation**: Measures cache effectiveness (2x+ speedup expected)
- **Cache Deletion**: Removes cache and tests full scan path
- **Cache Restoration**: Restores cache for subsequent tests

### 5. Multiple Scanner Instances
Tests concurrent scanner usage:
- **3 Parallel Instances**: Creates 3 separate Scanner objects
- **Concurrent Reads**: All instances read simultaneously
- **Resource Cleanup**: Verifies proper cleanup of all instances

## Usage

```bash
# Run from anywhere
python3 python_lib/example/benchmark2_test/comprehensive_benchmark.py

# Or from project root
cd /home/jacob/hackmud
python3 python_lib/example/benchmark2_test/comprehensive_benchmark.py
```

## Expected Results

### Success Criteria
- **Normal Operations**: 100% pass rate (20+ tests)
- **Error Conditions**: Proper exceptions caught (2 tests)
- **Game Update**: Checksum validation works (3 tests)
- **Cache Behavior**: 2x+ speedup on cached reads (3 tests)
- **Multiple Instances**: All instances work independently (6 tests)

### Performance Targets
- **Connection (cached)**: < 1ms
- **Connection (no cache)**: < 50ms
- **Version detection (cached)**: < 0.1ms
- **Window reads**: < 5ms average
- **Rapid reads**: < 1ms per read

## Output Format

```
================================================================================
TEST 1: NORMAL OPERATIONS
================================================================================

[1.1] Connection:
  connect()                        20.45ms  ✓
    PID: 1234567

[1.2] Version Detection:
  get_version() - run 1             0.00ms  ✓ v2.016
  get_version() - run 2             0.00ms  ✓ v2.016
  get_version() - run 3             0.00ms  ✓ v2.016

[1.3] Window Reading (all windows):
  read_window('shell   ', 10)       0.15ms  ✓ [10 lines]
  read_window('chat    ', 10)       3.52ms  ✓ [10 lines]
  ...

================================================================================
SUMMARY
================================================================================

Total Tests:   45
Passed:        45
Failed:        0
Success Rate:  45/45 (100.0%)
Total Time:    125.34ms

Overall: ALL TESTS PASSED ✓
```

## Color Coding

- 🟢 **Green** (< 1ms): Excellent performance
- 🟡 **Yellow** (1-20ms): Good performance
- 🔴 **Red** (> 20ms): Slow (expected for initial scan)
- ✓ Success
- ✗ Failure

## Test Coverage

This benchmark tests:
- ✅ All 7 public API methods
- ✅ All 7 window types
- ✅ Context manager pattern
- ✅ Manual connect/close pattern
- ✅ Debug mode
- ✅ Error handling (2 error types)
- ✅ Game update detection
- ✅ Cache effectiveness
- ✅ Cache invalidation
- ✅ Multiple concurrent instances
- ✅ Rapid sequential operations
- ✅ Performance consistency

## Configuration Files

The `data/` directory contains copies of the main configuration:
- `constants.json`: Game version and window names
- `mono_names_fixed.json`: Non-obfuscated class names
- `mono_names.json`: Obfuscated class names
- `mono_offsets.json`: Memory structure offsets
- `scanner_config.json`: Platform-specific paths and checksum
- `mono_addresses.json`: Runtime address cache

These files are **copies** of the main config for isolated testing.

## Troubleshooting

### "Game not found" Error
Make sure hackmud is running before starting the benchmark.

### Slow Connection Times
First connection without cache takes ~20-50ms. Subsequent connections should be < 1ms.

### Failed Error Condition Tests
Error handling tests are **supposed to fail** - they verify proper exception handling. Check that the error messages are correct.

### Cache Not Working
If second connection isn't faster, check that:
1. `mono_addresses.json` exists in `data/`
2. PID matches current game instance
3. No permission issues on cache file

## Development

To add new tests:
1. Create a new `test_xyz()` function
2. Follow the pattern: print header, run benchmarks, return results dict
3. Add to `main()` with try/except wrapper
4. Update this README with new test description

## See Also

- `../benchmark_test/` - Original simplified benchmark
- `../scanner_test/` - Basic usage example
- `../../hackmud/memory/scanner.py` - Scanner implementation
