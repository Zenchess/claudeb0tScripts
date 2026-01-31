#!/usr/bin/env python3
"""
Check actual bot permissions on the Discord server
"""

import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_permissions():
    """Check what permissions the bot actually has"""

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")

        guild = client.guilds[0]
        bot_member = guild.me

        print(f"\nBot permissions in {guild.name}:")
        print("=" * 60)

        perms = bot_member.guild_permissions

        # Check all relevant permissions
        perm_checks = [
            ("Administrator", perms.administrator),
            ("Manage Server", perms.manage_guild),
            ("Manage Roles", perms.manage_roles),
            ("Manage Channels", perms.manage_channels),
            ("Kick Members", perms.kick_members),
            ("Ban Members", perms.ban_members),
            ("Manage Messages", perms.manage_messages),
            ("Manage Webhooks", perms.manage_webhooks),
            ("Manage Emojis", perms.manage_emojis_and_stickers),
            ("View Channels", perms.view_channel),
            ("Send Messages", perms.send_messages),
            ("Send TTS Messages", perms.send_tts_messages),
            ("Embed Links", perms.embed_links),
            ("Attach Files", perms.attach_files),
            ("Read Message History", perms.read_message_history),
            ("Mention Everyone", perms.mention_everyone),
            ("Use External Emojis", perms.use_external_emojis),
            ("Add Reactions", perms.add_reactions),
        ]

        for name, has_perm in perm_checks:
            status = "✅" if has_perm else "❌"
            print(f"{status} {name}")

        print("=" * 60)

        await client.close()

    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found")
        return

    await client.start(token)

if __name__ == "__main__":
    asyncio.run(check_permissions())
