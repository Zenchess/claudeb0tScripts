# Hackmud Memory Structure Documentation

This document explains how to read hackmud's game state from memory using external tools. This is purely read-only inspection - no game modification.

## Overview

Hackmud is built on Unity with Mono runtime. Key structures:
- **Mono Runtime** - Manages .NET/C# objects
- **Unity Engine** - Handles rendering, GameObjects, Components
- **TextMeshPro** - Rich text rendering for terminal output

## Finding the Game Process

```python
import subprocess

def find_hackmud_pid():
    """Find hackmud process ID"""
    result = subprocess.run(['pgrep', '-f', 'hackmud'], capture_output=True, text=True)
    return int(result.stdout.strip().split()[0])
```

## Reading Process Memory (Linux)

```python
def read_memory(pid, address, size):
    """Read bytes from process memory"""
    with open(f'/proc/{pid}/mem', 'rb') as f:
        f.seek(address)
        return f.read(size)

def read_ptr(pid, address):
    """Read 64-bit pointer"""
    data = read_memory(pid, address, 8)
    return int.from_bytes(data, 'little')

def read_string(pid, address, encoding='utf-16-le'):
    """Read MonoString - length at +0x10, chars at +0x14"""
    length = int.from_bytes(read_memory(pid, address + 0x10, 4), 'little')
    if length > 10000:  # Sanity check
        return None
    data = read_memory(pid, address + 0x14, length * 2)
    return data.decode(encoding, errors='replace')
```

## Mono Runtime Navigation

### Finding mono_root_domain

The mono runtime root is exported in libmono. Find it via:
1. Parse `/proc/[pid]/maps` for libmono.so
2. Use symbol lookup or scan for known pattern

```python
def find_mono_domain(pid):
    """Find mono_root_domain from libmono"""
    # Read /proc/[pid]/maps to find libmono.so
    with open(f'/proc/{pid}/maps') as f:
        for line in f:
            if 'libmono' in line and 'r-x' in line:
                base = int(line.split('-')[0], 16)
                # mono_root_domain is typically at known offset
                # (varies by mono version)
                return base
    return None
```

### Mono Class Structures

```
MonoDomain
├── domain_assemblies (linked list of MonoAssembly)
    └── MonoAssembly
        └── image (MonoImage)
            └── class_cache (hash table of MonoClass)
                └── MonoClass
                    ├── name (+0x40) - class name string
                    ├── namespace (+0x48) - namespace string
                    ├── runtime_info (+0xC8) - MonoClassRuntimeInfo
                    │   └── vtable (+0x8) - MonoVTable*
                    └── fields - MonoClassField[]
```

### Key Offsets

```json
{
  "mono_class_name": "0x40",
  "mono_class_namespace": "0x48",
  "mono_class_runtime_info": "0xC8",
  "mono_runtime_info_vtable": "0x8",
  "mono_string_length": "0x10",
  "mono_string_data": "0x14"
}
```

## Hackmud-Specific Classes

### Window Class (hackmud.Window)

The Window class manages game UI panels (shell, chat, etc.)

```
Window
├── name (+0x90) - MonoString* ("shell", "chat", etc.)
├── gui_text (+0x58) - TextMeshProUGUI* component
└── ... other fields
```

### TextMeshProUGUI (TMPro.TextMeshProUGUI)

Rich text component containing terminal output:

```
TextMeshProUGUI
└── m_text (+0xC8) - MonoString* with current text content
```

### Kernel Class (hackmud.Kernel)

Main game controller. Contains static references to game state.

## Finding Object Instances

### Method 1: Vtable Scanning

1. Find MonoClass for target type
2. Get vtable address from runtime_info
3. Scan heap for pointers to vtable
4. Each match is an object instance

```python
def find_instances(pid, vtable_addr, region_start, region_end):
    """Scan memory region for objects with given vtable"""
    instances = []
    data = read_memory(pid, region_start, region_end - region_start)

    for offset in range(0, len(data) - 8, 8):
        ptr = int.from_bytes(data[offset:offset+8], 'little')
        if ptr == vtable_addr:
            instances.append(region_start + offset)

    return instances
```

### Method 2: Static Fields (Preferred)

If a class has static singleton fields, access directly:

1. Find MonoClass for type
2. Read runtime_info.vtable
3. Static field data follows vtable structure
4. Read pointer at known offset

## ASLR Handling

Addresses change on restart due to ASLR. Strategy:

1. **Runtime Discovery** - Find mono_root_domain each session
2. **Relative Offsets** - Store field offsets (stable across restarts)
3. **Class Name Lookup** - Find classes by name, not address
4. **Cache Results** - Instance addresses stable within a session

## Obfuscated Class Names

Hackmud obfuscates some class names. Map them on game update:

```python
def update_offsets():
    """Re-map obfuscated names after game update"""
    # Decompile Core.dll with ilspy/dnSpy
    # Search for known patterns (field types, method signatures)
    # Update mono_offsets.json with new names
```

Known mappings (may change):
- `NMOPNOICKDJ` - Output queue class
- `FFAKOMDAHHC` - Queue field name

Non-obfuscated (stable):
- `hackmud.Window`
- `hackmud.Kernel`
- `TMPro.TextMeshProUGUI`

## Example: Reading Shell Output

```python
def read_shell_output(pid):
    # 1. Find Window class
    window_class = find_class(pid, "hackmud", "Window")

    # 2. Get vtable
    runtime_info = read_ptr(pid, window_class + 0xC8)
    vtable = read_ptr(pid, runtime_info + 0x8)

    # 3. Find Window instances
    instances = find_instances(pid, vtable, heap_start, heap_end)

    # 4. Find shell window
    for inst in instances:
        name_ptr = read_ptr(pid, inst + 0x90)
        name = read_string(pid, name_ptr)
        if name == "shell":
            # 5. Get TextMeshPro component
            tmp_ptr = read_ptr(pid, inst + 0x58)

            # 6. Read text content
            text_ptr = read_ptr(pid, tmp_ptr + 0xC8)
            return read_string(pid, text_ptr)

    return None
```

## Tools Included

- `read_vtable.py` - Read terminal output using vtable method
- `update_offsets.py` - Re-extract offsets after game update
- `mono_offsets.json` - Stored offset mappings

## References

- [Mono Runtime Internals](https://www.mono-project.com/docs/advanced/embedding/)
- [Unity Mono](https://docs.unity3d.com/Manual/overview-of-dot-net-in-unity.html)
- [TextMeshPro](https://docs.unity3d.com/Packages/com.unity.textmeshpro@3.0/manual/index.html)

## Disclaimer

This documentation is for educational purposes - understanding how Unity/Mono games work internally. No game modification or cheating is involved. Reading memory is passive observation only.
