#!/usr/bin/env python3
"""
Create a private Discord channel accessible only to zenchess, kaj, and dunce
"""

import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Trusted users
ZENCHESS_ID = 190743971469721600
KAJ_ID = 1081873483300093952
DUNCE_ID = 626075347225411584

async def create_private_channel():
    """Create a private channel for trusted users only"""

    # Set up intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")

        # Get the guild (server) - assuming bot is only in one server
        guild = client.guilds[0]
        print(f"Guild: {guild.name}")

        # Check if channel already exists
        existing = discord.utils.get(guild.channels, name="trusted-only")
        if existing:
            print(f"Channel 'trusted-only' already exists: {existing.id}")
            await client.close()
            return

        # Get member objects
        zenchess = guild.get_member(ZENCHESS_ID)
        kaj = guild.get_member(KAJ_ID)
        dunce = guild.get_member(DUNCE_ID)

        if not all([zenchess, kaj, dunce]):
            print("Error: Could not find all members")
            print(f"Zenchess: {zenchess}")
            print(f"Kaj: {kaj}")
            print(f"Dunce: {dunce}")
            await client.close()
            return

        # Create channel with specific permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            zenchess: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            kaj: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            dunce: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name="trusted-only",
            overwrites=overwrites,
            topic="Private channel for zenchess, kaj, and dunce"
        )

        print(f"✅ Created private channel: {channel.name} (ID: {channel.id})")

        # Send a welcome message
        await channel.send(
            "🔒 **Private Channel Created**\n\n"
            "This channel is only visible to zenchess, kaj, and dunce.\n"
            "No lurkers allowed!"
        )

        await client.close()

    # Get token from environment
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment")
        return

    await client.start(token)

if __name__ == "__main__":
    asyncio.run(create_private_channel())
