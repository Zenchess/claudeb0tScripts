#!/usr/bin/env python3
"""Web dashboard for hackmud terminal - screenshot-based with input support"""
import base64
import json
import subprocess
import threading
import time
import os
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
from PIL import Image

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Trusted Discord user IDs who can send commands
TRUSTED_DISCORD_USERS = {
    190743971469721600,    # Zenchess
    1081873483300093952,   # Kaj
    626075347225411584,    # dunce
}

# HTML template with screenshot display and command input
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>hackmud Terminal</title>
    <style>
        @font-face {
            font-family: 'WhiteRabbit';
            src: url('/static/WhiteRabbitHackmudExtended.ttf') format('truetype');
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body {
            background: #0a0a0a;
            color: #00ff00;
            font-family: 'WhiteRabbit', 'Consolas', monospace;
            font-size: 11px;
            padding: 4px;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }
        body {
            display: flex;
            flex-direction: column;
            max-width: 100vw;
            max-height: 100vh;
        }
        #status {
            color: #888;
            margin-bottom: 4px;
            font-size: 10px;
            text-align: center;
        }
        .connected { color: #0f0; }
        .disconnected { color: #f00; }
        .view-only { color: #ff8000; }
        #main-container {
            display: flex;
            gap: 4px;
            flex: 1;
            min-height: 0;
            max-height: calc(100vh - 60px);
            overflow: hidden;
        }
        .panel {
            display: flex;
            flex-direction: column;
            min-height: 0;
            overflow: hidden;
        }
        .panel-label {
            color: #888;
            font-size: 9px;
            margin-bottom: 2px;
            text-transform: uppercase;
            flex-shrink: 0;
        }
        #shell-panel {
            flex: 2;
        }
        #right-panel {
            flex: 1;
            max-width: 30vw;
        }
        .screenshot {
            border: 1px solid #333;
            width: 100%;
            height: 100%;
            object-fit: contain;
            image-rendering: pixelated;
        }
        #input-area {
            margin-top: 5px;
            display: flex;
            gap: 5px;
            flex-shrink: 0;
        }
        #command-input {
            flex: 1;
            background: #111;
            border: 1px solid #333;
            color: #0f0;
            font-family: 'WhiteRabbit', 'Consolas', monospace;
            font-size: 12px;
            padding: 5px;
            outline: none;
        }
        #command-input:focus {
            border-color: #0f0;
        }
        #command-input:disabled {
            background: #1a1a1a;
            color: #666;
            border-color: #222;
        }
        #send-btn {
            background: #1a3320;
            border: 1px solid #0f0;
            color: #0f0;
            padding: 5px 10px;
            font-family: 'WhiteRabbit', 'Consolas', monospace;
            font-size: 12px;
            cursor: pointer;
        }
        #send-btn:hover {
            background: #2a4330;
        }
        #send-btn:disabled {
            background: #1a1a1a;
            border-color: #333;
            color: #666;
            cursor: not-allowed;
        }
        #hardline-btn {
            background: #332a1a;
            border: 1px solid #f80;
            color: #f80;
            padding: 5px 10px;
            font-family: 'WhiteRabbit', 'Consolas', monospace;
            font-size: 12px;
            cursor: pointer;
        }
        #hardline-btn:hover {
            background: #433a2a;
        }
        #hardline-btn:disabled {
            background: #1a1a1a;
            border-color: #333;
            color: #666;
            cursor: not-allowed;
        }
        #hardline-btn.running {
            background: #1a331a;
            border-color: #0f0;
            color: #0f0;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .viewers {
            color: #888;
            margin-top: 4px;
            font-size: 9px;
            text-align: center;
            flex-shrink: 0;
        }
        #user-info {
            color: #666;
            font-size: 9px;
        }
    </style>
