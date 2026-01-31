#!/usr/bin/env python3
"""
Python memory reading benchmark - equivalent to Rust vtable_lookup
"""

import time
from pathlib import Path

def find_hackmud_pid():
    """Find hackmud PID from scanner.pid or pgrep"""
    pid_file = Path('/home/jacob/hackmud/scanner.pid')
    if pid_file.exists():
        pid = int(pid_file.read_text().strip())
        if Path(f'/proc/{pid}/mem').exists():
            return pid

    # Fallback to pgrep
    import subprocess
    try:
        result = subprocess.run(['pgrep', 'hackmud'], capture_output=True, text=True)
        if result.returncode == 0:
            return int(result.stdout.strip())
    except:
        pass

    return None

def get_heap_addresses(pid):
    """Get sample addresses from heap region"""
    maps_path = f'/proc/{pid}/maps'
    addresses = []

    with open(maps_path, 'r') as f:
        for line in f:
            if '[heap]' in line:
                addr_range = line.split()[0]
                start_str, end_str = addr_range.split('-')
                start = int(start_str, 16)
                end = int(end_str, 16)

                # Sample 100 addresses from heap region
                region_size = end - start
                if region_size > 0:
                    for i in range(100):
                        offset = (region_size // 100) * i
                        addresses.append((start + offset, 8))

                break  # Only use first heap region

    return addresses

def benchmark_memory_reads(pid, addresses):
    """Benchmark memory reading"""
    mem_path = f'/proc/{pid}/mem'

    try:
        mem_file = open(mem_path, 'rb', buffering=0)
    except Exception as e:
        print(f"Failed to open {mem_path}: {e}")
        return 0, 0

    start = time.perf_counter()
    successful_reads = 0

    for addr, size in addresses:
        try:
            mem_file.seek(addr)
            data = mem_file.read(size)
            if len(data) == size:
                successful_reads += 1
        except:
            pass

    elapsed_micros = (time.perf_counter() - start) * 1_000_000
    mem_file.close()

    return successful_reads, elapsed_micros

def main():
    print("=== Python Memory Reading Benchmark ===\n")

    # Find hackmud PID
    pid = find_hackmud_pid()
    if pid is None:
        print("Error: hackmud process not found")
        print("Make sure hackmud is running")
        return

    print(f"Found hackmud process: PID {pid}")

    # Get addresses from heap
    print("Finding heap addresses...")
    addresses = get_heap_addresses(pid)

    if not addresses:
        print("Error: No heap addresses found")
        return

    print(f"Found {len(addresses)} addresses to test\n")

    # Run benchmark
    print(f"Running benchmark (reading {len(addresses)} locations)...")
    successful, elapsed_micros = benchmark_memory_reads(pid, addresses)

    print("\nResults:")
    print(f"  Successful reads: {successful}/{len(addresses)}")
    print(f"  Total time:       {elapsed_micros/1000:.3f} ms")
    print(f"  Time per read:    {elapsed_micros/len(addresses):.3f} µs")

    # Run multiple iterations for average
    print("\n Running 10 iterations for average...")
    times = []

    for _ in range(10):
        _, elapsed = benchmark_memory_reads(pid, addresses)
        times.append(elapsed)

    avg = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"  Average: {avg/1000:.3f} ms")
    print(f"  Min:     {min_time/1000:.3f} ms")
    print(f"  Max:     {max_time/1000:.3f} ms")
    print(f"  Per read: {avg/len(addresses):.3f} µs")

if __name__ == '__main__':
    main()
