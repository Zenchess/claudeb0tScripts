#!/usr/bin/env python3
"""
Flask server for hackmud Discord Activity
Serves live terminal data using the Scanner API with Discord OAuth authentication
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory, request, session, redirect, url_for
from flask_cors import CORS
from flask_discord import DiscordOAuth2Session, requires_authorization

# Load environment variables from .env file
load_dotenv()

# Add python_lib to path
sys.path.insert(0, str(Path(__file__).parent / 'python_lib'))
from hackmud.memory import Scanner

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS with credentials

# Discord OAuth Configuration
# You need to create a Discord application at https://discord.com/developers/applications
# and set these environment variables:
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "replace_with_random_secret_key")
app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID", "")  # Your Discord App Client ID
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET", "")  # Your Discord App Secret
app.config["DISCORD_REDIRECT_URI"] = os.getenv("DISCORD_REDIRECT_URI", "https://zenchess.ngrok.app/callback")

# Force HTTPS scheme for OAuth (needed when behind ngrok proxy)
app.config["PREFERRED_URL_SCHEME"] = "https"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Allow OAuth over ngrok tunnel

# Trusted Discord user IDs (zenchess, kaj, dunce)
TRUSTED_USERS = {
    190743971469721600,  # zenchess
    1081873483300093952,  # kaj/isinctorp
    626075347225411584   # dunce
}

# Session-based authentication storage
# Format: {session_id: {'discord_id': int, 'username': str, 'expires': timestamp}}
import random
import string
_active_sessions = {}

def generate_session_code():
    """Generate a unique 6-character session code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in _active_sessions:
            return code

# Initialize Discord OAuth if configured
# Using minimal scope: only 'identify' for user ID and username (no email, no guilds)
discord_oauth = None
if app.config["DISCORD_CLIENT_ID"] and app.config["DISCORD_CLIENT_SECRET"]:
    app.config["DISCORD_OAUTH_SCOPES"] = ["identify"]  # Minimal permissions
    discord_oauth = DiscordOAuth2Session(app)

# Global Scanner instance for persistent connection
_scanner = None

def get_scanner():
    """Get or create Scanner instance"""
    global _scanner
    if _scanner is None:
        _scanner = Scanner()
        _scanner.connect()
    return _scanner

def is_authenticated():
    """Check if user is logged in via Discord OAuth or session auth"""
    # Check OAuth first
    if discord_oauth:
        try:
            if discord_oauth.authorized:
                return True
        except:
            pass

    # Check session auth
    code = session.get('session_code')
    if code and code in _active_sessions:
        session_data = _active_sessions[code]
        if session_data['authenticated'] and time.time() <= session_data['expires']:
            return True

    return False

def is_authorized_user():
    """Check if logged-in user is one of the trusted users (OAuth or session)"""
    # Allow localhost for testing
    if request.remote_addr in ('127.0.0.1', '::1', 'localhost'):
        return True

    # Check OAuth first
    if discord_oauth:
        try:
            if discord_oauth.authorized:
                user = discord_oauth.fetch_user()
                return user.id in TRUSTED_USERS
        except:
            pass

    # Check session auth
    code = session.get('session_code')
    if code and code in _active_sessions:
        session_data = _active_sessions[code]
        if session_data['authenticated'] and time.time() <= session_data['expires']:
            return session_data['discord_id'] in TRUSTED_USERS

    return False

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'hackmud_activity.html')

@app.route('/WhiteRabbitHackmudExtended.ttf')
def font():
    """Serve the WhiteRabbit font"""
    return send_from_directory('.', 'WhiteRabbitHackmudExtended.ttf')

@app.route('/noise.png')
def noise_vfx():
    """Serve the noise VFX image"""
    return send_from_directory('.', 'noise.png')

@app.route('/crtscans.png')
def crtscans_vfx():
    """Serve the CRT scanlines VFX image"""
    return send_from_directory('.', 'crtscans.png')

@app.route('/login')
def login():
    """Discord OAuth login"""
    if not discord_oauth:
        return jsonify({'error': 'Discord OAuth not configured'}), 500
    return discord_oauth.create_session()

