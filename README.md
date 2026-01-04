# Hackmud Linux Tools

Tools for communicating with the hackmud game process on Linux - reading game output from memory and sending keyboard input.

## Prerequisites

```bash
sudo pacman -S xdotool python
```

## Components

### 1. Terminal Reader (`read_vtable.py`) - Primary Scanner

Reads hackmud terminal output directly from memory using Mono runtime vtable structures. This is the most reliable scanner that works across game restarts and updates.

**Basic usage:**
```bash
# Read last 30 lines from shell terminal
python3 read_vtable.py 30

# Read chat instead of shell
python3 read_vtable.py 30 --chat

# Keep Unity color tags
python3 read_vtable.py 30 --colors

# Debug output showing vtable and instance addresses
python3 read_vtable.py 30 --debug
```

**How it works:**
- Scans heap for TextMeshProUGUI vtable via MonoClass structures
- Finds all TMP instances by scanning for vtable pointers
- Identifies shell/chat by Window.name field or content patterns
- Reads m_text field (MonoString) to get terminal text
- Loads offsets from `mono_offsets.json` for game update compatibility

**Configuration (`mono_offsets.json`):**
```json
{
  "version": "v2.016",
  "window_offsets": {
    "name": "0x90",
    "gui_text": "0x58"
  },
  "tmp_offsets": {
    "m_text": "0xc8"
  }
}
```

When hackmud updates, run `update_offsets.py` to recalculate field offsets from the decompiled Core.dll.

### 2. JSON Memory Scanner (`mem_scanner.py`)

Reads JSON responses directly from hackmud's memory. This captures all server responses including script outputs, errors, chat messages, etc.

**One-time scan:**
```bash
python3 mem_scanner.py
```

**Watch mode (continuous):**
```bash
python3 mem_scanner.py -w
```

Responses are logged to `responses.log` with timestamps and memory addresses.

**How it works:**
- Finds the hackmud process by name
- Scans readable memory regions for JSON patterns
- Extracts and validates JSON objects
- Deduplicates using MD5 hashes
- Writes new responses to the log file

### 3. Send Command (`send_command.py`)

Sends text input to the hackmud window using xdotool.

```bash
python3 send_command.py "scripts.fullsec"
python3 send_command.py "accts.balance"
python3 send_command.py "user.loc{target:\"some_npc\"}"
```

**How it works:**
- Finds the hackmud window via xdotool
- Types the command character by character
- Sends Enter key to execute

### 4. Get Responses (`get_responses.py`)

Retrieves recent responses from the log file.

```bash
# Get last 10 responses (formatted)
python3 get_responses.py

# Get last 20 responses
python3 get_responses.py -n 20

# Raw JSON output
python3 get_responses.py --raw

# Filter by script name
python3 get_responses.py --script weyland.public
```

### 5. Hardline Script (`hardline.sh`)

Automates the kernel.hardline process (typing characters as they appear).

```bash
bash hardline.sh
```

**How it works:**
- Sends `kernel.hardline` command
- Waits for the challenge prompt
- Reads the required characters from memory
- Types them with appropriate timing
- Confirms completion

### 6. Start Scanner (`start_scanner.sh`)

Convenience script to start the memory scanner in the background.

```bash
bash start_scanner.sh
```

PID is saved to `scanner.pid` for later management.

## Typical Workflow

1. Start hackmud and log in
2. Start the memory scanner:
   ```bash
   python3 mem_scanner.py -w &
   ```
3. Send commands:
   ```bash
   python3 send_command.py "accts.balance"
   ```
4. Read responses:
   ```bash
   python3 get_responses.py -n 1
   ```

## Files

| File | Purpose |
|------|---------|
| `read_vtable.py` | **Primary** - Reads terminal via Mono vtables |
| `mono_offsets.json` | Field offsets for game version compatibility |
| `update_offsets.py` | Recalculates offsets after game updates |
| `mem_scanner.py` | Reads JSON responses from process memory |
| `send_command.py` | Sends keyboard input to game window |
| `get_responses.py` | Retrieves responses from log |
| `hardline.sh` | Automates hardline connection |
| `start_scanner.sh` | Starts scanner in background |
| `responses.log` | Log of all captured responses |
| `scanner_backup/` | Legacy scanners (read_live.py, mono_reader.py) |

## Troubleshooting

**"Hackmud process not found"**
- Make sure hackmud is running
- The scanner looks for a process named "hackmud"

**"Could not find hackmud window"**
- Make sure the hackmud window is open (not minimized to tray)
- Window title must contain "hackmud"

**Commands not being sent**
- Focus may be getting stolen - ensure no popups
- Try running with hackmud window visible

**Missing responses**
- Scanner might not be running: `pgrep -f mem_scanner`
- Check if log is being written: `tail -f responses.log`