</head>
<body>
    <div id="status">Connecting...</div>
    <div id="main-container">
        <div class="panel" id="shell-panel">
            <div class="panel-label">Shell</div>
            <img id="screenshot-shell" class="screenshot" alt="shell">
        </div>
        <div class="panel" id="right-panel">
            <div class="panel-label">Right Side (Chat/Scratch/Breach/Badge)</div>
            <img id="screenshot-right" class="screenshot" alt="right_side">
        </div>
    </div>
    <div id="input-area">
        <input type="text" id="command-input" placeholder="Enter command..." autocomplete="off" disabled>
        <button id="send-btn" disabled>Send</button>
        <button id="hardline-btn" disabled>Hardline</button>
    </div>
    <div class="viewers"><span id="viewers">Viewers: 1</span> | <span id="user-info">Loading user...</span></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>
    <script type="module">
        import { DiscordSDK } from 'https://esm.sh/@discord/embedded-app-sdk';

        const shellImg = document.getElementById('screenshot-shell');
        const rightImg = document.getElementById('screenshot-right');
        const status = document.getElementById('status');
        const commandInput = document.getElementById('command-input');
        const sendBtn = document.getElementById('send-btn');
        const hardlineBtn = document.getElementById('hardline-btn');
        const viewers = document.getElementById('viewers');
        const userInfo = document.getElementById('user-info');

        let usePolling = false;
        let socket = null;
        let pollInterval = null;
        let discordUserId = null;
        let discordUsername = null;
        let canSendCommands = false;

        // Initialize Discord SDK
        async function initDiscord() {
            try {
                const discordSdk = new DiscordSDK('1456296098573439087');
                await discordSdk.ready();
                console.log('Discord SDK ready, frame_id:', discordSdk.frameId);

                // Get user ID from SDK (available after ready() in Activity context)
                // The SDK exposes the user who launched the activity
                discordUserId = discordSdk.userId;

                if (discordUserId) {
                    // Check if user can send commands
                    const permResp = await fetch(`/api/check-permission?user_id=${discordUserId}`);
                    const permData = await permResp.json();
                    canSendCommands = permData.can_send;

                    if (canSendCommands) {
                        commandInput.disabled = false;
                        sendBtn.disabled = false;
                        hardlineBtn.disabled = false;
                        userInfo.innerHTML = `<span style="color:#0f0">User ${discordUserId}</span> (can send)`;
                    } else {
                        userInfo.innerHTML = `<span style="color:#ff8000">User ${discordUserId}</span> (view only)`;
                    }
                } else {
                    // No user ID available - view only
                    userInfo.textContent = 'Unknown user (view only)';
                }
            } catch (e) {
                console.log('Discord SDK init error (running outside Activity?):', e);
                userInfo.textContent = 'Not in Discord Activity';
                // Allow commands when not in Discord Activity (direct access)
                commandInput.disabled = false;
                sendBtn.disabled = false;
                hardlineBtn.disabled = false;
                canSendCommands = true;
            }
        }

        // Try WebSocket first, fallback to REST polling
        function initSocket() {
            try {
                socket = io({
                    transports: ['websocket', 'polling'],
                    reconnection: true,
                    reconnectionAttempts: 3,
                    timeout: 5000
                });

                socket.on('connect', () => {
                    const modeText = canSendCommands ? 'Live hackmud view' : 'View only mode';
                    status.innerHTML = '<span class="connected">Connected (WebSocket)</span> - ' + modeText;
                    usePolling = false;
                    if (pollInterval) {
                        clearInterval(pollInterval);
                        pollInterval = null;
                    }
                });

                socket.on('connect_error', (err) => {
                    console.log('WebSocket failed, using REST polling:', err);
                    startPolling();
                });

                socket.on('disconnect', () => {
                    status.innerHTML = '<span class="disconnected">Disconnected</span> - Reconnecting...';
                    setTimeout(() => {
                        if (!socket.connected) startPolling();
                    }, 3000);
                });

                socket.on('screenshot', (data) => {
                    shellImg.src = 'data:image/jpeg;base64,' + data.image;
                });

                socket.on('right_screenshot', (data) => {
                    rightImg.src = 'data:image/jpeg;base64,' + data.image;
                });

                socket.on('viewer_count', (data) => {
                    viewers.textContent = 'Viewers: ' + data.count;
                });

                socket.on('command_sent', (data) => {
                    commandInput.style.borderColor = '#0f0';
                    setTimeout(() => { commandInput.style.borderColor = '#333'; }, 200);
                });

                socket.on('permission_denied', (data) => {
                    commandInput.style.borderColor = '#f00';
                    status.innerHTML = '<span class="disconnected">Permission denied</span> - View only mode';
                    setTimeout(() => { commandInput.style.borderColor = '#333'; }, 1000);
                });

                // Timeout - if no screenshot in 5 seconds, start polling
                setTimeout(() => {
                    if (!shellImg.src || shellImg.src === '' || shellImg.src === window.location.href) {
                        console.log('No screenshot received, starting REST polling');
                        startPolling();
                    }
                }, 5000);

            } catch (e) {
                console.log('Socket.io init failed:', e);
                startPolling();
            }
        }

        // REST polling fallback
        function startPolling() {
            if (pollInterval) return;
            usePolling = true;
            const modeText = canSendCommands ? 'Live hackmud view' : 'View only mode';
            status.innerHTML = '<span class="connected">Connected (Polling)</span> - ' + modeText;

            async function fetchScreenshots() {
                try {
                    // Fetch shell screenshot
                    const shellResp = await fetch('/api/screenshot?area=shell');
                    const shellData = await shellResp.json();
                    if (shellData.image) {
                        shellImg.src = 'data:image/jpeg;base64,' + shellData.image;
                    }
                    // Fetch right_side screenshot
                    const rightResp = await fetch('/api/screenshot?area=right_side');
                    const rightData = await rightResp.json();
                    if (rightData.image) {
                        rightImg.src = 'data:image/jpeg;base64,' + rightData.image;
                    }
                } catch (e) {
                    console.error('Polling error:', e);
                }
            }

            fetchScreenshots(); // Get first screenshots immediately
            pollInterval = setInterval(fetchScreenshots, 3000); // Then every 3 seconds
        }

        function sendCommand() {
            if (!canSendCommands) {
                status.innerHTML = '<span class="disconnected">Permission denied</span> - View only mode';
                return;
            }
            const cmd = commandInput.value.trim();
            if (cmd) {
                if (socket && socket.connected) {
                    socket.emit('send_command', { command: cmd, user_id: discordUserId });
                } else {
                    // REST fallback for commands
                    fetch('/api/command', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({command: cmd, user_id: discordUserId})
                    });
                }
                commandInput.value = '';
                commandInput.style.borderColor = '#0f0';
                setTimeout(() => { commandInput.style.borderColor = '#333'; }, 200);
            }
        }

        sendBtn.addEventListener('click', sendCommand);
        commandInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendCommand();
        });

        // Hardline button handler
        async function runHardline() {
            if (!canSendCommands) {
                status.innerHTML = '<span class="disconnected">Permission denied</span> - View only mode';
                return;
            }
            hardlineBtn.disabled = true;
            hardlineBtn.classList.add('running');
            hardlineBtn.textContent = 'Running...';
            status.innerHTML = '<span style="color:#f80">Running hardline sequence (takes ~15 seconds)...</span>';

            try {
                const resp = await fetch('/api/hardline', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: discordUserId})
                });
                const data = await resp.json();
                if (data.success) {
                    status.innerHTML = '<span class="connected">Hardline complete</span>';
                } else {
                    status.innerHTML = '<span class="disconnected">Hardline failed: ' + (data.error || 'unknown error') + '</span>';
                }
            } catch (e) {
                status.innerHTML = '<span class="disconnected">Hardline error: ' + e.message + '</span>';
            } finally {
                hardlineBtn.disabled = false;
                hardlineBtn.classList.remove('running');
                hardlineBtn.textContent = 'Hardline';
            }
        }

        hardlineBtn.addEventListener('click', runHardline);

        // Tab completion for common hackmud scripts
        const COMPLETIONS = [
            // Chat
            'chats.send', 'chats.tell', 'chats.join', 'chats.leave', 'chats.channels', 'chats.users',
            // System
            'sys.upgrades', 'sys.manage', 'sys.status', 'sys.access_log', 'sys.cull', 'sys.loc',
            // Scripts
            'scripts.fullsec', 'scripts.highsec', 'scripts.midsec', 'scripts.lowsec', 'scripts.nullsec',
            'scripts.trust', 'scripts.get_level', 'scripts.quine', 'scripts.user',
            // Market
            'market.browse', 'market.sell', 'market.buy',
            // Users
            'users.inspect', 'users.top',
            // Accts
            'accts.balance', 'accts.transactions', 'accts.xfer_gc_to',
            // Other
            'kernel.hardline', 'trust.me', 'aon.memb', 'expose.gl0bal',
            // Popular user scripts
            't0asted.t1', 'k3ys.public'
        ];

        let completionIndex = -1;
        let completionMatches = [];

        commandInput.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                e.preventDefault();
                const text = commandInput.value;
                const cursorPos = commandInput.selectionStart;

                // Find start of current word
                let wordStart = cursorPos;
                while (wordStart > 0 && text[wordStart - 1] !== ' ' && text[wordStart - 1] !== '{') {
                    wordStart--;
                }
                const currentWord = text.substring(wordStart, cursorPos).toLowerCase();

                if (currentWord.length === 0) return;

                // Find matching completions
                if (completionIndex === -1 || !completionMatches.length) {
                    completionMatches = COMPLETIONS.filter(c => c.toLowerCase().startsWith(currentWord));
                    completionIndex = 0;
                } else {
                    completionIndex = (completionIndex + 1) % completionMatches.length;
                }

                if (completionMatches.length > 0) {
                    const completion = completionMatches[completionIndex];
                    commandInput.value = text.substring(0, wordStart) + completion + text.substring(cursorPos);
                    commandInput.setSelectionRange(wordStart + completion.length, wordStart + completion.length);
                }
            } else {
                // Reset completion state on other keys
                completionIndex = -1;
                completionMatches = [];
            }
        });

        // Initialize
        await initDiscord();
        initSocket();
    </script>
