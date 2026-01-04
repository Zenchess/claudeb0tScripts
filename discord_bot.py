#!/usr/bin/env python3
"""
Discord bot for Claude to communicate with Discord servers.
Usage:
    ./discord_venv/bin/python discord_bot.py --token YOUR_TOKEN

Or set DISCORD_BOT_TOKEN environment variable.
"""

import discord
import asyncio
import argparse
import os
import json
import aiohttp
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# File to store messages for Claude to read
INBOX_FILE = "discord_inbox.json"
OUTBOX_FILE = "discord_outbox.json"
IMAGES_DIR = "discord_images"

# Ensure images directory exists
Path(IMAGES_DIR).mkdir(exist_ok=True)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Required for profile lookups

client = discord.Client(intents=intents)

# Store channel references
channels = {}

def load_inbox():
    if os.path.exists(INBOX_FILE):
        with open(INBOX_FILE, 'r') as f:
            return json.load(f)
    return []

def save_inbox(messages):
    with open(INBOX_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

def load_outbox():
    if os.path.exists(OUTBOX_FILE):
        with open(OUTBOX_FILE, 'r') as f:
            return json.load(f)
    return []

def clear_outbox():
    with open(OUTBOX_FILE, 'w') as f:
        json.dump([], f)

@client.event
async def on_ready():
    print(f'Bot connected as {client.user}')
    print(f'Bot is in {len(client.guilds)} server(s):')
    for guild in client.guilds:
        print(f'  - {guild.name} (id: {guild.id})')
        for channel in guild.text_channels:
            channels[f"{guild.name}#{channel.name}"] = channel
            print(f'    - #{channel.name} (id: {channel.id})')
    print("\nBot is ready! Listening for messages...")
    print("Messages will be saved to discord_inbox.json")
    print("To send messages, write to discord_outbox.json and the bot will send them")

    # Start outbox checking loop
    client.loop.create_task(check_outbox())

async def download_attachment(attachment, message_id):
    """Download an attachment and save it locally"""
    try:
        # Create filename with message_id for uniqueness
        ext = Path(attachment.filename).suffix or '.png'
        filename = f"{message_id}_{attachment.id}{ext}"
        filepath = Path(IMAGES_DIR) / filename

        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status == 200:
                    with open(filepath, 'wb') as f:
                        f.write(await resp.read())
                    return str(filepath.absolute())
    except Exception as e:
        print(f"Failed to download attachment: {e}")
    return None

@client.event
async def on_message(message):
    # Don't respond to ourselves
    if message.author == client.user:
        return

    # Download any attachments (images, files)
    downloaded_images = []
    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']):
            path = await download_attachment(attachment, message.id)
            if path:
                downloaded_images.append(path)
                print(f"  Downloaded image: {path}")

    # Save message to inbox
    inbox = load_inbox()
    msg_data = {
        "timestamp": datetime.now().isoformat(),
        "server": message.guild.name if message.guild else "DM",
        "channel": message.channel.name if hasattr(message.channel, 'name') else "DM",
        "channel_id": message.channel.id,
        "author": message.author.display_name,  # Show display name/nickname instead of username
        "author_id": message.author.id,
        "content": message.content,
        "message_id": message.id
    }
    if downloaded_images:
        msg_data["images"] = downloaded_images
    inbox.append(msg_data)
    # Keep only last 100 messages
    inbox = inbox[-100:]
    save_inbox(inbox)

    img_note = f" [+{len(downloaded_images)} images]" if downloaded_images else ""
    print(f"[{message.guild.name if message.guild else 'DM'}#{message.channel.name if hasattr(message.channel, 'name') else 'DM'}] {message.author.display_name}: {message.content}{img_note}")

async def check_outbox():
    """Check outbox file for messages to send or profile requests"""
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            outbox = load_outbox()
            if outbox:
                for msg in outbox:
                    msg_type = msg.get('type', 'message')

                    if msg_type == 'profile':
                        # Handle profile lookup request
                        user_id = msg.get('user_id')
                        username = msg.get('username')
                        guild_id = msg.get('guild_id')

                        try:
                            user = None
                            member = None

                            if user_id:
                                user = await client.fetch_user(int(user_id))
                            elif username and guild_id:
                                guild = client.get_guild(int(guild_id))
                                if guild:
                                    # Search by display name
                                    for m in guild.members:
                                        if username.lower() in m.display_name.lower() or username.lower() in m.name.lower():
                                            member = m
                                            user = m
                                            break

                            if user:
                                profile_data = {
                                    "timestamp": datetime.now().isoformat(),
                                    "type": "profile_response",
                                    "user_id": user.id,
                                    "username": user.name,
                                    "display_name": user.display_name,
                                    "created_at": user.created_at.isoformat() if user.created_at else None,
                                    "avatar_url": str(user.display_avatar.url) if user.display_avatar else None,
                                    "bot": user.bot
                                }
                                # Add member-specific info if available
                                if member:
                                    profile_data["nickname"] = member.nick
                                    profile_data["roles"] = [role.name for role in member.roles if role.name != "@everyone"]
                                    profile_data["joined_at"] = member.joined_at.isoformat() if member.joined_at else None

                                inbox = load_inbox()
                                inbox.append(profile_data)
                                inbox = inbox[-100:]
                                save_inbox(inbox)
                                print(f"Profile lookup: {user.display_name}")
                            else:
                                print(f"User not found: {user_id or username}")
                        except Exception as e:
                            print(f"Profile lookup error: {e}")
                    else:
                        # Regular message sending
                        channel_id = msg.get('channel_id')
                        content = msg.get('content', '')

                        if channel_id and content:
                            try:
                                # Use fetch_channel instead of get_channel for reliability
                                channel = client.get_channel(int(channel_id))
                                if not channel:
                                    channel = await client.fetch_channel(int(channel_id))
                                if channel:
                                    await channel.send(content)
                                    print(f"Sent to #{channel.name}: {content}")
                                else:
                                    print(f"Channel {channel_id} not found")
                            except Exception as e:
                                print(f"Error sending to channel {channel_id}: {e}")

                clear_outbox()
        except Exception as e:
            print(f"Outbox error: {e}")

        await asyncio.sleep(2)  # Check every 2 seconds

def main():
    parser = argparse.ArgumentParser(description='Discord bot for Claude')
    parser.add_argument('--token', help='Discord bot token')
    args = parser.parse_args()

    token = args.token or os.environ.get('DISCORD_BOT_TOKEN')

    if not token:
        print("Error: No token provided!")
        print("Use --token YOUR_TOKEN or set DISCORD_BOT_TOKEN environment variable")
        return

    # Initialize empty files
    if not os.path.exists(INBOX_FILE):
        save_inbox([])
    if not os.path.exists(OUTBOX_FILE):
        clear_outbox()

    print("Starting Discord bot...")
    client.run(token)

if __name__ == '__main__':
    main()
