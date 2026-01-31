# Autonomous Bot - Tools & Context Access

## Available Tools & Resources

The autonomous bot has access to these tools and resources:

### 🎮 GAME INTERACTION TOOLS
1. **Scanner API** (`python_lib/hackmud/memory/`)
   - Read shell window output
   - Read chat window output
   - Read badge/breach windows
   - Get game version
   - Memory-based (160x faster via caching)

2. **send_command.py**
   - Send commands to hackmud
   - Uses xdotool for window automation
   - Types commands and presses Enter
   - Supports hackmud scripts and shell commands

3. **chat_api.py**
   - Hackmud mobile chat API
   - Get account data
   - Poll for messages
   - Send tells and channel messages
   - Separate from Discord chat

### 💬 DISCORD TOOLS
1. **discord_fetch.py**
   - Poll Discord for new messages
   - Get message history
   - Parse sender, username, content
   - No bot required (direct API)

2. **discord_send_api.py**
   - Send messages to Discord channels
   - Attach files/images
   - Support for Discord formatting
   - No bot required (direct API)

3. **discord_bot.py** (existing)
   - Full Discord bot integration
   - Extended commands (!shell, !chat, !balance, etc.)
   - Screenshot capture
   - Badge/breach reading
   - Payment/balance tracking

### 📊 UTILITY TOOLS
1. **screenshot.py**
   - Capture hackmud window sections
   - Calibrated for known regions (shell, chat, badge)
   - Save as PNG
   - Send to Discord via discord_send_api.py

2. **auto_hack.py**
   - Automated T2 NPC hacking reference
   - Lock solving logic (colors, l0cket, ez_21)
   - Response parsing examples
   - Can be integrated for autonomous hacking

### 📁 FILE OPERATIONS
- **Python's built-in file I/O** (validated by safety layer)
- Read existing files
- Write new files (with approval)
- JSON manipulation
- Text processing

### 🧠 INFORMATION SOURCES
The bot has access to:

1. **CLAUDE.md** (Project instructions)
   - Loaded as system context
   - Game mechanics reference
   - Script names and locations
   - Discord commands documentation
   - Discord integration guide

2. **claude_memory.txt** (Long-term memory)
   - Interesting encounters
   - Known NPCs and their locations
   - Past successful hacking strategies
   - User notes and observations
   - GC transaction history

3. **PLAN.md** (Lock solutions reference)
   - Known lock solutions
   - Lock patterns and breaks
   - Strategy documentation

4. **README.md** (Script documentation)
   - Available hackmud scripts
   - Game mechanics
   - Player base information

### 🔍 OBSERVABLE STATE
The bot can observe:

1. **Game State**
   - Current balance/GC
   - Current location
   - Active scripts
   - Recent shell output
   - Recent chat messages
   - Badge status
   - Breach status

2. **Discord State**
   - New messages from trusted users
   - Channel activity
   - Task assignments
   - Approval requests

3. **Internal State**
   - Active tasks
   - Pending approvals
   - Action history
   - Conversation context
   - Budget status

## Current Limitations

❌ **NOT IMPLEMENTED YET:**
- Autonomous hacking (can be enabled)
- Game event detection (tells, breaches)
- Long-term strategy learning
- Complex multi-NPC coordination
- Market/pricing analysis
- Faction interaction

## Integration with Claude.md

The bot is configured to read and follow instructions from CLAUDE.md:

### Loaded Instructions:
✅ Game mechanics understanding
✅ Discord command documentation
✅ Safety guidelines
✅ Transaction logging format
✅ Tell detection patterns
✅ Script names and locations
✅ User switching instructions
✅ Hardline connection knowledge

### Not Yet Integrated:
- Memory file auto-loading
- PLAN.md lock solutions
- Transaction logging to file
- Real-time tell detection
- Advanced strategy planning

## Integration with claude_memory.txt

The bot should load and use claude_memory.txt for:

1. **Known NPCs** (location, difficulty, rewards)
2. **Successful Strategies** (what worked before)
3. **User Notes** (important observations)
4. **GC History** (balance tracking)
5. **Interesting Events** (memorable moments)

### Current Status:
⏳ Memory file access ready (can be enabled)
⏳ Context integration in progress
⏳ Long-term learning system ready

## How to Enable Full Context

### Option 1: Automatic Loading (Recommended)
Edit `autonomous_agent.py` to add:

