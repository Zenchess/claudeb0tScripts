"""OpenRouter API client for autonomous bot decision making"""

import json
import time
import os
from typing import Optional, List, Dict, Any
import urllib.request
import urllib.error

from ..state.schemas import Decision, Action, ActionType


class OpenRouterClient:
    """Client for OpenRouter API with conversation context management"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key (or read from OPENROUTER_API_KEY env var)
            model: Model to use (or read from OPENROUTER_MODEL env var)
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY', '')
        self.model = model or os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
        self.api_base = 'https://openrouter.ai/api/v1'

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")

        # Conversation context
        self.conversation_history: List[Dict[str, str]] = []
        self.max_context_turns = 20
        self.last_api_call_time = 0
        self.min_time_between_calls = 1  # Rate limiting (1 call/second)

    def _rate_limit(self) -> None:
        """Apply rate limiting between API calls"""
        now = time.time()
        elapsed = now - self.last_api_call_time
        if elapsed < self.min_time_between_calls:
            time.sleep(self.min_time_between_calls - elapsed)

    def _call_api(self, messages: List[Dict[str, str]], temperature: float = 0.7,
                  max_tokens: int = 4096) -> Optional[Dict[str, Any]]:
        """
        Make API call to OpenRouter.

        Returns:
            Response dict or None on error
        """
        self._rate_limit()

        try:
            data = {
                'model': self.model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }

            request = urllib.request.Request(
                f'{self.api_base}/chat/completions',
                data=json.dumps(data).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Hackmud-Autonomous-Bot/1.0'
                },
                method='POST'
            )

            with urllib.request.urlopen(request, timeout=60) as resp:
                response = json.loads(resp.read().decode('utf-8'))
                self.last_api_call_time = time.time()
                return response

        except urllib.error.HTTPError as e:
            # API error
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                print(f"OpenRouter API error: {error_data}")
            except:
                print(f"OpenRouter HTTP error: {e.code}")
            return None
        except Exception as e:
            print(f"Error calling OpenRouter API: {e}")
            return None

    def decide(self, observations: Dict[str, Any], system_prompt: str = None,
               temperature: float = 0.7, max_tokens: int = 4096) -> Optional[Decision]:
        """
        Get AI decision based on observations.

        Args:
            observations: Current game state and environment
            system_prompt: System prompt to use
            temperature: Sampling temperature (0-1)
            max_tokens: Max tokens in response

        Returns:
            Decision object or None on error
        """
        if not system_prompt:
            system_prompt = self._get_default_system_prompt()

        # Build user prompt from observations
        user_prompt = self._build_user_prompt(observations)

        # Build message list with conversation history
        messages = [{'role': 'system', 'content': system_prompt}]

        # Add recent conversation history
        messages.extend(self.conversation_history[-self.max_context_turns:])

        # Add current turn
        messages.append({'role': 'user', 'content': user_prompt})

        # Call API
        response = self._call_api(messages, temperature, max_tokens)
        if not response:
            return None

        # Extract response text
        try:
            response_text = response['choices'][0]['message']['content']
        except (KeyError, IndexError):
            print(f"Unexpected response format: {response}")
            return None

        # Add to conversation history
        self.conversation_history.append({'role': 'user', 'content': user_prompt})
        self.conversation_history.append({'role': 'assistant', 'content': response_text})

        # Trim history if too long
        if len(self.conversation_history) > self.max_context_turns * 2:
            self.conversation_history = self.conversation_history[-(self.max_context_turns * 2):]

        # Parse decision from response
        decision = self._parse_decision(response_text)
        return decision

    def _build_user_prompt(self, observations: Dict[str, Any]) -> str:
        """Build user prompt from observations"""
        parts = [
            "# Current Situation",
            f"Time: {observations.get('timestamp', 'unknown')}",
            ""
        ]

        # Discord messages
        if observations.get('discord_new_messages'):
            parts.append("## Discord Messages")
            for msg in observations['discord_new_messages'][:5]:  # Last 5 messages
                # Handle both dict and DiscordMessage objects
                username = msg.username if hasattr(msg, 'username') else msg.get('username', 'unknown')
                content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
                parts.append(f"@{username}: {content}")
            parts.append("")

        # Game state
        if 'game_state' in observations:
            gs = observations['game_state']
            parts.append("## Game State")
            # Handle both dict and GameState objects
            balance = gs.balance if hasattr(gs, 'balance') else gs.get('balance', 'unknown')
            location = gs.location if hasattr(gs, 'location') else gs.get('location', 'unknown')
            shell_output = gs.shell_output if hasattr(gs, 'shell_output') else gs.get('shell_output', '')
            parts.append(f"Balance: {balance} GC")
            parts.append(f"Location: {location}")
            if shell_output:
                # Show last few lines of shell
                lines = shell_output.split('\n')[-3:]
                parts.append("Recent Shell Output:")
                for line in lines:
                    if line.strip():
                        parts.append(f"  {line}")
            parts.append("")

        # Active tasks
        if observations.get('active_tasks'):
            parts.append("## Active Tasks")
            for task in observations['active_tasks'][:3]:
                parts.append(f"- {task}")
            parts.append("")

        # Available actions
        parts.append("## Available Actions")
        parts.append("- shell_command: Execute a hackmud script or shell command")
        parts.append("- read_game_state: Read current game state (shell/chat windows)")
        parts.append("- discord_send: Send a message to Discord")
        parts.append("- file_read: Read a file (readonly)")
        parts.append("- file_write: Write a file (requires approval)")
        parts.append("")

        parts.append("## Your Decision")
        parts.append("Based on the current situation, what should I do next?")
        parts.append("Respond with your reasoning and planned actions in JSON format.")
        parts.append("")

        return "\n".join(parts)

    def _parse_decision(self, response: str) -> Decision:
        """Parse AI response into Decision object"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                decision_data = json.loads(json_str)
            else:
                # No JSON found, create default decision from text
                decision_data = {
                    'reasoning': response,
                    'actions': []
                }

            # Extract reasoning
            reasoning = decision_data.get('reasoning', response)

            # Extract actions
            actions = []
            for action_data in decision_data.get('actions', []):
                try:
                    action_type = ActionType[action_data.get('type', 'SHELL_COMMAND').upper()]
                    action = Action(
                        action_type=action_type,
                        parameters=action_data.get('parameters', {}),
                        reasoning=action_data.get('reasoning', ''),
                        priority=action_data.get('priority', 'normal')
                    )
                    actions.append(action)
                except (KeyError, ValueError) as e:
                    print(f"Error parsing action: {e}")
                    continue

            # Create decision
            decision = Decision(
                reasoning=reasoning,
                actions=actions,
                confidence=decision_data.get('confidence', 0.5),
                alternatives=decision_data.get('alternatives', [])
            )

            return decision

        except json.JSONDecodeError:
            # If JSON parsing fails, create basic decision
            return Decision(
                reasoning=response,
                actions=[],
                confidence=0.3
            )
        except Exception as e:
            print(f"Error parsing decision: {e}")
            return Decision(
                reasoning="Error parsing response",
                actions=[],
                confidence=0.0
            )

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []

    def get_context_length(self) -> int:
        """Get approximate context length in tokens"""
        # Rough estimate: 1 token ≈ 4 characters
        total_chars = sum(len(turn['content']) for turn in self.conversation_history)
        return total_chars // 4

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for the bot"""
        return """You are an autonomous agent controlling a player in the hacking simulation game "hackmud".

Your role:
- Monitor Discord for commands from trusted users
- Play the game autonomously to achieve goals
- Make strategic decisions about which scripts to run and what to hack
- Respond helpfully to Discord messages
- Manage resources (GC currency) responsibly

Guidelines:
- Always prioritize safety and never execute commands you're unsure about
- Ask for approval before risky actions
- Report interesting findings to Discord
- Be strategic: analyze game state before taking action
- Track your balance and budget carefully
- Only engage in authorized activities

When planning actions, respond with JSON containing:
{
  "reasoning": "explanation of your decision",
  "confidence": 0.0-1.0,
  "actions": [
    {
      "type": "shell_command|read_game_state|discord_send|file_read|file_write",
      "parameters": {...},
      "reasoning": "why this action",
      "priority": "critical|high|normal|low"
    }
  ],
  "alternatives": ["alternative approaches if available"]
}

Remember: You run on behalf of the player claudeb0t. Be helpful, safe, and fun!"""

    def set_model(self, model: str) -> None:
        """Change the model being used"""
        self.model = model

    def get_model(self) -> str:
        """Get current model"""
        return self.model
