#!/usr/bin/env python3
import subprocess
import time
import sys
from datetime import datetime

def get_latest_messages():
    """Get the latest messages from Discord"""
    try:
        result = subprocess.run([
            './discord_venv/bin/python',
            'discord_tools/discord_fetch.py',
            '-n', '10'
        ], capture_output=True, text=True, cwd='/home/jacob/hackmud')
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # Filter out empty lines and headers
            messages = [line.strip() for line in lines if line.strip() and line.startswith('[')]
            return messages
        else:
            return []
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []

def is_our_message(message):
    """Check if a message is from us (claudeb0t)"""
    return 'claudeb0t/claudeb0t' in message

def extract_message_content(message):
    """Extract the content from a Discord message line"""
    try:
        # Format: [timestamp] user_id/username/displayname -> "message"
        if '->' in message:
            content_part = message.split('->', 1)[1].strip()
            if content_part.startswith('"') and content_part.endswith('"'):
                return content_part[1:-1]  # Remove quotes
        return ""
    except:
        return ""

def extract_display_name(message):
    """Extract display name from message"""
    try:
        # Format: [timestamp] user_id/username/displayname -> "message"
        user_part = message.split('->', 1)[0].strip()
        parts = user_part.split('/')
        if len(parts) >= 3:
            return parts[2]
    except:
        pass
    return "Unknown"

def should_respond(message_content):
    """Check if we should respond to this message"""
    content_lower = message_content.lower()
    
    # Don't respond to very short messages
    if len(message_content.strip()) < 3:
        return False
    
    # Keywords that trigger responses
    response_triggers = [
        'claude', 'opencode', 'hackmud', 'help', 'thanks', 'ty',
        '?', 'what', 'how', 'why', 'when', 'where', 'can you',
        'could you', 'would you', 'monitoring', 'there'
    ]
    
    return any(trigger in content_lower for trigger in response_triggers)

def generate_response(message_content, display_name):
    """Generate an appropriate response"""
    content_lower = message_content.lower()
    
    # Direct mentions of Claude
    if 'claude' in content_lower or 'opencode' in content_lower:
        return f"@{display_name} Yes?"
    
    # Questions
    if '?' in content_lower:
        if 'what' in content_lower or 'how' in content_lower:
            return f"@{display_name} What do you need help with?"
        elif 'why' in content_lower:
            return f"@{display_name} Why what?"
        else:
            return f"@{display_name} I can help with that!"
    
    # Thanks/ty
    if 'thanks' in content_lower or 'ty' in content_lower or 'thank you' in content_lower:
        return f"@{display_name} You're welcome!"
    
    # Help requests
    if 'help' in content_lower:
        return f"@{display_name} What do you need help with?"
    
    # Hackmud related
    if 'hackmud' in content_lower:
        return f"@{display_name} Are you playing hackmud too?"
    
    # Monitoring related
    if 'monitoring' in content_lower:
        return f"@{display_name} Yes, I'm keeping an eye on Discord while working on hackmud stuff!"
    
    # Generic response
    if any(word in content_lower for word in ['hi', 'hello', 'hey', 'yo']):
        return f"@{display_name} Hey there!"
    
    return None

def send_response(response):
    """Send a response to Discord"""
    try:
        subprocess.run([
            './discord_venv/bin/python',
            'discord_tools/discord_send_api.py',
            '1456288519403208800',
            response
        ], cwd='/home/jacob/hackmud', check=True)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent: {response}")
        return True
    except Exception as e:
        print(f"Error sending response: {e}")
        return False

def main():
    """Main monitoring loop"""
    if len(sys.argv) > 1:
        duration = int(sys.argv[1]) * 60  # Convert minutes to seconds
    else:
        duration = 120  # Default 2 minutes for testing
    
    end_time = time.time() + duration
    last_messages = []
    
    print(f"Starting Discord monitoring for {duration//60} minutes")
    print(f"End time: {datetime.fromtimestamp(end_time).strftime('%H:%M:%S')}")
    
    while time.time() < end_time:
        try:
            current_messages = get_latest_messages()
            
            if current_messages != last_messages:
                # Find new messages (messages that weren't in our last batch)
                new_messages = []
                for msg in current_messages:
                    if msg not in last_messages and not is_our_message(msg):
                        new_messages.append(msg)
                
                # Process new messages in chronological order
                for msg in reversed(new_messages):
                    content = extract_message_content(msg)
                    display_name = extract_display_name(msg)
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] New from {display_name}: {content}")
                    
                    if should_respond(content):
                        response = generate_response(content, display_name)
                        if response:
                            send_response(response)
                            time.sleep(2)  # Brief pause between responses
                
                last_messages = current_messages
            
            # Show status every 10 minutes
            if int(time.time()) % 600 < 15:
                remaining = int((end_time - time.time()) // 60)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring... {remaining} minutes remaining")
            
            time.sleep(15)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            break
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            time.sleep(15)
    
    print(f"Monitoring completed at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()