#!/usr/bin/env python3
"""
Autonomous OpenRouter-powered bot for hackmud
Main entry point and event loop orchestrator
"""

import asyncio
import json
import signal
import sys
import time
import os
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import subprocess

# Add autonomous_bot to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

from autonomous_bot.state.schemas import (
    Action, ActionType, Decision, BotState, GameState, DiscordMessage
)
from autonomous_bot.state.state_manager import StateManager
from autonomous_bot.safety.validator import SafetyValidator
from autonomous_bot.ai.openrouter_client import OpenRouterClient
from autonomous_bot.execution.action_executor import ActionExecutor


class AutonomousAgent:
    """Main autonomous agent orchestrator"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_path = self.project_root / "autonomous_bot" / "config" / "bot_config.json"

        # Load configuration
        self.config = self._load_config()

        # Initialize subsystems
        self.state_manager = StateManager()
        self.safety_validator = SafetyValidator(str(self.config_path))
        self.action_executor = ActionExecutor(str(self.project_root))

        # Load state
        self.state = self.state_manager.load_state()

        # Initialize OpenRouter client
        try:
            import os
            api_key = os.getenv('OPENROUTER_API_KEY')
            model = os.getenv('OPENROUTER_MODEL', self.config.get('openrouter', {}).get('model'))
            self.openrouter = OpenRouterClient(api_key=api_key, model=model)
            print(f"OpenRouter client initialized with model: {self.openrouter.model}")
        except Exception as e:
            print(f"Error initializing OpenRouter: {e}")
            self.openrouter = None

        # Control flags
        self.running = True
        self.paused = False
        self.last_observation_time = 0

        # Stats
        self.start_time = time.time()
        self.iterations = 0

    def _load_config(self) -> dict:
        """Load configuration from JSON"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
            return {
                'openrouter': {},
                'discord': {},
                'game': {},
                'safety': {},
                'behavior': {},
                'monitoring': {}
            }

    async def run(self) -> None:
        """Main autonomous loop"""
        print("🤖 Autonomous Agent Starting...")
        print(f"Model: {self.openrouter.model if self.openrouter else 'NOT LOADED'}")
        print(f"Safe mode: {not self.running}")

        # Set signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

        # Main loop
        while self.running:
            try:
                if self.paused:
                    await asyncio.sleep(5)
                    continue

                # === OBSERVE ===
                observations = await self._gather_observations()

                # === THINK ===
                decision = await self._make_decision(observations)

                if not decision:
                    print("❌ Failed to get decision from OpenRouter")
                    await asyncio.sleep(self.config.get('game', {}).get('poll_interval', 5))
                    continue

                # === VALIDATE ===
                actions_to_execute = []
                for action in decision.actions:
                    validation = self.safety_validator.validate_action(action)

                    if validation.requires_approval:
                        print(f"⏳ Action requires approval: {action.reasoning}")
                        action_id = self.safety_validator.queue_for_approval(action)
                        print(f"   Queued as: {action_id}")
                        continue

                    if validation.allowed:
                        actions_to_execute.append(action)
                    else:
                        print(f"🚫 Action blocked: {validation.reason}")

                # === ACT ===
                for action in actions_to_execute:
                    print(f"▶️  Executing: {action.action_type.value}")
                    result = await self.action_executor.execute(action)

                    # Log action
                    self.state_manager.log_action(action, result)

                    if result.success:
                        print(f"✅ Success: {result.output[:100]}...")
                        self.state.failed_actions = 0
                    else:
                        print(f"❌ Failed: {result.error[:100]}...")
                        self.state.failed_actions += 1

                    # Update state from result
                    self._update_state_from_result(action, result)

                # Check emergency stop conditions
                if self.state.failed_actions >= 5:
                    await self._trigger_emergency_stop("High error rate (5+ failures)")

                # Save state
                self.state.uptime_seconds = time.time() - self.start_time
                self.state.last_heartbeat = time.time()
                self.state_manager.save_state(self.state)

                self.iterations += 1

                # Rate limiting - sleep between cycles
                poll_interval = self.config.get('game', {}).get('poll_interval', 3)
                print(f"⏸️  Sleeping {poll_interval}s until next cycle...")
                await asyncio.sleep(poll_interval)

            except KeyboardInterrupt:
                print("⏸️  Interrupted")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                self.state.failed_actions += 1
                await asyncio.sleep(5)

        # Shutdown
        await self._shutdown()

    async def _gather_observations(self) -> Dict:
        """Observe current game and Discord state"""
        try:
            discord_msgs = await self._poll_discord()
        except:
            discord_msgs = []

        # Check if game is running
        game_running = self._check_game_running()

        observations = {
            'timestamp': datetime.now().isoformat(),
            'discord_messages': discord_msgs,
            'game_running': game_running,
            'task': 'Check Discord for commands' + (' and play the game' if game_running else ' (game is offline)')
        }
        return observations

    def _check_game_running(self) -> bool:
        """Check if hackmud process is running"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'hackmud'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

    async def _read_game_state(self) -> GameState:
        """Read current game state"""
        try:
            result = await self.action_executor.execute(
                Action(
                    action_type=ActionType.READ_GAME_STATE,
                    parameters={'window': 'shell', 'lines': 20}
                )
            )

            if result.success:
                # Update balance if found in output
                import re
                balance_match = re.search(r'(\d+)[KMB]?GC', result.output)
                if balance_match:
                    # Simple parse (would need more sophisticated parsing for full GC)
                    self.state.current_balance = int(balance_match.group(1)) * 1000  # K GC

                return GameState(
                    shell_output=result.output,
                    balance=self.state.current_balance,
                    timestamp=time.time()
                )
        except Exception as e:
            print(f"Error reading game state: {e}")

        return GameState()

    async def _poll_discord(self) -> List[DiscordMessage]:
        """Poll Discord for new messages"""
        try:
            result = subprocess.run(
                [str(self.project_root / 'discord_fetch.sh'), '-n', '5'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            messages = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                # Parse format: [timestamp] Discord_ID/username/displayname -> "message"
                try:
                    import re
                    match = re.match(r'\[(.*?)\]\s+(\d+)/(.*?)/(.*?)\s+->\s+"(.*)"', line)
                    if match:
                        messages.append(DiscordMessage(
                            user_id=int(match.group(2)),
                            username=match.group(3),
                            display_name=match.group(4),
                            content=match.group(5),
                            timestamp=match.group(1)
                        ))
                except:
                    pass

            return messages

        except Exception as e:
            print(f"Error polling Discord: {e}")
            return []

    async def _make_decision(self, observations: Dict) -> Optional[Decision]:
        """Get AI decision from OpenRouter"""
        if not self.openrouter:
            print("❌ OpenRouter not initialized")
            return None

        try:
            decision = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.openrouter.decide(
                    observations,
                    system_prompt=self._get_system_prompt()
                )
            )

            if decision:
                print(f"🧠 Decision: {decision.reasoning[:100]}...")
                print(f"   Actions: {len(decision.actions)}, Confidence: {decision.confidence:.1%}")

            return decision

        except Exception as e:
            print(f"Error getting decision: {e}")
            return None

    def _load_context_files(self) -> str:
        """Load CLAUDE.md and memory file for context"""
        context = ""

        # Load CLAUDE.md (game instructions and mechanics)
        try:
            claude_md_path = self.project_root / "CLAUDE.md"
            if claude_md_path.exists():
                with open(claude_md_path, 'r') as f:
                    content = f.read()
                    # Take first 1500 chars to preserve tokens
                    context += "\n## GAME INSTRUCTIONS (from CLAUDE.md)\n"
                    context += content[:1500] + "...\n"
        except Exception as e:
            print(f"Note: Could not load CLAUDE.md: {e}")

        # Load claude_memory.txt (long-term memory)
        try:
            memory_path = self.project_root / "claude_memory.txt"
            if memory_path.exists():
                with open(memory_path, 'r') as f:
                    content = f.read()
                    # Take last 1000 chars (most recent memory)
                    if len(content) > 1000:
                        context += "\n## RECENT MEMORY\n..." + content[-1000:] + "\n"
                    else:
                        context += "\n## MEMORY\n" + content + "\n"
        except Exception as e:
            print(f"Note: Could not load claude_memory.txt: {e}")

        return context

    def _get_system_prompt(self) -> str:
        """Get system prompt"""
        return """You are Claude, an autonomous agent for hackmud game.

