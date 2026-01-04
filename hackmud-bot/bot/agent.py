#!/usr/bin/env python3
"""
Autonomous hackmud agent powered by Claude Code
Uses stdin pipe pattern (like mindcraft) for reliable communication
"""

import subprocess
import json
import time
import os
import sys
import re
from pathlib import Path
from datetime import datetime
import threading
import socketio

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent
LINUX_DIR = PROJECT_DIR.parent  # The parent of hackmud-bot is the linux tools directory

MEMORY_FILE = SCRIPT_DIR / "memory.json"
STATE_FILE = SCRIPT_DIR / "state.json"
LOG_FILE = LINUX_DIR / "responses.log"

# Socket.IO client
sio = socketio.Client()
connected = False

# Threading
state_lock = threading.Lock()
user_message_event = threading.Event()

# Conversation history for context
conversation_history = []

def load_memory():
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "known_npcs": [],
        "cracked_npcs": [],
        "failed_npcs": [],
        "lock_solutions": {},
        "gc_transferred": 0,
        "notes": [],
        "strategies": [],
        "session_start": datetime.now().isoformat()
    }

def save_memory(memory):
    memory["last_activity"] = datetime.now().isoformat()
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def load_state():
    with state_lock:
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "status": "idle",
            "current_task": None,
            "last_command": None,
            "user_message_queue": [],
            "pause_requested": False,
            "hardline_active": False,
            "hardline_expires": None
        }

def save_state(state):
    with state_lock:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)

