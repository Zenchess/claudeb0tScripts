#!/usr/bin/env python3
"""
Create a #font Discord channel for discussion about fonts and typography
"""

import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def create_font_channel():
    """Create a #font channel for font discussions"""

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
        existing = discord.utils.get(guild.text_channels, name="font")
        if existing:
            print(f"Channel '#font' already exists: {existing.id}")
            await client.close()
            return

        # Create channel with default permissions (everyone can see)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=True, 
                send_messages=True,
                embed_links=True,
                attach_files=True
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True, 
                send_messages=True,
                manage_channels=True,
                manage_messages=True
            )
        }

        channel = await guild.create_text_channel(
            name="font",
            overwrites=overwrites,
            topic="Discussion about fonts, typography, and text rendering - requested by zenchess"
        )

        print(f"✅ Created #font channel: {channel.name} (ID: {channel.id})")

        # Send a welcome message
        await channel.send(
            "🖋️ **#font Channel Created**\n\n"
            "Welcome to the #font channel! This space is for discussion about:\n"
            "• Fonts and typography\n"
            "• Text rendering and display issues\n"
            "• Font recommendations and resources\n"
            "• Character encoding and Unicode topics\n\n"
            "Requested by zenchess. Let the font discussions begin! 🎨"
        )

        await client.close()

    # Get token from environment
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment")
        return

    await client.start(token)

if __name__ == "__main__":
    asyncio.run(create_font_channel())