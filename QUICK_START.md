# Autonomous Bot - Quick Start Guide

## What's Ready

✅ **Complete autonomous bot system** with:
- OpenRouter AI integration (minimax/minimax-m2 model)
- Multi-layer safety validation
- Discord command monitoring
- Game state reading via Scanner API
- Persistent state management
- Approval workflow for high-risk actions

## Prerequisites

✅ OpenRouter API key configured in `.env` (you've already done this!)
✅ Model set to `minimax/minimax-m2` in config
✅ All core components implemented

## Starting the Bot

### Option 1: Simple Start (Foreground)
```bash
cd /home/jacob/hackmud
python3 autonomous_agent.py
```

Watch the output to see:
- `🤖 Autonomous Agent Starting...`
- `🧠 Decision: ...` (AI thinking)
- `✅ Success:` or `❌ Failed:` (action results)

### Option 2: Background Start (Recommended)
```bash
cd /home/jacob/hackmud
nohup python3 autonomous_agent.py >> /tmp/autonomous_agent.log 2>&1 &
echo $! > autonomous_agent.pid

# Monitor logs in real-time
tail -f /tmp/autonomous_agent.log
```

### Option 3: With Custom Model
```bash
export OPENROUTER_MODEL=minimax/minimax-m2
export OPENROUTER_API_KEY=sk-or-v1-your-key
python3 autonomous_agent.py
```

## Stopping the Bot

### Graceful Shutdown
```bash
# Via signal
kill -TERM $(cat autonomous_agent.pid)

# Or just Ctrl+C if running in foreground
```

### Force Quit (Emergency)
```bash
kill -9 $(cat autonomous_agent.pid)
```

## Monitoring

### Check if Running
```bash
ps -p $(cat autonomous_agent.pid)
```

### Watch Logs
```bash
tail -f /tmp/autonomous_agent.log
```

### Check Status
```bash
ls -la autonomous_bot/state/bot_state.json
cat autonomous_bot/state/bot_state.json | jq '.running'
```

## What It Does (Event Loop)

Each cycle (~5 seconds):

1. **Observe** 📡
   - Poll Discord for messages
   - Read hackmud game state
   - Check for pending approvals

2. **Think** 🧠
   - Build context from observations
   - Call OpenRouter API (minimax model)
   - Get AI decision with planned actions

3. **Validate** 🛡️
   - Command blocklist check
   - File access validation
   - GC budget verification
   - Trust validation

4. **Act** ▶️
   - Execute safe actions
   - Queue high-risk actions for approval
   - Log all results
   - Update persistent state

## Discord Commands (Planned)

These will be available once we integrate with discord_bot.py:

```
!agent status           # Show bot state
!agent task "do X"      # Queue task
!agent stop             # Emergency stop
!agent start            # Resume
!approve <action_id>    # Approve queued action
!reject <action_id>     # Reject queued action
```

## Safety Features Active

✅ **Command Blocklist**
- Blocks: shutdown, quit, exit, logout, clear, rm -rf, format, dd
- Requires approval: shell pipes, redirects, chaining

✅ **File Access Control**
- Only `/home/jacob/hackmud/` allowed
- Protected: `.env`, `scanner_config.json`, `*venv`
- Max file size: 10MB

✅ **GC Budget Limits**
- Per transaction: 1M GC
- Per hour: 5M GC
- Per day: 20M GC

✅ **Trust Validation**
- Only 3 trusted Discord users can command

✅ **Emergency Stops**
- 5+ errors in 10 minutes
- Daily budget exceeded
- Manual stop signal

## Configuration

### Main Config File
```
/home/jacob/hackmud/autonomous_bot/config/bot_config.json
```

Key settings:
- `openrouter.model` - Currently: `minimax/minimax-m2`
- `discord.poll_interval` - Check Discord every 10 seconds
- `game.poll_interval` - Check game every 5 seconds
- `safety.gc_limits` - GC spending budgets
- `behavior.autonomous_mode` - Currently: `balanced`

### Environment Variables
```bash
export OPENROUTER_API_KEY=sk-or-v1-...
export OPENROUTER_MODEL=minimax/minimax-m2
```

## Logs

### Real-time Output
```
/tmp/autonomous_agent.log
```

### Action History (JSON Lines)
```
autonomous_bot/state/action_history.jsonl
```

### Conversation History (JSON Lines)
```
autonomous_bot/state/conversation_history.jsonl
```

### Current State
```
autonomous_bot/state/bot_state.json
```

## Testing

### Test 1: Does It Start?
```bash
python3 autonomous_agent.py
# Should see: 🤖 Autonomous Agent Starting...
# Should see: OpenRouter client initialized with model: minimax/minimax-m2
# Press Ctrl+C to stop
```

### Test 2: Can It Read Game State?
```bash
# While running, check logs for:
# ▶️  Executing: read_game_state
# ✅ Success: shell output...
```

### Test 3: Can It Make Decisions?
```bash
# While running, check logs for:
# 🧠 Decision: reasoning...
# Actions: N, Confidence: X%
```

### Test 4: Safety Systems Work
```bash
# In bot logs you should see safety messages like:
# 🚫 Action blocked: Blocked command: shutdown
# ⏳ Action requires approval: Write file...
```

## Troubleshooting

### Bot Won't Start
```bash
# Check Python version
python3 --version  # Need 3.8+

# Check dependencies
python3 -c "import asyncio; print('OK')"

# Check config
cat autonomous_bot/config/bot_config.json | python3 -m json.tool
```

### OpenRouter Error
```bash
# Check API key
echo $OPENROUTER_API_KEY  # Should not be empty

# Check model name
python3 -c "from autonomous_bot.ai.openrouter_client import OpenRouterClient; c = OpenRouterClient(model='minimax/minimax-m2'); print(c.model)"
```

### No Discord Messages
```bash
# Check discord_fetch.py works
python3 discord_tools/discord_fetch.py -n 5

# Check it returns messages in format:
# [timestamp] discord_id/username/displayname -> "message"
```

### No Game State Reading
```bash
# Check Scanner API works
python3 -c "from hackmud.memory import Scanner; s = Scanner(); s.connect(); print(s.read_window('shell', lines=5))"
```

## Performance

- **Decision cycle**: ~5-10 seconds
- **API call time**: ~1-5 seconds (OpenRouter)
- **Validation**: ~10ms
- **Memory usage**: ~100-200MB
- **CPU usage**: Low (async, event-driven)

## Next Steps

1. **Start the bot** and monitor logs
2. **Integrate with discord_bot.py** to add `!agent` commands
3. **Add monitoring modules** for Discord/game event detection
4. **Create integration tests** to verify all subsystems

## Architecture Reminder

```
Discord/Game Input
        ↓
   Observations
        ↓
   OpenRouter API (minimax-m2)
        ↓
   Safety Validators
        ↓
   Action Executor
        ↓
   Persistent State
```

## Support

For issues:
1. Check logs: `tail -f /tmp/autonomous_agent.log`
2. Review config: `cat autonomous_bot/config/bot_config.json | jq .`
3. Check state: `cat autonomous_bot/state/bot_state.json | jq '.running'`

Good luck! 🚀