@app.route('/callback')
def callback():
    """Discord OAuth callback"""
    if not discord_oauth:
        return jsonify({'error': 'Discord OAuth not configured'}), 500

    try:
        discord_oauth.callback()
        user = discord_oauth.fetch_user()

        # Check if user is authorized
        if user.id not in TRUSTED_USERS:
            session.clear()
            return """
                <h1>Access Denied</h1>
                <p>You are not authorized to access this Discord Activity.</p>
                <p>Only zenchess, kaj, and dunce can access the command interface.</p>
            """, 403

        return redirect(url_for('index'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/session/create', methods=['POST'])
def create_session():
    """Create a new session code for authentication"""
    code = generate_session_code()
    # Store pending session (not yet authenticated)
    _active_sessions[code] = {
        'discord_id': None,
        'username': None,
        'expires': time.time() + 600,  # 10 minute expiry
        'authenticated': False
    }
    # Store session code in Flask session
    session['session_code'] = code
    return jsonify({'session_code': code})

@app.route('/api/session/status')
def session_status():
    """Check if current session is authenticated"""
    code = session.get('session_code')
    if not code or code not in _active_sessions:
        return jsonify({'authenticated': False})

    session_data = _active_sessions[code]

    # Check if expired
    if time.time() > session_data['expires']:
        del _active_sessions[code]
        return jsonify({'authenticated': False})

    if session_data['authenticated']:
        return jsonify({
            'authenticated': True,
            'authorized': session_data['discord_id'] in TRUSTED_USERS,
            'username': session_data['username'],
            'id': session_data['discord_id']
        })

    return jsonify({'authenticated': False, 'pending': True, 'code': code})

@app.route('/api/session/validate', methods=['POST'])
def validate_session():
    """Discord bot endpoint to validate a session code with Discord ID"""
    data = request.json
    code = data.get('code')
    discord_id = data.get('discord_id')
    username = data.get('username')

    if not code or not discord_id:
        return jsonify({'error': 'Missing code or discord_id'}), 400

    if code not in _active_sessions:
        return jsonify({'error': 'Invalid or expired session code'}), 404

    # Check if user is trusted
    if discord_id not in TRUSTED_USERS:
        return jsonify({'error': 'User not authorized'}), 403

    # Authenticate the session
    _active_sessions[code]['discord_id'] = discord_id
    _active_sessions[code]['username'] = username
    _active_sessions[code]['authenticated'] = True
    _active_sessions[code]['expires'] = time.time() + 3600  # Extend to 1 hour

    return jsonify({'success': True, 'message': 'Session authenticated'})

@app.route('/api/user')
def user_info():
    """Get current user info (OAuth or session auth)"""
    if not is_authenticated():
        return jsonify({'authenticated': False})

    # Try OAuth first
    if discord_oauth:
        try:
            if discord_oauth.authorized:
                user = discord_oauth.fetch_user()
                return jsonify({
                    'authenticated': True,
                    'authorized': user.id in TRUSTED_USERS,
                    'username': user.username,
                    'discriminator': user.discriminator,
                    'id': user.id,
                    'auth_method': 'oauth'
                })
        except:
            pass

    # Check session auth
    code = session.get('session_code')
    if code and code in _active_sessions:
        session_data = _active_sessions[code]
        if session_data['authenticated'] and time.time() <= session_data['expires']:
            return jsonify({
                'authenticated': True,
                'authorized': session_data['discord_id'] in TRUSTED_USERS,
                'username': session_data['username'],
                'discriminator': '0000',  # Session auth doesn't have discriminator
                'id': session_data['discord_id'],
                'auth_method': 'session'
            })

    return jsonify({'authenticated': False})

@app.route('/api/terminal')
def terminal_data():
    """
    API endpoint that returns live terminal data from hackmud
    Returns JSON with shell, badge, breach, and chat content

    NEW: Scanner now returns unwrapped lines from Queue<string>
    No unwrapping needed - lines are already natural breaks!
    """
    try:
        scanner = get_scanner()

        # Read from different windows with large history buffers
        # Scanner now reads from Window.output Queue<string> - unwrapped!
        shell_lines = scanner.read_window('shell', lines=500, preserve_colors=True)
        badge_lines = scanner.read_window('badge', lines=10, preserve_colors=True)
        breach_lines = scanner.read_window('breach', lines=10, preserve_colors=True)
        chat_lines = scanner.read_window('chat', lines=300, preserve_colors=True)

        # Simple join - no unwrapping needed!
        shell = '\n'.join(shell_lines)
        badge = '\n'.join(badge_lines)
        breach = '\n'.join(breach_lines)
        chat = '\n'.join(chat_lines)

        # Unescape backslashes (hackmud stores them escaped in memory)
        shell = shell.replace('\\\\', '\\')
        badge = badge.replace('\\\\', '\\')
        breach = breach.replace('\\\\', '\\')
        chat = chat.replace('\\\\', '\\')

        return jsonify({
            'shell': shell,
            'badge': badge,
            'breach': breach,
            'chat': chat
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'shell': f'Error reading shell: {e}',
            'badge': f'Error reading badge: {e}',
            'breach': f'Error reading breach: {e}',
            'chat': f'Error reading chat: {e}'
        }), 500

@app.route('/api/autocomplete')
def autocomplete_data():
    """Return autocomplete data from hackmud settings file"""
    try:
        import json
        settings_path = Path.home() / '.config' / 'hackmud' / 'settings'

        if not settings_path.exists():
            return jsonify({'error': 'Settings file not found'}), 404

        with open(settings_path, 'r') as f:
            settings = json.load(f)

        # Extract autocomplete from settings
        autocomplete_json = settings.get('autocomplete', '{}')
        if isinstance(autocomplete_json, str):
            autocomplete_data = json.loads(autocomplete_json)
        else:
            autocomplete_data = autocomplete_json

        return jsonify(autocomplete_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/command', methods=['POST'])
def execute_command():
    """
    Add hackmud command to FIFO queue (requires authentication and authorization)
    """
    # Check authentication
    if not is_authorized_user():
        return jsonify({'error': 'Unauthorized: You must be logged in as a trusted user'}), 403

    data = request.json
    if not data or 'command' not in data:
        return jsonify({'error': 'Missing command'}), 400

    command = data['command'].strip()
    if not command:
        return jsonify({'error': 'Empty command'}), 400

    # Handle /clear command - send Escape key to clear input line
    if command == '/clear':
        try:
            import subprocess

            # Find hackmud window
            result = subprocess.run(
                ['xdotool', 'search', '--name', 'hackmud'],
                capture_output=True, text=True
            )
            window_id = result.stdout.strip().split('\n')[0]

            if window_id:
                # Send Escape key to clear input
                subprocess.run(['xdotool', 'key', '--window', window_id, 'Escape'])
                return jsonify({'success': True, 'message': 'Input line cleared'})
            else:
                return jsonify({'error': 'Hackmud window not found'}), 500
        except Exception as e:
            return jsonify({'error': f'Failed to clear: {str(e)}'}), 500

    try:
        # Get user info
        user_id = None
        username = None

        # Try to get user info from session
        code = session.get('session_code')
        if code and code in _active_sessions:
            session_data = _active_sessions[code]
            user_id = session_data.get('discord_id')
            username = session_data.get('username')

        # Add command to queue
        from command_queue import CommandQueue
        queue = CommandQueue()
        position = queue.push(command, user_id=user_id, username=username)
        queue_size = queue.size()

        return jsonify({
            'success': True,
            'command': command,
            'position': position,
            'queue_size': queue_size,
            'message': f'Command queued at position {position} ({queue_size} pending)'
        })

    except Exception as e:
        return jsonify({'error': f'Failed to queue command: {str(e)}'}), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        scanner = get_scanner()
        version = scanner.get_version()
        return jsonify({
            'status': 'ok',
            'version': version,
            'connected': True,
            'oauth_configured': discord_oauth is not None
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'connected': False
        }), 500

# =============================================================================
# Script Runner Endpoints
# =============================================================================

@app.route('/api/script', methods=['GET'])
def get_script():
    """Get current script code and status"""
    if not is_authorized_user():
        return jsonify({'error': 'Unauthorized'}), 403

    from script_runner import get_runner
    runner = get_runner()

    return jsonify({
        'code': runner.get_script(),
        'status': runner.get_status()
    })

@app.route('/api/script', methods=['POST'])
def save_script():
    """Save/update script code"""
    if not is_authorized_user():
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.json
    if not data or 'code' not in data:
        return jsonify({'error': 'Missing code'}), 400

    from script_runner import get_runner
    runner = get_runner()
    runner.load_script(data['code'])

    return jsonify({'success': True, 'message': 'Script saved'})

@app.route('/api/script/start', methods=['POST'])
def start_script():
    """Start script execution"""
    if not is_authorized_user():
        return jsonify({'error': 'Unauthorized'}), 403

    from script_runner import get_runner
    runner = get_runner()

    if runner.start():
        return jsonify({'success': True, 'message': 'Script started'})
    else:
        return jsonify({'error': 'Failed to start script', 'status': runner.get_status()}), 400

@app.route('/api/script/stop', methods=['POST'])
def stop_script():
    """Stop script execution"""
    if not is_authorized_user():
        return jsonify({'error': 'Unauthorized'}), 403

    from script_runner import get_runner
    runner = get_runner()
    runner.stop()

    return jsonify({'success': True, 'message': 'Script stop requested'})

@app.route('/api/script/logs', methods=['GET'])
def get_script_logs():
    """Get script logs"""
    if not is_authorized_user():
        return jsonify({'error': 'Unauthorized'}), 403

    from script_runner import get_runner
    runner = get_runner()

    last_n = request.args.get('last', 100, type=int)
    return jsonify({
        'logs': runner.get_logs(last_n),
        'status': runner.get_status()
    })

if __name__ == '__main__':
    print("Starting hackmud Activity Server...")
    print("Visit: http://localhost:5000")

    if not discord_oauth:
        print("\n⚠️  WARNING: Discord OAuth not configured!")
        print("Set DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET environment variables")
        print("Or add them to .env file")

    print("Press Ctrl+C to stop\n")

    # Run on all interfaces so ngrok can access it
    app.run(host='0.0.0.0', port=5000, debug=False)
