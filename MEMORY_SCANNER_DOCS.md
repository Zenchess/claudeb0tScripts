# Hackmud Memory Scanner Documentation

Scripts for reading hackmud terminal/shell output directly from process memory.

## Scripts

### read_live.py
**DYNAMIC** memory scanner that automatically finds the live buffer region containing recent shell output.

**Usage:**
```bash
python3 read_live.py [lines] [--colors] [--debug]
```

**Options:**
- `lines` - Number of lines to show (default: 20)
- `--colors` - Preserve Unity color tags in output
- `--debug` - Show region detection details and scoring

**Example:**
```bash
python3 read_live.py 30 --colors
python3 read_live.py 20 --debug
```

**Features:**
- Automatically scans ~80+ memory regions to find the live buffer
- Scores regions by: shell prompts (>>>), Unity color tags, chat entries, timestamp recency
- Raises RuntimeError if multiple regions have ambiguous/similar scores
- Filters garbage unicode characters from output
- Deduplicates chat entries
- No hardcoded addresses - works across hackmud restarts

### read_terminal.py
Basic terminal reader that searches for `>>>` prompts across memory regions.

**Usage:**
```bash
python3 read_terminal.py [lines]
```

### read_shell.py
Pattern-based reader that looks for JSON script results and chat entries.

**Usage:**
```bash
python3 read_shell.py [lines]
```

### discord_send_direct.py
Reliable one-shot Discord message sender.

**Usage:**
```bash
./discord_venv/bin/python discord_send_direct.py CHANNEL_ID "message"
```

**Example:**
```bash
./discord_venv/bin/python discord_send_direct.py 1456288519403208800 "Hello from claudeb0t"
```

## How It Works

### Memory Layout
- Hackmud stores terminal output as UTF-16 encoded strings
- Shell commands appear with `>>>` prompts
- Text uses Unity color tags: `<color=#RRGGBBAA>text</color>`
- Chat uses format: `timestamp channel username :::message:::`

### Color Codes
| Color | Hex | Usage |
|-------|-----|-------|
| Orange | #FF8000FF | Script names |
| Green | #1EFF00FF | Method names |
| Cyan | #00FFFFFF | Parameter names |
| Gray | #9B9B9BFF | Secondary text |
| Yellow/Gold | #FFF404FF | claudeb0t username in chat |
| Dark Gray | #3F3F3FFF | ::: chat separators |
| White | #FFFFFFFF | Default/prompt |

### Finding the Live Buffer
The "live" buffer region can be identified dynamically:

1. Send a unique command (e.g., `MARKER_timestamp`)
2. Wait a few seconds
3. Send another unique command
4. Scan all rw-p regions for both markers
5. The region with ONLY the newer marker is the live buffer

The live buffer is typically ~836KB and located after System.Runtime.Serialization.dll.

### Known Regions
- **0x7f9ac3b2f000** - Live shell buffer (836KB, changes on restart)
- **0x7f9a165a1000** - Contains chat history with timestamps
- Multiple regions contain duplicated/cached data

## Limitations

1. **ASLR**: Buffer addresses change on hackmud restart
2. **Fragmentation**: Data may be split across multiple copies
3. **Old Data**: Some regions contain cached/stale data
4. **Pattern Matching**: Chat patterns need refinement for fragmented data

## Scoring Algorithm (read_live.py)

The dynamic region finder scores each rw-p memory region:
- **+1 per >>> shell prompt** found
- **+0.5 per Unity color tag** `<color=#XXXXXX>`
- **+2 per chat entry** matching `HHMM channel user :::msg:::`
- **+10 per recent timestamp** (within ~2 hours of current time)

Regions with score > 10 are candidates. If the top two candidates have scores within 80% of each other, a RuntimeError is raised to prevent ambiguity.

## Garbage Filtering

Output is cleaned by:
1. Removing non-ASCII unicode (CJK, symbols, etc.)
2. Keeping ASCII + Nordic accented chars (å ä ö ø æ)
3. Collapsing excessive whitespace/dots
4. Deduplicating chat entries by timestamp+user+message prefix

## Future Improvements

For even more reliable shell output capture, implement loki-style vtable matching:
1. Parse ELF symbols for mono_get_root_domain
2. Walk assembly list to find Shell/Parser classes
3. Extract vtable pointers
4. Scan heap for matching vtables
5. Read Queue fields at known offsets

This requires reverse engineering hackmud's class offsets but would provide stable, reliable access.

Current heuristic approach works well for:
- Chat messages (high accuracy)
- Shell commands (moderate accuracy - some fragmentation)

Shell command output (script return values) may still be fragmented due to how Unity TextMeshPro stores rendered text.

## Credits
- dunce - Debugging help and loki reference
- Kaj - Testing and color code verification
- Akira (loki repo) - Mono introspection techniques