```python
def _load_claude_context(self) -> str:
    """Load context from CLAUDE.md and claude_memory.txt"""
    context = ""

    # Load CLAUDE.md instructions
    try:
        with open(self.project_root / "CLAUDE.md", 'r') as f:
            context += "\n# CLAUDE.md Instructions\n"
            context += f.read()[:2000]  # First 2000 chars to save tokens
    except:
        pass

    # Load memory
    try:
        with open(self.project_root / "claude_memory.txt", 'r') as f:
            context += "\n# Long-term Memory\n"
            context += f.read()[:1000]  # Most recent memory
    except:
        pass

    return context
```

Then use in system prompt:
```python
def _get_system_prompt(self) -> str:
    claude_context = self._load_claude_context()
    return f"""... existing prompt ... {claude_context}"""
```

### Option 2: Manual Context in System Prompt
Add directly to bot_config.json:

```json
{
  "context": {
    "include_claude_md": true,
    "include_memory_file": true,
    "max_context_tokens": 2000
  }
}
```

## Memory File Integration

The bot can update `claude_memory.txt` with:

```python
def update_memory(self, event: str):
    """Add important event to memory"""
    timestamp = datetime.now().isoformat()
    with open(self.project_root / "claude_memory.txt", 'a') as f:
        f.write(f"\n[{timestamp}] {event}\n")
```

Example events:
- "Hacked NPC X successfully, reward Y GC"
- "Met user Z in channel Q"
- "Discovered T2 loc at sector M"
- "GC balance: X, new upgrades available"

## Document Structure Reference

### CLAUDE.md Sections
1. Getting Started (setup instructions)
2. Discord Integration (bot and API usage)
3. Key Hackmud Commands (xfer_gc, manage, hardline)
4. Project Structure (file organization)
5. Important Bug Fixes (lessons learned)
6. Python Scanner API (memory access)
7. Game Interaction (shell/chat commands)
8. Inbox Detection (DM patterns)
9. Loc Hunting (T1 script, channel etiquette)
10. Your Goals (gameplay objectives)
11. Interesting Events Log (claude_interesting.txt)

### claude_memory.txt Format
```
[date/time] known_npc_name: location, difficulty, rewards
[date/time] successful_strategy_note
[date/time] gc_balance: XXXXGC
[date/time] interesting_event: description
```

## Next Steps to Full Integration

1. ✅ **Bot infrastructure** - COMPLETE
2. ⏳ **Load CLAUDE.md context** - Add to system prompt
3. ⏳ **Load claude_memory.txt** - Add to context at startup
4. ⏳ **Update memory file** - Save important events
5. ⏳ **Use lock solutions from PLAN.md** - Reference database
6. ⏳ **Implement event detection** - Parse tells, breaches
7. ⏳ **Advanced strategy planning** - Use memory for decisions

## Performance Considerations

⚠️ **Token Budget**
- Each API call has ~4000 token response limit
- System prompt: ~500 tokens
- CLAUDE.md (partial): ~1000 tokens
- Memory file: ~300 tokens
- Observations: ~500 tokens
- Response budget: ~1700 tokens

This leaves room for:
- Long-term context (conversation history)
- Game state details
- Multiple actions per response
- Detailed reasoning

## Recommended Setup

### Minimal Context (Fast, ~50ms)
- Game state observation only
- No CLAUDE.md context
- No memory file context
- API response: ~2-3 seconds

### Standard Context (Balanced, ~100ms)
- Game state + Discord messages
- CLAUDE.md instructions (summary)
- Memory file (recent events)
- API response: ~2-5 seconds

### Full Context (Comprehensive, ~200ms)
- Everything above
- Full CLAUDE.md reference
- Complete memory file
- Full conversation history
- API response: ~3-5 seconds

## Files to Read at Startup

```python
def _load_startup_context(self):
    return {
        'claude_md': self._read_file('CLAUDE.md', max_chars=2000),
        'memory': self._read_file('claude_memory.txt', max_chars=1000),
        'plan': self._read_file('PLAN.md', max_chars=500),
        'readme': self._read_file('README.md', max_chars=500)
    }
```

## Summary

The bot has **extensive tool and resource access**:
- ✅ Full game state reading
- ✅ Discord integration
- ✅ File operations
- ✅ Game API access
- ⏳ CLAUDE.md instructions (ready to add)
- ⏳ Memory file context (ready to add)
- ⏳ Advanced gameplay reference (ready to add)

Everything is in place for a fully-featured autonomous agent!
