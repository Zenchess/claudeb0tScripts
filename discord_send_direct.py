#!/usr/bin/env python3
"""Send a message to Discord directly (one-shot)"""
import discord
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get('DISCORD_BOT_TOKEN')

if len(sys.argv) < 3:
    print("Usage: ./discord_send_direct.py CHANNEL_ID MESSAGE")
    sys.exit(1)

channel_id = int(sys.argv[1])
message = ' '.join(sys.argv[2:])

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    try:
        channel = await client.fetch_channel(channel_id)
        await channel.send(message)
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Error: {e}")
    await client.close()

client.run(token, log_handler=None)