def get_recent_responses(n=10):
    """Get recent responses from log file (legacy method)"""
    if not LOG_FILE.exists():
        return ""
    try:
        result = subprocess.run(
            ['python3', str(LINUX_DIR / 'get_responses.py'), '-n', str(n), '--raw'],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout
    except:
        return ""

def ocr_game_screen():
    """OCR the hackmud window to get current game state"""
    try:
        result = subprocess.run(
            ['python3', str(LINUX_DIR / 'ocr_screen.py')],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            emit_log(f"OCR failed: {result.stderr}", level="error")
            return ""
    except Exception as e:
        emit_log(f"OCR error: {e}", level="error")
        return ""

def send_game_command(command):
    try:
        result = subprocess.run(
            ['python3', str(LINUX_DIR / 'send_command.py'), command],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        emit_log(f"Error sending command: {e}")
        return False

def establish_hardline():
    emit_log("Running hardline.sh (~15 seconds)...")
    try:
        result = subprocess.run(
            ['bash', str(LINUX_DIR / 'hardline.sh')],
            capture_output=True, text=True, timeout=60
        )
        success = "complete" in result.stdout.lower()
        if success:
            emit_log("Hardline established!")
            state = load_state()
            state['hardline_active'] = True
            state['hardline_expires'] = datetime.now().timestamp() + 120
            save_state(state)
        return success
    except Exception as e:
        emit_log(f"Hardline error: {e}")
        return False

def disconnect_hardline():
    emit_log("Disconnecting hardline...")
    send_game_command('kernel.hardline{dc:true}')
    state = load_state()
    state['hardline_active'] = False
    state['hardline_expires'] = None
    save_state(state)

def emit_log(message, level="info"):
    global connected
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {"time": timestamp, "level": level, "message": message}
    print(f"[{timestamp}] {message}")
    if connected:
        try:
            sio.emit('bot_log', log_entry)
        except:
            pass

def emit_state(state, memory):
    global connected
    if connected:
        try:
            sio.emit('bot_state', {"state": state, "memory": memory})
        except:
            pass

def emit_chat(message, sender="bot"):
    global connected
    if connected:
        try:
            sio.emit('chat_message', {
                "sender": sender,
                "message": message,
                "time": datetime.now().strftime("%H:%M:%S")
            })
        except:
            pass

@sio.event
def connect():
    global connected
    connected = True
    emit_log("Connected to web server")

@sio.event
def disconnect():
    global connected
    connected = False
    print("Disconnected from web server")

@sio.on('user_message')
def on_user_message(data):
    message = data.get('message', '')
    emit_log(f"User message: {message[:50]}...")
    state = load_state()
    state['user_message_queue'].append(message)
    save_state(state)
    user_message_event.set()

@sio.on('command')
def on_command(data):
    cmd = data.get('command', '')
    state = load_state()
    if cmd == 'pause':
        state['pause_requested'] = True
        state['status'] = 'paused'
        save_state(state)
        emit_log("Paused")
        emit_chat("Paused.", sender="bot")
    elif cmd == 'resume':
        state['pause_requested'] = False
        state['status'] = 'playing'
        save_state(state)
        emit_log("Resumed")
        emit_chat("Resuming.", sender="bot")
    elif cmd == 'stop':
        emit_log("Stopping...")
        emit_chat("Goodbye!", sender="bot")
        time.sleep(1)
        os._exit(0)

def connect_to_server():
    global connected
    for i in range(10):
        try:
            sio.connect('http://localhost:3000')
            return True
        except:
            print(f"Waiting for server... ({i+1}/10)")
            time.sleep(2)
    return False

def run_claude_code(prompt, timeout=60):
    """
    Run Claude Code using stdin pipe pattern (like mindcraft).
    Spawns process, sends prompt via stdin, reads JSON response from stdout.
    """
    try:
        emit_log("Spawning Claude...")

        # Spawn claude with JSON output format
        process = subprocess.Popen(
            ['claude', '--output-format', 'json'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(LINUX_DIR)
        )

        # Send prompt via stdin and close
        stdout, stderr = process.communicate(input=prompt, timeout=timeout)

        if process.returncode != 0:
            emit_log(f"Claude error (code {process.returncode}): {stderr[:200]}", level="error")
            return None

        # Parse JSON response
        try:
            response = json.loads(stdout.strip())

            if response.get('is_error'):
                emit_log(f"Claude returned error: {response.get('result', 'Unknown')}", level="error")
                return None

            result = response.get('result', '')
            emit_log(f"Claude: {result[:150]}...")
            return result

        except json.JSONDecodeError:
            # If not JSON, return raw output
            emit_log(f"Raw response: {stdout[:150]}...")
            return stdout.strip()

    except subprocess.TimeoutExpired:
        emit_log("Claude timeout!", level="error")
        process.kill()
        return None
    except Exception as e:
        emit_log(f"Error: {e}", level="error")
        return None

def parse_actions(response):
    """Parse Claude's response into actions"""
    if not response:
        return []

    actions = []
    for line in response.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        if line.startswith('GAME_COMMAND:'):
            cmd = line[len('GAME_COMMAND:'):].strip()
            actions.append(('game_command', cmd))
        elif line == 'HARDLINE' or line.startswith('HARDLINE'):
            actions.append(('hardline', None))
        elif 'DISCONNECT_HARDLINE' in line.upper():
            actions.append(('disconnect_hardline', None))
        elif line.startswith('MEMORY_UPDATE:'):
            try:
                data = line[len('MEMORY_UPDATE:'):].strip()
                update = json.loads(data)
                actions.append(('memory_update', update))
            except:
                pass
        elif line.startswith('USER_RESPONSE:'):
            msg = line[len('USER_RESPONSE:'):].strip()
            actions.append(('user_response', msg))
        elif line.startswith('STATUS:'):
            status = line[len('STATUS:'):].strip().lower()
            actions.append(('status', status))
        elif line.startswith('WAIT:'):
            try:
                secs = int(line[len('WAIT:'):].strip())
                actions.append(('wait', secs))
            except:
                pass
        elif line.startswith('LOG:'):
            msg = line[len('LOG:'):].strip()
            actions.append(('log', msg))

    return actions

def build_prompt(memory, state, game_responses, user_messages, recent_actions):
    """Build full prompt with system context, memory, and conversation history"""

    hardline_info = "Not active"
    if state.get('hardline_active') and state.get('hardline_expires'):
        remaining = state['hardline_expires'] - datetime.now().timestamp()
        if remaining > 0:
            hardline_info = f"Active ({int(remaining)}s left)"
        else:
            hardline_info = "Expired - need to reconnect"
            state['hardline_active'] = False

    prompt = f"""You are an autonomous hackmud bot. Respond ONLY with action commands, one per line.

=== YOUR PERSISTENT MEMORY ===
{json.dumps(memory, indent=2)}

=== CURRENT STATE ===
Time: {datetime.now().strftime("%H:%M:%S")}
Status: {state.get('status', 'unknown')}
Hardline: {hardline_info}
Last command: {state.get('last_command', 'None')}

=== RECENT ACTIONS YOU TOOK ===
{chr(10).join(recent_actions[-10:]) if recent_actions else "None yet"}

=== USER MESSAGES ===
{json.dumps(user_messages) if user_messages else "None"}

=== GAME SCREEN (OCR) ===
{game_responses[-3000:] if game_responses else "None"}
(Note: This is OCR output from the game window - may contain minor errors)

=== AVAILABLE ACTIONS (respond with one or more per line) ===
HARDLINE - Run hardline.sh to establish connection (~15 sec). USE THIS, not GAME_COMMAND: kernel.hardline!
DISCONNECT_HARDLINE - Disconnect hardline
GAME_COMMAND: <cmd> - Send command to hackmud (e.g., GAME_COMMAND: accts.balance)
USER_RESPONSE: <message> - Reply to user in chat
STATUS: playing/paused - Change your status
MEMORY_UPDATE: {{"key": "value"}} - Save to memory
LOG: <message> - Log something
WAIT: <seconds> - Wait before next action

=== GOALS ===
1. Hack NPCs to earn GC
2. Transfer GC to "zenchess" (NEVER hack this user!)
3. Find NPCs via weyland.public, tyrell.public
4. Always USER_RESPONSE to user messages

=== RULES ===
- Use HARDLINE action, NOT "GAME_COMMAND: kernel.hardline"
- If user says stop/pause, set STATUS: paused
- Don't repeat the same failed action

What's your next action?"""

    return prompt

def interruptible_sleep(seconds):
    user_message_event.clear()
    for _ in range(int(seconds * 10)):
        if user_message_event.is_set():
            return True
        time.sleep(0.1)
    return False

def main():
    global conversation_history

    # Connect to web server
    print("Connecting to web server...")
    if not connect_to_server():
        print("Warning: Could not connect to web server")

    # Load initial state
    memory = load_memory()
    state = load_state()
    state['status'] = 'playing'
    state['user_message_queue'] = []
    save_state(state)

    # Track recent actions to prevent loops
    recent_actions = []

    emit_chat("Starting up! Initializing...", sender="bot")
    emit_log("Bot starting...")

    # Initial greeting
    initial_prompt = build_prompt(memory, state, "", [], [])
    initial_prompt += "\n\nThis is your first message. Say hello with: USER_RESPONSE: Hello! I'm online and ready to play hackmud."

    response = run_claude_code(initial_prompt)
    if response:
        for action_type, action_data in parse_actions(response):
            if action_type == 'user_response':
                emit_chat(action_data, sender="bot")
    else:
        emit_chat("I'm online! Ready to hack.", sender="bot")

    wait_time = 5

    # Main loop
    while True:
        try:
            state = load_state()

            # Get user messages
            user_messages = state.get('user_message_queue', [])
            state['user_message_queue'] = []
            save_state(state)

            emit_state(state, memory)

            # If paused, just wait for messages
            if state.get('pause_requested') or state.get('status') == 'paused':
                if user_messages:
                    prompt = build_prompt(memory, state, "", user_messages, recent_actions)
                    response = run_claude_code(prompt)
                    if response:
                        for action_type, action_data in parse_actions(response):
                            if action_type == 'user_response':
                                emit_chat(action_data, sender="bot")
                            elif action_type == 'status':
                                state['status'] = action_data
                                state['pause_requested'] = (action_data == 'paused')
                                save_state(state)

                if interruptible_sleep(2):
                    continue
                continue

            # Get game state via OCR
            game_responses = ocr_game_screen()
            if not game_responses:
                # Fallback to log file if OCR fails
                game_responses = get_recent_responses(10)

            # Build prompt with full context
            prompt = build_prompt(memory, state, game_responses, user_messages, recent_actions)
            response = run_claude_code(prompt)

            if not response:
                emit_log("No response, waiting...")
                time.sleep(5)
                continue

            # Execute actions
            actions = parse_actions(response)

            if not actions:
                emit_log("No actions in response")
                time.sleep(3)
                continue

            for action_type, action_data in actions:
                state = load_state()
                if state.get('user_message_queue'):
                    break

                # Track action
                action_str = f"{action_type}: {action_data}" if action_data else action_type
                recent_actions.append(f"[{datetime.now().strftime('%H:%M:%S')}] {action_str}")
                if len(recent_actions) > 20:
                    recent_actions = recent_actions[-20:]

                if action_type == 'game_command':
                    emit_log(f"Command: {action_data}")
                    state['last_command'] = action_data
                    save_state(state)
                    send_game_command(action_data)
                    interruptible_sleep(2)

                elif action_type == 'hardline':
                    recent_actions.append(f"[{datetime.now().strftime('%H:%M:%S')}] HARDLINE started")
                    establish_hardline()
                    recent_actions.append(f"[{datetime.now().strftime('%H:%M:%S')}] HARDLINE completed")

                elif action_type == 'disconnect_hardline':
                    disconnect_hardline()

                elif action_type == 'memory_update':
                    for key, value in action_data.items():
                        if isinstance(value, list) and key in memory and isinstance(memory[key], list):
                            memory[key].extend(value)
                        else:
                            memory[key] = value
                    save_memory(memory)
                    emit_log(f"Memory updated")

                elif action_type == 'user_response':
                    emit_chat(action_data, sender="bot")

                elif action_type == 'status':
                    state['status'] = action_data
                    state['pause_requested'] = (action_data == 'paused')
                    save_state(state)

                elif action_type == 'wait':
                    wait_time = action_data

                elif action_type == 'log':
                    emit_log(action_data)

            # Reload fresh state (may have been updated by action handlers like establish_hardline)
            state = load_state()
            emit_state(state, memory)

            if interruptible_sleep(wait_time):
                continue
            wait_time = 5

        except KeyboardInterrupt:
            emit_log("Shutting down...")
            break
        except Exception as e:
            emit_log(f"Error: {e}", level="error")
            import traceback
            traceback.print_exc()
            interruptible_sleep(5)

if __name__ == '__main__':
    main()
