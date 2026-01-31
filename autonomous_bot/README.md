# Autonomous OpenRouter Bot

A fully autonomous bot for hackmud that uses the OpenRouter API to make intelligent decisions about gameplay, responds to Discord commands, and manages files safely.

## Architecture

### Layered Safety Design

```
Decision Layer (OpenRouter AI)
         ↓
Safety & Validation Layer
         ↓
Execution Layer (Actions)
```

Every action flows through the Safety Layer before execution. The AI can *request* actions but cannot *directly execute* them without validation.

## Implemented Components

### Phase 1: Core Infrastructure ✅
- **schemas.py** - Data classes for state, actions, decisions, game events
- **state_manager.py** - Persistent state with atomic writes and action logging
- **bot_config.json** - Configuration for OpenRouter, Discord, safety, behavior

### Phase 2: Safety Layer ✅
- **validator.py** - Main safety validator orchestrating all checks
- **command_validator.py** - Blocks dangerous commands and detects suspicious patterns
- **file_validator.py** - Restricts file access to project directory, protects critical files
- **gc_validator.py** - Tracks GC spending against hourly/daily budgets
- **approval_queue.py** - Manages high-risk actions awaiting human approval

### Phase 3: OpenRouter Integration ✅
- **openrouter_client.py** - API client with conversation context management
- **prompt_builder.py** - (TODO) Build context-aware prompts from observations

### Phase 4: Action Execution
- **action_types.py** - Action type definitions ✅
- **action_executor.py** - (TODO) Execute validated actions using existing tools

### Phase 5: Monitoring
- **discord_monitor.py** - (TODO) Poll Discord for commands
- **game_monitor.py** - (TODO) Poll hackmud game state
- **event_detector.py** - (TODO) Detect interesting game events

### Phase 6: Main Orchestrator
- **autonomous_agent.py** - (TODO) Main event loop: observe → think → validate → act

### Phase 7: Discord Integration
- Update **discord_bot.py** with `!agent` commands - (TODO)

## Configuration

### .env
Add your OpenRouter API key:
```bash
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

### bot_config.json
- OpenRouter settings (model, tokens, temperature)
- Discord settings (poll interval, trusted users, channel)
- Safety settings (blocked commands, GC limits, file protections)
- Behavior settings (autonomy level, log level)

## Safety Mechanisms

### Multi-Layer Validation

1. **Command Blocklist**
   - Blocked: `shutdown`, `quit`, `exit`, `logout`, `clear`, `rm -rf`, `format`, `dd`
   - Suspicious patterns require approval: redirects, pipes, command chaining

2. **File Access Control**
   - Only allowed in `/home/jacob/hackmud/`
   - Protected files: `.env`, `scanner_config.json`, `chat_token.json`
   - Protected dirs: `discord_venv`, `.git`, `*venv`
   - Max file size: 10MB
   - Writes require approval

3. **GC Budget Limits**
   - Per transaction: 1M GC
   - Per hour: 5M GC
   - Per day: 20M GC

4. **Trust Validation**
   - Only trusted Discord users can give commands
   - Trusted users: Jacob (zenchess), Kaj, dunce

5. **Approval Queue**
   - High-risk actions queue for human approval
   - 5-minute timeout, auto-reject if no response
   - Accessible via `!approve <id>` / `!reject <id>`

### Emergency Stop Conditions
- 5+ errors in 10 minutes
- Daily GC budget exceeded
- Discord `!agent stop` command
- Loop detection (same action repeated 5+ times)

## Integration with Existing Tools

### Reuses
- **Scanner API** - Fast memory reading with address caching (160x speedup)
- **send_command.py** - Command injection via xdotool
- **discord_tools/** - Direct Discord API access
- **auto_hack.py** - Reference patterns for game automation

### Runs Alongside discord_bot.py
- discord_bot.py handles instant responses (!shell, !chat, !balance)
- autonomous_agent.py handles complex multi-step tasks
- Both read Discord but serve different purposes

## Usage

### Starting the Bot
```bash
# Start with nohup (background, survives logout)
nohup python3 autonomous_agent.py >> /tmp/autonomous_agent.log 2>&1 &
echo $! > autonomous_agent.pid

# Monitor logs
tail -f /tmp/autonomous_agent.log
```

### Discord Commands
- `!agent status` - Show bot state, active tasks, recent actions
- `!agent task "description"` - Queue task for bot
- `!agent stop` - Emergency stop
- `!agent start` - Resume operations
- `!approve <id>` - Approve high-risk action
- `!reject <id>` - Reject action

### Stopping the Bot
```bash
# Graceful shutdown via Discord
!agent stop

