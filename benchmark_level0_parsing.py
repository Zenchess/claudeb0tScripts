#!/usr/bin/env python3
"""Benchmark window name extraction from level0"""

import sys
import time
sys.path.insert(0, '/tmp/unitypy_venv/lib/python3.13/site-packages')

import UnityPy

# Number of iterations
ITERATIONS = 10

# Load the level0 file
level0_path = "/home/jacob/.local/share/Steam/steamapps/common/hackmud/hackmud_lin_Data/level0"

print(f"Benchmarking window name extraction from level0")
print(f"Iterations: {ITERATIONS}")
print()

times = []

for i in range(ITERATIONS):
    start = time.perf_counter()

    # Load and parse
    env = UnityPy.load(level0_path)

    # Extract window names
    window_names = set()
    for obj in env.objects:
        if obj.type.name == "GameObject":
            data = obj.read()
            name = data.m_Name
            if any(w in name.lower() for w in ['shell', 'chat', 'badge', 'breach', 'scratch', 'binlog', 'binmat', 'version']):
                window_names.add(name)

    elapsed = time.perf_counter() - start
    times.append(elapsed * 1000)  # Convert to ms

    print(f"Run {i+1}: {elapsed*1000:.2f}ms - Found {len(window_names)} windows")

print()
print(f"Average: {sum(times)/len(times):.2f}ms")
print(f"Min: {min(times):.2f}ms")
print(f"Max: {max(times):.2f}ms")
print()
print(f"Windows found: {sorted(window_names)}")
