# Hackmud Scanner API - Test Examples

Simple examples demonstrating the hackmud memory scanner API with automatic config generation.

## Files

- **basic_example.py**: Basic usage of Scanner class (connect, version, read windows)

## Requirements

- Python 3.6+
- hackmud installed
- ilspycmd (.NET decompiler): `dotnet tool install -g ilspycmd`
- Scanner API (python_lib/hackmud/memory/)

## Auto-Configuration

**New in v1.2.1:** The Scanner automatically generates configuration files on first use!

When you first call `scanner.connect()`, the Scanner will:
1. Create a `data/` folder in your current working directory
2. Auto-detect your hackmud installation path
3. Decompile Core.dll to extract current offsets
4. Generate all required config files:
   - `mono_offsets.json` - Memory offsets and class names
   - `scanner_config.json` - Platform and paths
   - `mono_names_fixed.json` - Fixed class mappings
   - `constants.json` - Game version and window names

**First run takes ~5-10 seconds** (decompilation). Subsequent runs are instant.

## Usage

### Basic Example

```bash
# Run from this directory
python3 basic_example.py

# Or from project root
python3 python_lib/example/scanner_test/basic_example.py
```

## Scanner API Methods

### Connection
```python
from hackmud.memory import Scanner

scanner = Scanner()
scanner.connect()  # Auto-finds hackmud PID
print(f"Connected to PID: {scanner.pid}")
```

### Version Detection
```python
version = scanner.get_version()  # Returns: "v2.016"
```

### Window Reading
```python
# Read shell window
shell_lines = scanner.read_window('shell', lines=20)

# Read chat window
chat_lines = scanner.read_window('chat', lines=10)
```

### Cleanup
```python
scanner.close()  # Always close when done
```

## Performance Notes

- **connect()**: ~3-4 seconds (finds PID, scans memory)
- **get_version()**: ~0.5-1 second (searches for version string)
- **read_terminal()**: ~0.05-0.1 seconds (reads cached window)

For faster performance with multiple reads, keep the Scanner instance alive instead of creating new ones.

## Error Handling

```python
try:
    scanner = Scanner()
    scanner.connect()
    version = scanner.get_version()
except Exception as e:
    print(f"Error: {e}")
finally:
    scanner.close()
```