# Or via signal
kill -TERM $(cat autonomous_agent.pid)
```

## Decision Loop

### Observe
1. Poll Discord for new commands from trusted users
2. Read hackmud game state (balance, location, recent output)
3. Detect game events (tells, GC transfers, breaches)
4. Check for pending approvals

### Think
1. Build context-aware prompt from observations
2. Call OpenRouter API
3. Parse AI decision with planned actions
4. Rank actions by priority

### Validate
1. Run through command validator
2. Run through file validator
3. Run through GC validator
4. Check trust for Discord-triggered actions
5. Queue for approval if needed

### Act
1. Execute validated actions in priority order
2. Log all actions and results
3. Update state (balance, location, etc.)
4. Check for emergency stop conditions
5. Report results to Discord if needed

## Data Flow

```
Discord Messages
     ↓
discord_monitor.poll()
     ↓
observations dict
     ↓
openrouter_client.decide()
     ↓
Decision (with actions)
     ↓
safety_validator.validate_action()
     ↓
ValidationResult
     ↓
IF needs_approval:
  → approval_queue.add()
  → Discord notification
  → wait for approval
ELSE IF allowed:
  → action_executor.execute()
  → log result
ELSE:
  → reject, log reason
     ↓
state_manager.save_state()
```

## Testing

### Unit Tests
- [ ] Command validator blocks dangerous commands
- [ ] File validator restricts paths
- [ ] GC validator tracks budgets
- [ ] State serialization/deserialization
- [ ] Action parsing from AI response

### Integration Tests
- [ ] Full observe → think → validate → act cycle
- [ ] Mock OpenRouter response
- [ ] Mock game state
- [ ] Safety checks prevent dangerous actions

### Manual Tests
- [ ] Start bot, verify connects to Discord and game
- [ ] Send Discord command from trusted user
- [ ] Send Discord command from untrusted user (should reject)
- [ ] Trigger high-risk action (should queue for approval)
- [ ] Check logs for decision reasoning
- [ ] Verify state persists after restart

## File Structure

```
autonomous_bot/
├── __init__.py
├── README.md
├── ai/
│   ├── __init__.py
│   ├── openrouter_client.py        ✅
│   └── prompt_builder.py           (TODO)
├── config/
│   ├── __init__.py
│   └── bot_config.json             ✅
├── execution/
│   ├── __init__.py
│   ├── action_executor.py          (TODO)
│   └── action_types.py             ✅
├── monitoring/
│   ├── __init__.py
│   ├── discord_monitor.py          (TODO)
│   ├── game_monitor.py             (TODO)
│   └── event_detector.py           (TODO)
├── safety/
│   ├── __init__.py
│   ├── validator.py                ✅
│   ├── command_validator.py        ✅
│   ├── file_validator.py           ✅
│   ├── gc_validator.py             ✅
│   └── approval_queue.py           ✅
└── state/
    ├── __init__.py
    ├── schemas.py                  ✅
    └── state_manager.py            ✅
```

## Next Steps

1. Create action_executor.py (execute validated actions)
2. Create monitoring modules (Discord, game, event detection)
3. Create autonomous_agent.py (main event loop)
4. Add !agent commands to discord_bot.py
5. Set OPENROUTER_API_KEY in .env
6. Test each component
7. Integrate with existing discord_bot.py
8. Run end-to-end tests

## Performance

- **Observer**: ~100ms to poll Discord and read game state
- **Thinker**: ~1-5 seconds OpenRouter API call
- **Validator**: ~10ms for safety checks
- **Executor**: ~100ms for shell commands (with rate limiting)
- **Overall cycle**: ~2-10 seconds per iteration

## Logging

All actions logged to:
- Console: Real-time info, warnings, errors
- `autonomous_bot/state/bot_state.json`: Current state
- `autonomous_bot/state/action_history.jsonl`: All executed actions
- `autonomous_bot/state/conversation_history.jsonl`: OpenRouter conversations
- `/tmp/autonomous_agent.log`: Full bot output

## Emergency Stop

If the bot gets stuck or misbehaving:

```bash
# Via Discord (fastest)
!agent stop

# Via signal (graceful)
kill -TERM $(cat autonomous_agent.pid)

# Via process (force)
kill -9 $(cat autonomous_agent.pid)
```

The bot will:
1. Save current state
2. Close Scanner connection
3. Notify Discord
4. Exit gracefully
