#!/usr/bin/env python3
import subprocess
import time
import json
import os
from datetime import datetime

def get_last_message_id():
    """Store the last message ID we've seen"""
    try:
        with open('/tmp/last_discord_id.txt', 'r') as f:
            return f.read().strip()
    except:
        return None

def save_last_message_id(message_id):
    """Save the last message ID we've seen"""
    with open('/tmp/last_discord_id.txt', 'w') as f:
        f.write(message_id)

def get_discord_messages(count=10):
    """Fetch recent Discord messages"""
    try:
        result = subprocess.run([
            './discord_venv/bin/python',
            'discord_tools/discord_fetch.py',
            '-n', str(count)
        ], capture_output=True, text=True, cwd='/home/jacob/hackmud')
        
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return None

def parse_messages(output):
    """Parse Discord messages into structured format"""
    messages = []
    if not output:
        return messages
    
    lines = output.strip().split('\n')
    for line in lines:
        if line.startswith('[') and '->' in line:
            try:
                # Parse: [timestamp] user_id/username/displayname -> "message"
                parts = line.split(' ', 3)
                timestamp = parts[0] + ' ' + parts[1]
                user_info = parts[2]
                message_part = parts[3]
                
                # Extract user info
                user_parts = user_info.split('/')
                user_id = user_parts[0]
                username = user_parts[1]
                displayname = user_parts[2]
                
                # Extract message
                message = message_part.split('-> ', 1)[1].strip('"')
                
                messages.append({
                    'timestamp': timestamp,
                    'user_id': user_id,
                    'username': username,
                    'displayname': displayname,
                    'message': message,
                    'raw': line
                })
            except Exception as e:
                print(f"Error parsing line: {line} - {e}")
                continue
    
    return messages

def should_respond_to_message(msg):
    """Check if we should respond to this message"""
    # Don't respond to our own messages
    if msg['username'] == 'opencode' or msg['displayname'] == 'Claude':
        return False

    # Only respond to messages from specific users
    allowed_users = ['kaj', 'zenchess', 'dunce']
    if msg['username'] not in allowed_users:
        return False
    
    # Keywords that might need a response
    response_keywords = [
        'claude', 'opencode', 'hackmud', 'help', 'thanks', 'ty',
        '?', 'what', 'how', 'why', 'when', 'where'
    ]
    
    message_lower = msg['message'].lower()
    return any(keyword in message_lower for keyword in response_keywords)

def generate_response(msg):
    """Generate a response to a message"""
    message_lower = msg['message'].lower()
    displayname = msg['displayname']
    
    # Direct mentions
    if 'claude' in message_lower or 'opencode' in message_lower:
        return f"@{displayname} Yes?"
    
    # Questions
    if '?' in message_lower:
        return f"@{displayname} What do you need help with?"
    
    # Thanks
    if 'thanks' in message_lower or 'ty' in message_lower:
        return f"@{displayname} You're welcome!"
    
    # Hackmud related
    if 'hackmud' in message_lower:
        return f"@{displayname} Are you playing hackmud too?"
    
    # Help requests
    if 'help' in message_lower:
        return f"@{displayname} What do you need help with?"
    
    return None

def send_response(message):
    """Send a response to Discord"""
    try:
        subprocess.run([
            './discord_venv/bin/python',
            'discord_tools/discord_send_api.py',
            '1456288519403208800',
            message
        ], cwd='/home/jacob/hackmud', check=True)
        print(f"Sent response: {message}")
        return True
    except Exception as e:
        print(f"Error sending response: {e}")
        return False

def main():
    """Main monitoring loop"""
    end_time = time.time() + (2 * 60 * 60)  # 2 hours from now
    last_id = get_last_message_id()
    
    print(f"Starting Discord monitoring for 2 hours...")
    print(f"End time: {datetime.fromtimestamp(end_time)}")
    
    while time.time() < end_time:
        try:
            # Get messages
            output = get_discord_messages(15)
            if not output:
                print("No messages fetched")
                time.sleep(15)
                continue
            
            messages = parse_messages(output)
            if not messages:
                print("No messages parsed")
                time.sleep(15)
                continue
            
            # Check for new messages
            new_messages = []
            if last_id:
                # Find messages after our last seen ID
                for msg in messages:
                    if msg['user_id'] == last_id:
                        break
                    new_messages.append(msg)
            else:
                # First run, just get the latest
                if messages:
                    new_messages = [messages[0]]
            
            def execute_command(command):
                """Execute a command safely."""
                print(f"Executing command: {command}")
                # Implement safety checks here to prevent harmful commands
                # Example: Check if the command starts with 'rm -rf'
                if command.startswith('rm -rf'):
                    print("Potentially harmful command detected. Skipping.")
                    return False
            
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd='/home/jacob/hackmud')
                    print(f"Command output: {result.stdout}")
                    print(f"Command error: {result.stderr}")
                    return True
                except Exception as e:
                    print(f"Error executing command: {e}")
                    return False
            
            def main():
                """Main monitoring loop"""
                end_time = time.time() + (2 * 60 * 60)  # 2 hours from now
                last_id = get_last_message_id()
            
                print(f"Starting Discord monitoring for 2 hours...")
                print(f"End time: {datetime.fromtimestamp(end_time)}")
            
                while time.time() < end_time:
                    try:
                        # Get messages
                        output = get_discord_messages(15)
                        if not output:
                            print("No messages fetched")
                            time.sleep(15)
                            continue
            
                        messages = parse_messages(output)
                        if not messages:
                            print("No messages parsed")
                            time.sleep(15)
                            continue
            
                        # Check for new messages
                        new_messages = []
                        if last_id:
                            # Find messages after our last seen ID
                            for msg in messages:
                                if msg['user_id'] == last_id:
                                    break
                                new_messages.append(msg)
                        else:
                            # First run, just get the latest
                            if messages:
                                new_messages = [messages[0]]
            
                        # Process new messages
                        for msg in reversed(new_messages):  # Process in chronological order
                            print(f"New message: {msg['displayname']}: {msg['message']}")
            
                            if should_respond_to_message(msg):
                                response = None
                                if msg['message'].startswith('!'):  # Command prefix
                                    command = msg['message'][1:]  # Remove the prefix
                                    if execute_command(command):
                                        response = f"@{msg['displayname']} Command executed successfully."
                                    else:
                                        response = f"@{msg['displayname']} Command execution failed."
                                else:
                                    response = generate_response(msg)
            
                                if response:
                                    send_response(response)
                                    time.sleep(2)  # Small delay between responses            
            # Update last seen ID
            if messages:
                save_last_message_id(messages[0]['user_id'])
            
            print(f"Checked at {datetime.now().strftime('%H:%M:%S')} - sleeping 15s...")
            time.sleep(15)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            break
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            time.sleep(15)
    
    print("Monitoring completed")

if __name__ == "__main__":
    main()