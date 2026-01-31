#!/usr/bin/env python3
"""
Add reactions to recent messages
"""

import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def add_reactions():
    """Add reactions to recent messages"""

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")

        # Get the main channel
        guild = client.guilds[0]
        channel = discord.utils.get(guild.text_channels, id=1456288519403208800)

        if not channel:
            print("Could not find channel")
            await client.close()
            return

        # Get recent messages
        messages = [msg async for msg in channel.history(limit=10)]

        # Add reactions to some messages
        for msg in messages:
            if "do some reactions" in msg.content.lower():
                await msg.add_reaction("✅")
                await msg.add_reaction("👍")
                print(f"Added reactions to: {msg.content[:50]}")
            elif "private channel created" in msg.content.lower():
                await msg.add_reaction("🔒")
                await msg.add_reaction("🎉")
                print(f"Added reactions to: {msg.content[:50]}")
            elif "trusted-only" in msg.content.lower() and msg.author.id == 1081873483300093952:
                await msg.add_reaction("😂")
                print(f"Added reactions to Kaj's message")

        print("✅ Reactions added!")
        await client.close()

    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found")
        return

    await client.start(token)

if __name__ == "__main__":
    asyncio.run(add_reactions())
