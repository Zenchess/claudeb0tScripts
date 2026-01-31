#!/usr/bin/env python3
"""
Create #psi-nabby channel with dunce excluded
Requested by psinabby on 2026-01-19T23:29:43
"""

import discord
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/home/jacob/hackmud/.env')

# Discord bot token
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', '142990364433334272'))  # Default to Claudeb0t server

# Specific channel IDs for role/permission management
PSI_NABBY_USER_ID = 1355702736800448723  # psinabby's Discord user ID
DUNCE_USER_ID = 626075347225411584      # dunce's Discord user ID
ZENCHESS_USER_ID = 190743971469721600   # zenchess's Discord user ID

intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")
    
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print(f"Guild {GUILD_ID} not found")
        await client.close()
        return
    
    print(f"Working in guild: {guild.name}")
    
    # Create the #psi-nabby channel
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            read_messages=False,  # Deny access to everyone by default
            send_messages=False,
            read_message_history=False
        ),
        guild.me: discord.PermissionOverwrite(  # Bot permissions
            read_messages=True,
            send_messages=True,
            manage_channels=True,
            read_message_history=True
        )
    }
    
    try:
        # Create the channel
        channel = await guild.create_text_channel(
            name="psi-nabby",
            topic="Private channel for psinabby - dunce excluded per request",
            overwrites=overwrites,
            reason="Requested by psinabby with dunce excluded"
        )
        
        print(f"✅ #psi-nabby channel created successfully! Channel ID: {channel.id}")
        
        # Get the member objects
        psinabby_member = guild.get_member(PSI_NABBY_USER_ID)
        dunce_member = guild.get_member(DUNCE_USER_ID)
        zenchess_member = guild.get_member(ZENCHESS_USER_ID)
        
        # Grant psinabby access
        if psinabby_member:
            await channel.set_permissions(
                psinabby_member,
                read_messages=True,
                send_messages=True,
                read_message_history=True,
                reason="Grant psinabby access to their own channel"
            )
            print(f"✅ Granted access to psinabby")
        else:
            print("⚠️ Could not find psinabby member in guild")
        
        # Grant zenchess access (he's the server owner/operator)
        if zenchess_member:
            await channel.set_permissions(
                zenchess_member,
                read_messages=True,
                send_messages=True,
                read_message_history=True,
                reason="Grant zenchess access (server operator)"
            )
            print(f"✅ Granted access to zenchess")
        else:
            print("⚠️ Could not find zenchess member in guild")
        
        # Explicitly deny dunce access (redundant since @everyone is denied, but explicit)
        if dunce_member:
            await channel.set_permissions(
                dunce_member,
                read_messages=False,
                send_messages=False,
                read_message_history=False,
                reason="Explicitly deny dunce access as requested"
            )
            print(f"✅ Explicitly denied access to dunce")
        else:
            print("⚠️ Could not find dunce member in guild")
        
        # Send welcome message
        await channel.send(
            f"**#psi-nabby channel created!** 🎉\n\n"
            f"This is a private channel requested by <@{PSI_NABBY_USER_ID}>.\n"
            f"<@{DUNCE_USER_ID}> has been explicitly excluded from accessing this channel.\n\n"
            f"Channel permissions:\n"
            f"✅ <@{PSI_NABBY_USER_ID}> - Full access\n"
            f"✅ <@{ZENCHESS_USER_ID}> - Full access (server operator)\n"
            f"❌ <@{DUNCE_USER_ID}> - No access (explicitly excluded)"
        )
        
        print(f"📝 Sent welcome message to #psi-nabby")
        
        # Report to general channel
        general_channel = client.get_channel(1456288519403208800)  # #general
        if general_channel:
            await general_channel.send(
                f"✅ **#psi-nabby channel created successfully!**\n\n"
                f"Channel ID: {channel.id}\n"
                f"Created by request of <@{PSI_NABBY_USER_ID}> with <@{DUNCE_USER_ID}> excluded from access.\n\n"
                f"Access granted to: <@{PSI_NABBY_USER_ID}> and <@{ZENCHESS_USER_ID}>"
            )
            print(f"📢 Reported creation to #general channel")
        
    except discord.Forbidden as e:
        print(f"❌ Permission denied: {e}")
        print("Make sure the bot has 'Manage Channels' permission")
    except Exception as e:
        print(f"❌ Error creating channel: {e}")
    
    await client.close()

if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN not found in environment variables")
        exit(1)
    
    print("Creating #psi-nabby channel with dunce excluded...")
    client.run(TOKEN)