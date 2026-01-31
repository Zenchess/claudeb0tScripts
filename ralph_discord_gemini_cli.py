#!/usr/bin/env python3
"""
ralph_discord_gemini_cli.py

A "Ralph loop" agent that uses **gemini-cli** as the brain and your existing
Discord tools as the hands.

Assumptions (based on what Gemini saw in your repo):
- discord_tools/discord_fetch.py    (fetch messages)
- discord_tools/discord_send_api.py (send messages)
- Optional: claude.md in your repo for instructions

What this script does:
1) Fetch latest Discord messages (via your fetch tool)
2) Filter to messages from trusted users (kaj / zenchess / dunce)
3) Build a prompt (includes claude.md if present)
4) Call gemini-cli (subprocess) and ask it to output STRICT JSON replies
5) Send those replies via your send tool
6) Repeat forever (or once)

Safety:
- This script does NOT run arbitrary commands suggested by Gemini.
- It only ever calls:
    - your discord_fetch.py
    - your discord_send_api.py
    - gemini CLI
- It won't delete files or execute shell commands from the model.

Usage:
  python ralph_discord_gemini_cli.py --channel-id 1234567890

Common extras:
  --once                 Run one iteration and exit
  --poll-seconds 8       Poll interval
  --max-messages 25      How many recent messages to fetch
  --trusted kaj zenchess dunce
  --claude-md ./claude.md

Notes:
- You MUST already have your Discord tool scripts working (token in .env, etc.)
- You may need to adjust the fetch/send CLI arguments to match your scripts.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict


HISTORY_FILE_PATH = Path("./conversation_history.json")


class HistoryEntry(TypedDict):
    role: str
    content: str


def load_history() -> List[HistoryEntry]:
    if HISTORY_FILE_PATH.exists():
        try:
            with open(HISTORY_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode {HISTORY_FILE_PATH}. Starting with empty history.", file=sys.stderr)
            return []
    return []


def save_history(history: List[HistoryEntry]) -> None:
    with open(HISTORY_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# ----------------------------
# Config + helpers
# ----------------------------

@dataclass
class Cfg:
    channel_id: str
    gemini_cmd: str
    gemini_model: Optional[str]
    claude_md_path: Path
    trusted: List[str]
    poll_seconds: float
    max_messages: int
    once: bool
    dry_run: bool
    # Paths to your tools
    discord_fetch_py: Path
    discord_send_py: Path
    python_exec: str


def run_cmd(cmd: List[str], timeout: int = 120) -> Tuple[int, str, str]:
    """Run a subprocess, capture stdout/stderr."""
    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    return p.returncode, p.stdout, p.stderr


def read_text_if_exists(p: Path) -> str:
    try:
        if p.exists() and p.is_file():
            return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        pass
    return ""


def normalize_name(s: str) -> str:
    return re.sub(r"\s+", "", s.strip().lower())


# ----------------------------
# Discord tool adapters
# ----------------------------

def fetch_discord_messages(cfg: Cfg) -> List[Dict[str, Any]]:
    """
    Calls your discord_fetch tool and returns a list of messages.
    You may need to adjust the arguments here to match your script.

    Expected output formats supported:
      - JSON list of messages
      - JSON object with key "messages" that is a list
    """
    cmd = [
        cfg.python_exec,
        str(cfg.discord_fetch_py),
        "-c", cfg.channel_id,
        "-n", str(cfg.max_messages),
        "--json",
    ]

    rc, out, err = run_cmd(cmd, timeout=120)
    if rc != 0:
        raise RuntimeError(f"discord_fetch failed rc={rc}\nSTDERR:\n{err}\nSTDOUT:\n{out}")

    out = out.strip()
    if not out:
        return []

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        # If your tool prints logs + JSON, try to extract the last JSON block
        m = re.search(r"(\{.*\}|\[.*\])\s*$", out, flags=re.S)
        if not m:
            raise
        data = json.loads(m.group(1))

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("messages"), list):
        return data["messages"]
    raise RuntimeError("discord_fetch returned unexpected JSON shape")


def send_discord_message(cfg: Cfg, content: str) -> None:
    """
    Calls your discord_send tool to send a message to the channel.
    Adjust args to match your script.
    """
    if cfg.dry_run:
        print(f"[DRY RUN] Would send:\n{content}\n")
        return

    cmd = [
        cfg.python_exec,
        str(cfg.discord_send_py),
        "--channel-id", cfg.channel_id,
        "--content", content,
    ]
    rc, out, err = run_cmd(cmd, timeout=60)
    if rc != 0:
        raise RuntimeError(f"discord_send failed rc={rc}\nSTDERR:\n{err}\nSTDOUT:\n{out}")


# ----------------------------
# Gemini CLI adapter
# ----------------------------

SYSTEM_INSTRUCTIONS = """You are an assistant helping me reply on Discord. Your Discord User ID is {BOT_DISCORD_ID}.