YOUR JOB:
1. Check Discord for messages from zenchess, kaj, dunce
2. Execute commands/tasks they give you
3. Run game scripts and report back to Discord

COMMANDS YOU CAN RUN (via shell_command action):
- python3 send_command.py "sys.specs" (game command)
- ./discord_fetch.sh -n 5 (read Discord)
- ./discord_send.sh 1456288519403208800 "msg" (send Discord)
- python3 auto_hack.py (hack NPCs)
- Any bash/python command in /home/jacob/hackmud/

RESPOND WITH JSON:
{"reasoning": "why", "confidence": 0.8, "actions": [{"type": "shell_command", "parameters": {"command": "cmd here"}}]}

NOW: What should the bot do? Check Discord and respond to any messages."""

    def _update_state_from_result(self, action: Action, result) -> None:
        """Update bot state based on action result"""
        if action.action_type == ActionType.SHELL_COMMAND:
            self.state.total_commands_sent += 1

        if result.success:
            self.state.total_actions_executed += 1
        else:
            self.state.total_errors += 1

    async def _trigger_emergency_stop(self, reason: str) -> None:
        """Trigger emergency stop"""
        print(f"🛑 EMERGENCY STOP: {reason}")
        self.state.emergency_stop = True
        self.state.emergency_stop_reason = reason

        # Try to notify Discord
        try:
            await self.action_executor._discord_send(
                Action(
                    action_type=ActionType.DISCORD_SEND,
                    parameters={
                        'channel_id': self.config.get('discord', {}).get('notification_channel', ''),
                        'message': f"🛑 Emergency stop: {reason}"
                    }
                )
            )
        except:
            pass

        # Save state and stop
        self.state_manager.save_state(self.state)
        self.running = False

    async def _shutdown(self) -> None:
        """Graceful shutdown"""
        print("💤 Shutting down...")

        # Close connections
        self.action_executor.close()

        # Save final state
        self.state.running = False
        self.state.uptime_seconds = time.time() - self.start_time
        self.state_manager.save_state(self.state)

        print(f"✅ Shutdown complete. Uptime: {self.state.uptime_seconds:.0f}s, Iterations: {self.iterations}")

    def _handle_signal(self, sig, frame):
        """Handle SIGTERM/SIGINT"""
        print("\n🔔 Received signal, graceful shutdown...")
        self.running = False


async def main():
    """Main entry point"""
    agent = AutonomousAgent()

    if not agent.openrouter:
        print("❌ Cannot start: OpenRouter not configured")
        print("   Set OPENROUTER_API_KEY environment variable")
        sys.exit(1)

    try:
        await agent.run()
    except KeyboardInterrupt:
        print("\n⏸️  Interrupted")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    # Run async main
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Goodbye!")
