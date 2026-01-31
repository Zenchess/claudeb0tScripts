#!/usr/bin/env python3
"""
Hackmud Discord Bot - Autonomous agent that uses tools to interact with Discord
The agent decides what to do and uses tools to check Discord and send messages
"""

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime
import requests

# Load .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()


class AgenticBot:
    def __init__(self):
        self.api_base = os.getenv('AGENTIC_API_BASE', 'http://localhost:8000')
        self.project_root = Path(__file__).parent
        self.session_id = None
        self.last_api_call = 0
        self.discord_channel_id = '1456288519403208800'  # hackmud-updates channel

        # Load context
        self.claude_md = self._load_file('CLAUDE.md')
        self.memory = self._load_file('claude_memory.txt')

        print(f"🤖 Bot starting - Agentic API at {self.api_base}")
        print(f"📝 Loaded CLAUDE.md ({len(self.claude_md)} chars)")
        print(f"📝 Loaded claude_memory.txt ({len(self.memory)} chars)")

    def _load_file(self, filename: str) -> str:
        """Load a file from project root"""
        try:
            path = self.project_root / filename
            if path.exists():
                with open(path, 'r') as f:
                    return f.read()
        except Exception as e:
            print(f"⚠️  Could not load {filename}: {e}")
        return ""

    def _make_api_call(self, payload: dict) -> dict:
        """Make blocking API call (will be run in executor)"""
        try:
            response = requests.post(
                f"{self.api_base}/api/chat",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"❌ API error: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except Exception as e:
            print(f"❌ API error: {e}")
            return None

    async def call_agent(self) -> dict:
        """Call Agentic WebUI API - agent decides what to do with tools"""
        print("🔄 Calling agent...")
        # Rate limit
        elapsed = time.time() - self.last_api_call
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)

        print("📝 Building agent prompt")
        # Agent prompt with context about available scripts
        message = f"""You are Claude, an autonomous Discord bot for hackmud.

TRUSTED USERS (can give you orders):
- zenchess (Jacob, the main boss)
- kaj/isinctorp (trusted collaborator)
- dunce (trusted collaborator)

AVAILABLE SCRIPTS:
- python3 discord_tools/discord_fetch.py -n 10  → Fetch recent Discord messages
- python3 discord_tools/discord_send_api.py <channel_id> "<message>"  → Send Discord message

CHANNEL IDs:
- hackmud-updates: 1456288519403208800

YOUR MISSION:
1. Use a shell/bash tool to run: python3 discord_tools/discord_fetch.py -n 10
2. Parse the output and look for messages from trusted users
3. If messages from trusted users exist, respond using: python3 discord_tools/discord_send_api.py 1456288519403208800 "<your response>"
4. Be helpful, friendly, concise
5. Only respond to trusted users

START: Check Discord messages and respond to any trusted users."""

        payload = {
            "message": message,
            "session_id": self.session_id,
            "enable_tools": True,
            "tool_choice": "auto"
        }

        try:
            print(f"🚀 Making API call (session: {self.session_id})")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._make_api_call, payload)

            if result:
                self.last_api_call = time.time()
                if 'session_id' in result:
                    self.session_id = result['session_id']
                print(f"✅ API response received")

            return result
        except Exception as e:
            print(f"❌ Error calling API: {e}")
            return None

    async def run(self):
        """Main bot loop - just call the agent repeatedly"""
        print("🤖 Bot running (Ctrl+C to stop)")
        print("📌 Agent will use tools to check Discord and respond autonomously")

        try:
            while True:
                print(f"\n⏱️  [{datetime.now().strftime('%H:%M:%S')}] Starting agent cycle...")

                # Call agent - it decides what tools to use
                response = await self.call_agent()

                if not response:
                    print("⏸️  API error, waiting 15s...")
                    await asyncio.sleep(15)
                    continue

                # Log what happened
                try:
                    content = response.get('response', '')
                    tool_calls = response.get('tool_calls', [])

                    if content:
                        print(f"💬 Agent response: {content[:150]}")

                    if tool_calls:
                        print(f"🔧 Agent used {len(tool_calls)} tool(s):")
                        for tc in tool_calls:
                            print(f"   - {tc.get('name', 'unknown')}")
                    else:
                        print("⏸️  Agent decided not to take action")

                except Exception as e:
                    print(f"❌ Error parsing response: {e}")

                # Sleep before next cycle
                print("⏸️  Waiting 15 seconds for next cycle...")
                await asyncio.sleep(15)

        except KeyboardInterrupt:
            print("\n👋 Bot stopped!")


async def main():
    try:
        bot = AgenticBot()
        await bot.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    asyncio.run(main())