Hard constraints:
- Output MUST be valid JSON only. No extra text.
- Do not propose or request running shell commands.
- You cannot access the filesystem or Discord directly; you only see the messages I provide.
- Keep replies "within reason" and safe. Do NOT delete files or ask to delete files.

Task:
Given recent messages in a Discord channel from trusted users, **ALWAYS reply** to each with a helpful response.
If a reply is needed, draft a helpful reply.

Output JSON schema:
{
  "replies": [
    {
      "in_reply_to_id": "<string>",
      "to": "<author name>",
      "content": "<message to send>"
    }
  ]
}

Rules:
- Only reply to messages from: {TRUSTED_LIST}
- Keep each reply concise unless they asked for detail.
- If nothing needs a reply, output: {"replies":[]}
"""


def call_gemini_cli(cfg: Cfg, prompt: str) -> Dict[str, Any]:
    """
    Invoke gemini-cli and parse JSON.
    """
    cmd = [cfg.gemini_cmd, "-y", "--output-format", "json"]
    if cfg.gemini_model:
        cmd += ["--model", cfg.gemini_model]
    cmd += [prompt]

    rc, out, err = run_cmd(cmd, timeout=600)
    if rc != 0:
        # Surface quota errors, etc.
        raise RuntimeError(f"gemini-cli failed rc={rc}\nSTDERR:\n{err}\nSTDOUT:\n{out}")

    text = out.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise RuntimeError(f"gemini-cli did not return valid JSON.\nOUT:\n{text}\nERR:\n{err}")


# ----------------------------
# Ralph loop core
# ----------------------------

def build_prompt(cfg: Cfg, conversation_history: List[HistoryEntry], new_trusted_content: List[str]) -> str:
    claude_md_content = read_text_if_exists(cfg.claude_md_path)
    trusted_list = ", ".join(cfg.trusted)

    bot_discord_id = "UNKNOWN_BOT_ID" # Default value
    if claude_md_content:
        match = re.search(r"MY_DISCORD_ID:\s*(\d+)", claude_md_content)
        if match:
            bot_discord_id = match.group(1)

    sys_instr = SYSTEM_INSTRUCTIONS.replace("{TRUSTED_LIST}", trusted_list)
    sys_instr = sys_instr.replace("{BOT_DISCORD_ID}", bot_discord_id)
    parts = [sys_instr]

    if claude_md_content:
        parts.append("\n\n---\nclaude.md instructions:\n" + claude_md_content + "\n---\n")

    # Add full conversation history to the prompt
    if conversation_history:
        parts.append("\n--- Past Conversation (for context only) ---")
        for entry in conversation_history:
            parts.append(f"{entry['role'].upper()}: {entry['content']}")
        parts.append("--- End Past Conversation ---")

    # Add the specific new trusted messages that need a reply
    if new_trusted_content:
        parts.append("\n--- New Discord Messages (requiring a reply) ---")
        for content in new_trusted_content:
            parts.append(f"USER: {content}")
        parts.append("--- End New Discord Messages ---")
    else:
        # This case should ideally not be hit if new_trusted_content is used to gate prompt generation
        parts.append("\nNo new trusted messages to address in this turn.")

    parts.append("\nNow produce the JSON output schema exactly for the new messages. Do NOT summarize past conversation.")
    return "\n".join(parts)


def filter_trusted(cfg: Cfg, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    trusted_norm = {normalize_name(x) for x in cfg.trusted}

    out: List[Dict[str, Any]] = []
    for m in messages:
        author_data = m.get("author")
        if not author_data or not isinstance(author_data, dict):
            continue

        author_name = str(author_data.get("global_name") or author_data.get("username") or "")
        if normalize_name(author_name) in trusted_norm:
            out.append(m)
    return out


def extract_replies(model_json: Dict[str, Any]) -> List[Dict[str, str]]:
    replies = model_json.get("replies", [])
    if not isinstance(replies, list):
        return []
    cleaned: List[Dict[str, str]] = []
    for r in replies:
        if not isinstance(r, dict):
            continue
        content = str(r.get("content", "")).strip()
        if not content:
            continue
        cleaned.append({
            "in_reply_to_id": str(r.get("in_reply_to_id", "")).strip(),
            "to": str(r.get("to", "")).strip(),
            "content": content,
        })
    return cleaned


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel-id", required=True, help="Discord channel id to monitor/respond in")
    ap.add_argument("--trusted", nargs="+", default=["kaj", "zenchess", "dunce"], help="Trusted author names")
    ap.add_argument("--claude-md", default="./claude.md", help="Path to claude.md instructions file")
    ap.add_argument("--poll-seconds", type=float, default=10.0)
    ap.add_argument("--max-messages", type=int, default=25)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="Do not send; just print what would be sent")

    ap.add_argument("--gemini-cmd", default=os.environ.get("GEMINI_CMD", "gemini"))
    ap.add_argument("--model", default=None, help="Gemini model name for gemini-cli (e.g., gemini-2.0-flash)")

    ap.add_argument("--discord-fetch", default="./discord_tools/discord_fetch.py")
    ap.add_argument("--discord-send", default="./discord_tools/discord_send_api.py")
    ap.add_argument("--python-exec", default=sys.executable)

    args = ap.parse_args()

    cfg = Cfg(
        channel_id=str(args.channel_id),
        gemini_cmd=str(args.gemini_cmd),
        gemini_model=str(args.model) if args.model else None,
        claude_md_path=Path(args.claude_md),
        trusted=[str(x) for x in args.trusted],
        poll_seconds=float(args.poll_seconds),
        max_messages=int(args.max_messages),
        once=bool(args.once),
        dry_run=bool(args.dry_run),
        discord_fetch_py=Path(args.discord_fetch),
        discord_send_py=Path(args.discord_send),
        python_exec=str(args.python_exec),
    )

    print(f"[ralph] channel_id={cfg.channel_id} trusted={cfg.trusted} model={cfg.gemini_model or '(default)'}")
    print(f"[ralph] fetch={cfg.discord_fetch_py} send={cfg.discord_send_py} claude_md={cfg.claude_md_path}")

def deduplicate_and_append_new_messages(
    conversation_history: List[HistoryEntry],
    trusted_msgs: List[Dict[str, Any]],
    last_seen_id: Optional[str],
) -> Tuple[List[HistoryEntry], List[str], Optional[str]]:
    """
    Identifies truly new messages from trusted_msgs, appends them to conversation_history,
    and returns content for the prompt and the updated last_seen_id.
    """
    new_messages_for_prompt: List[str] = []
    current_newest_id_in_batch: Optional[str] = last_seen_id

    # Sort trusted_msgs by ID to ensure we process them in chronological order
    # (assuming Discord message IDs are monotonically increasing)
    sorted_trusted_msgs = sorted(trusted_msgs, key=lambda m: int(m.get("id") or m.get("message_id") or "0"))

    for m in sorted_trusted_msgs:
        msg_id = str((m.get("id") or m.get("message_id") or "")).strip()
        if not msg_id:
            continue

        # Only consider messages STRICTLY newer than last_seen_id
        if last_seen_id is None or int(msg_id) > int(last_seen_id):
            content = str(m.get("content") or m.get("text") or "")
            if content.strip():
                conversation_history.append({"role": "user", "content": content})
                new_messages_for_prompt.append(content)
        
        # Always track the absolute newest ID seen in this batch, regardless of whether it's "new" for prompt
        if current_newest_id_in_batch is None or int(msg_id) > int(current_newest_id_in_batch):
            current_newest_id_in_batch = msg_id

    return conversation_history, new_messages_for_prompt, current_newest_id_in_batch


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel-id", required=True, help="Discord channel id to monitor/respond in")
    ap.add_argument("--trusted", nargs="+", default=["kaj", "zenchess", "dunce"], help="Trusted author names")
    ap.add_argument("--claude-md", default="./claude.md", help="Path to claude.md instructions file")
    ap.add_argument("--poll-seconds", type=float, default=10.0)
    ap.add_argument("--max-messages", type=int, default=25)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="Do not send; just print what would be sent")

    ap.add_argument("--gemini-cmd", default=os.environ.get("GEMINI_CMD", "gemini"))
    ap.add_argument("--model", default=None, help="Gemini model name for gemini-cli (e.g., gemini-2.0-flash)")

    ap.add_argument("--discord-fetch", default="./discord_tools/discord_fetch.py")
    ap.add_argument("--discord-send", default="./discord_tools/discord_send_api.py")
    ap.add_argument("--python-exec", default=sys.executable)

    args = ap.parse_args()

    cfg = Cfg(
        channel_id=str(args.channel_id),
        gemini_cmd=str(args.gemini_cmd),
        gemini_model=str(args.model) if args.model else None,
        claude_md_path=Path(args.claude_md),
        trusted=[str(x) for x in args.trusted],
        poll_seconds=float(args.poll_seconds),
        max_messages=int(args.max_messages),
        once=bool(args.once),
        dry_run=bool(args.dry_run),
        discord_fetch_py=Path(args.discord_fetch),
        discord_send_py=Path(args.discord_send),
        python_exec=str(args.python_exec),
    )

    print(f"[ralph] channel_id={cfg.channel_id} trusted={cfg.trusted} model={cfg.gemini_model or '(default)'}")
    print(f"[ralph] fetch={cfg.discord_fetch_py} send={cfg.discord_send_py} claude_md={cfg.claude_md_path}")

    # Load conversation history
    conversation_history: List[HistoryEntry] = load_history()
    print(f"[ralph] Loaded {len(conversation_history)} history entries.")

    # Initialize last_seen_id from the newest message ID found in the loaded history
    last_seen_id: Optional[str] = None
    if conversation_history:
        # Assuming Discord message IDs are monotonically increasing, we can find the max ID
        # This requires storing message IDs in HistoryEntry, which we don't do.
        # For now, we will simply not pre-initialize last_seen_id from history,
        # but instead let current_newest_id_in_batch track it across fetches.
        # A more robust solution would store msg_id in HistoryEntry.
        # For the current purpose, last_seen_id is dynamically updated by the script's loop.
        pass # No change needed here for now, last_seen_id remains None initially.

    while True:
        try:
            msgs = fetch_discord_messages(cfg)
            trusted_msgs = filter_trusted(cfg, msgs)

            conversation_history, new_trusted_content_for_prompt, current_newest_id_in_batch_fetched = \
                deduplicate_and_append_new_messages(conversation_history, trusted_msgs, last_seen_id)
            
            # Unconditionally update last_seen_id to the newest message ID seen in this batch
            # This ensures we don't re-process older messages on subsequent fetches.
            if current_newest_id_in_batch_fetched is not None:
                last_seen_id = current_newest_id_in_batch_fetched

            if not new_trusted_content_for_prompt:
                if cfg.once:
                    print("[ralph] no new trusted messages to process; exiting (--once).")
                    return
                time.sleep(cfg.poll_seconds)
                continue

            prompt = build_prompt(cfg, conversation_history, new_trusted_content_for_prompt)
            model_json = call_gemini_cli(cfg, prompt)
            
            replies = extract_replies(model_json)

            if not replies:
                print("[ralph] model returned no replies.")
            else:
                for r in replies:
                    content = r["content"]
                    print(f"[ralph] sending reply to {r.get('to','')} (in_reply_to_id={r.get('in_reply_to_id','')}):\n{content}\n---")
                    send_discord_message(cfg, content)
                    # Add bot's reply to history
                    if content.strip():
                        conversation_history.append({"role": "assistant", "content": content})
                # last_seen_id is already updated unconditionally above.
            
            # Trim history to prevent it from growing too large
            conversation_history = trim_history(conversation_history, max_len=cfg.max_messages * 2) # Example: keep 2x max_messages

            # Save history after each iteration
            save_history(conversation_history)

            if cfg.once:
                print("[ralph] done (--once).")
                return

        except subprocess.TimeoutExpired as e:
            print(f"[ralph] timeout: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[ralph] error: {e}", file=sys.stderr)

        time.sleep(cfg.poll_seconds)


def trim_history(history: List[HistoryEntry], max_len: int) -> List[HistoryEntry]:
    """Trims the conversation history to max_len, keeping the most recent entries."""
    if len(history) > max_len:
        print(f"[ralph] Trimming history from {len(history)} to {max_len} entries.", file=sys.stderr)
        return history[-max_len:]
    return history


if __name__ == "__main__":
    main()
