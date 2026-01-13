#!/usr/bin/env python3
"""Check memory regions to understand scanning scope"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'python_lib'))

from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()

regions = scanner._get_memory_regions()
heap = scanner._get_heap_region()

print(f"Total rw- regions: {len(regions)}")
print(f"Heap region: 0x{heap[0]:x}-0x{heap[1]:x} ({(heap[1]-heap[0])//1024//1024}MB)")
print()

print("Largest regions:")
for start, end in sorted(regions, key=lambda x: x[1]-x[0], reverse=True)[:10]:
    size_mb = (end - start) // 1024 // 1024
    print(f"  0x{start:x}-0x{end:x}  {size_mb:>4}MB")

scanner.close()