</body>
</html>
'''

# Track connected clients
connected_clients = 0

def take_screenshot(area='shell'):
    """Take screenshot of hackmud using screenshot.py, compressed as JPEG"""
    try:
        # Use different file for each area to avoid race conditions
        png_file = f'/tmp/hackmud_live_{area}.png'
        jpg_file = f'/tmp/hackmud_live_{area}.jpg'
        result = subprocess.run(
            ['python3', 'screenshot.py', area, '-o', png_file],
            capture_output=True, text=True, timeout=10,
            cwd='/home/jacob/hackmud'
        )
        if os.path.exists(png_file):
            # Compress to JPEG with quality 88 (good balance of size vs quality)
            img = Image.open(png_file)
            img = img.convert('RGB')  # JPEG doesn't support alpha
            img.save(jpg_file, 'JPEG', quality=88, optimize=True)
            with open(jpg_file, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Screenshot error: {e}")
    return None

def screenshot_streamer():
    """Background thread to stream screenshots"""
    last_shell_image = None
    last_right_image = None
    while True:
        try:
            if connected_clients > 0:
                # Shell screenshot
                shell_image = take_screenshot('shell')
                if shell_image and shell_image != last_shell_image:
                    socketio.emit('screenshot', {'image': shell_image})
                    last_shell_image = shell_image
                # Right side screenshot (chat/scratch/breach/badge)
                right_image = take_screenshot('right_side')
                if right_image and right_image != last_right_image:
                    socketio.emit('right_screenshot', {'image': right_image})
                    last_right_image = right_image
        except Exception as e:
            print(f"Streamer error: {e}")
        time.sleep(1.5)  # Update every 1.5 seconds

@socketio.on('connect')
def handle_connect():
    global connected_clients
    connected_clients += 1
    emit('viewer_count', {'count': connected_clients}, broadcast=True)
    # Send initial screenshots immediately
    shell_image = take_screenshot('shell')
    if shell_image:
        emit('screenshot', {'image': shell_image})
    right_image = take_screenshot('right_side')
    if right_image:
        emit('right_screenshot', {'image': right_image})

@socketio.on('disconnect')
def handle_disconnect():
    global connected_clients
    connected_clients = max(0, connected_clients - 1)
    socketio.emit('viewer_count', {'count': connected_clients})

def is_trusted_user(user_id):
    """Check if a Discord user ID is trusted to send commands"""
    if user_id is None:
        return True  # Allow when not in Discord Activity (direct access)
    try:
        return int(user_id) in TRUSTED_DISCORD_USERS
    except (ValueError, TypeError):
        return False

@socketio.on('send_command')
def handle_command(data):
    """Handle command sent from web client"""
    user_id = data.get('user_id')

    # Check if user is trusted
    if not is_trusted_user(user_id):
        emit('permission_denied', {'error': 'You do not have permission to send commands'})
        return

    command = data.get('command', '').strip()
    if command:
        try:
            subprocess.run(
                ['python3', 'send_command.py', command],
                capture_output=True, text=True, timeout=5,
                cwd='/home/jacob/hackmud'
            )
            emit('command_sent', {'success': True})
            # Take screenshot after command to show result
            time.sleep(0.5)
            image = take_screenshot('shell')
            if image:
                socketio.emit('screenshot', {'image': image})
        except Exception as e:
            print(f"Command error: {e}")
            emit('command_sent', {'success': False, 'error': str(e)})

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/screenshot')
def api_screenshot():
    """REST endpoint to get screenshot as base64 - fallback for WebSocket issues"""
    area = request.args.get('area', 'shell')
    if area not in ['shell', 'chat', 'badge', 'breach', 'scratch', 'right_side', 'full']:
        area = 'shell'
    image = take_screenshot(area)
    if image:
        return {'image': image, 'timestamp': time.time(), 'area': area}
    return {'error': 'Screenshot failed'}, 500

@app.route('/api/command', methods=['POST'])
def api_command():
    """REST endpoint to send command - fallback for WebSocket issues"""
    data = request.get_json()
    user_id = data.get('user_id')

    # Check if user is trusted
    if not is_trusted_user(user_id):
        return {'error': 'Permission denied'}, 403

    command = data.get('command', '').strip()
    if command:
        try:
            subprocess.run(
                ['python3', 'send_command.py', command],
                capture_output=True, text=True, timeout=5,
                cwd='/home/jacob/hackmud'
            )
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    return {'error': 'No command provided'}, 400

@app.route('/api/check-permission')
def api_check_permission():
    """Check if a Discord user ID has permission to send commands"""
    user_id = request.args.get('user_id')
    can_send = is_trusted_user(user_id)
    return {'can_send': can_send, 'user_id': user_id}

@app.route('/api/hardline', methods=['POST'])
def api_hardline():
    """Run the hardline sequence"""
    data = request.get_json()
    user_id = data.get('user_id')

    # Check if user is trusted
    if not is_trusted_user(user_id):
        return {'error': 'Permission denied'}, 403

    try:
        # Run hardline.sh script (takes about 15 seconds)
        result = subprocess.run(
            ['bash', 'hardline.sh'],
            capture_output=True, text=True, timeout=30,
            cwd='/home/jacob/hackmud'
        )
        if result.returncode == 0:
            return {'success': True, 'output': result.stdout}
        else:
            return {'success': False, 'error': result.stderr or 'Hardline failed'}, 500
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Hardline timed out'}, 500
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@app.route('/api/discord/token', methods=['POST'])
def api_discord_token():
    """Exchange Discord OAuth code for access token"""
    import requests
    from dotenv import load_dotenv
    load_dotenv()

    data = request.get_json()
    code = data.get('code')

    if not code:
        return {'error': 'No code provided'}, 400

    client_id = os.environ.get('DISCORD_CLIENT_ID', '1456296098573439087')
    client_secret = os.environ.get('DISCORD_CLIENT_SECRET')

    if not client_secret:
        # Return error but allow activity to work in view-only mode
        return {'error': 'Discord OAuth not configured'}, 500

    # Exchange code for token
    try:
        token_resp = requests.post('https://discord.com/api/oauth2/token', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code,
        })

        if token_resp.status_code == 200:
            return token_resp.json()
        else:
            return {'error': 'Token exchange failed', 'details': token_resp.text}, 500
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/static/<path:filename>')
def static_files(filename):
    from flask import send_from_directory
    return send_from_directory('/home/jacob/hackmud/static', filename)

def main():
    # Start screenshot streaming thread
    streamer = threading.Thread(target=screenshot_streamer, daemon=True)
    streamer.start()

    print("Starting hackmud web dashboard...")
    print("Open http://localhost:5000 in your browser")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()
