#!/usr/bin/env python3
"""
gemini_ralph_loop.py

A "Ralph loop" style wrapper around the *interactive* `gemini` CLI using pexpect:
- Runs gemini in a loop until it produces a recognizable DONE marker (or hits max iters)
- Auto-answers common approval prompts ("y"/"yes")
- Captures logs to a file
- Feeds back a short "state" summary each iteration (optional)

Install:
  pip install pexpect

Usage examples:
  python3 gemini_ralph_loop.py --prompt "Analyze server.log and propose fixes. End with: DONE"
  python3 gemini_ralph_loop.py --prompt-file task.txt --max-iters 6

Tip:
  In your prompt, ask Gemini to end with a literal marker like:
    "When you're finished, output exactly: DONE"
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import pexpect


DONE_REGEX_DEFAULT = r"(?m)^\s*DONE\s*$"


@dataclass
class LoopConfig:
    gemini_cmd: str
    model_args: list[str]
    max_iters: int
    timeout_s: int
    done_regex: re.Pattern
    log_path: Path
    auto_approve: bool
    approval_reply: str
    extra_patterns: list[tuple[re.Pattern, str]]  # (pattern, reply)
    state_max_chars: int


def read_prompt(prompt: str | None, prompt_file: str | None) -> str:
    if prompt_file:
        return Path(prompt_file).read_text(encoding="utf-8")
    if prompt:
        return prompt
    raise SystemExit("Provide --prompt or --prompt-file")


def build_spawn_command(cfg: LoopConfig, initial_prompt: str) -> list[str]:
    """
    You may need to adapt this depending on your gemini CLI flavor.
    Common patterns are:
      gemini "your prompt"
    or
      gemini --model <name> "your prompt"
    """
    cmd = [cfg.gemini_cmd, *cfg.model_args, initial_prompt]
    return cmd


def spawn_gemini(cfg: LoopConfig, prompt: str) -> pexpect.spawn:
    cmd = build_spawn_command(cfg, prompt)
    child = pexpect.spawn(cmd[0], cmd[1:], encoding="utf-8", echo=False)

    # Log everything (stdin/out) for debugging/auditing
    cfg.log_path.parent.mkdir(parents=True, exist_ok=True)
    logfile = cfg.log_path.open("a", encoding="utf-8")
    child.logfile = logfile
    child.logfile_read = logfile
    child.logfile_send = logfile

    return child


def ralph_loop(cfg: LoopConfig, base_prompt: str) -> str:
    """
    Runs iterative loop:
      prompt -> run gemini -> collect output -> if DONE found return -> else feed back summary and repeat
    """
    state = ""
    last_full_output = ""

    for i in range(1, cfg.max_iters + 1):
        iter_header = (
            f"\n\n===== ITERATION {i}/{cfg.max_iters} @ {time.strftime('%Y-%m-%d %H:%M:%S')} =====\n"
        )
        cfg.log_path.open("a", encoding="utf-8").write(iter_header)

        prompt = base_prompt
        if state.strip():
            prompt += (
                "\n\n---\n"
                "Previous attempt summary/state (for continuity):\n"
                f"{state}\n"
                "---\n"
                "Continue from that state. If complete, output exactly: DONE\n"
            )
        else:
            prompt += "\n\nIf complete, output exactly: DONE\n"

        child = spawn_gemini(cfg, prompt)

        # Patterns we’ll respond to.
        # You can add more patterns via --pattern.
        patterns: list[object] = []

        # DONE marker
        patterns.append(cfg.done_regex)

        # Common approval prompts (best-effort; varies by CLI build/version)
        if cfg.auto_approve:
            # y/n style
            patterns.append(re.compile(r"(?i)\b(?:approve|allow|proceed|continue)\b.*\?\s*$"))
            patterns.append(re.compile(r"(?i)\b(?:y\/n|yes\/no)\b"))
            patterns.append(re.compile(r"(?i)\bconfirm\b.*\?\s*$"))

        # Any extra user-specified patterns
        for pat, _reply in cfg.extra_patterns:
            patterns.append(pat)

        # EOF means the process ended
        patterns.append(pexpect.EOF)

        # TIMEOUT if it hangs
        patterns.append(pexpect.TIMEOUT)

        # We also want to accumulate all text we see.
        output_chunks: list[str] = []

        while True:
            idx = child.expect(patterns, timeout=cfg.timeout_s)

            # Whatever came before the match is in child.before
            if child.before:
                output_chunks.append(child.before)

            matched = patterns[idx]

            # DONE matched
            if isinstance(matched, re.Pattern) and matched.pattern == cfg.done_regex.pattern:
                # Include the match itself
                output_chunks.append(child.match.group(0))
                child.close(force=True)
                last_full_output = "".join(output_chunks)
                return last_full_output

            # Auto-approve prompts
            if cfg.auto_approve and isinstance(matched, re.Pattern):
                # Check if it was one of extra patterns first
                replied = False
                for pat, reply in cfg.extra_patterns:
                    if pat.pattern == matched.pattern:
                        child.sendline(reply)
                        replied = True
                        break
                if replied:
                    continue

                # Otherwise it's a generic approval-ish pattern:
                child.sendline(cfg.approval_reply)
                continue

            # EOF
            if matched is pexpect.EOF:
                child.close()
                break

            # TIMEOUT
            if matched is pexpect.TIMEOUT:
                # Try to stop it; treat as failure for this iter
                try:
                    child.sendcontrol("c")
                except Exception:
                    pass
                child.close(force=True)
                break

        last_full_output = "".join(output_chunks)

        # If it didn’t say DONE, create a short "state" summary to feed back.
        # Keep it lightweight: take the tail (often contains the most recent reasoning/outcome).
        tail = last_full_output[-cfg.state_max_chars :].strip()
        state = (
            "Gemini did not output DONE. Here is the tail of the last run (most recent output):\n"
            + tail
        )

        # Small backoff between runs
        time.sleep(0.5)

    return last_full_output


def parse_extra_patterns(pattern_args: list[str]) -> list[tuple[re.Pattern, str]]:
    """
    Accept --pattern 'REGEX=>REPLY'
    Example:
      --pattern '(?i)type\\s+YES\\s+to\\s+continue=>YES'
    """
    out: list[tuple[re.Pattern, str]] = []
    for item in pattern_args:
        if "=>" not in item:
            raise SystemExit(f"Bad --pattern format (expected REGEX=>REPLY): {item}")
        pat_s, reply = item.split("=>", 1)
        out.append((re.compile(pat_s), reply))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", help="Base task prompt")
    ap.add_argument("--prompt-file", help="Read base prompt from file")
    ap.add_argument("--gemini-cmd", default=os.environ.get("GEMINI_CMD", "gemini"))
    ap.add_argument("--model-arg", action="append", default=[],
                    help="Pass-through args for gemini (repeatable), e.g. --model-arg --model --model-arg gemini-2.0-flash")
    ap.add_argument("--max-iters", type=int, default=5)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--done-regex", default=DONE_REGEX_DEFAULT,
                    help=r"Regex that indicates completion (default: r'(?m)^\s*DONE\s*$')")
    ap.add_argument("--log", default="gemini_ralph.log")
    ap.add_argument("--no-auto-approve", action="store_true", help="Do not auto-answer approval prompts")
    ap.add_argument("--approve-reply", default="y", help="Reply to approval prompts (default: y)")
    ap.add_argument("--pattern", action="append", default=[],
                    help="Extra prompt-response rule: REGEX=>REPLY (repeatable)")
    ap.add_argument("--state-max-chars", type=int, default=2500,
                    help="How much of last output to carry forward as state")
    args = ap.parse_args()

    base_prompt = read_prompt(args.prompt, args.prompt_file)

    cfg = LoopConfig(
        gemini_cmd=args.gemini_cmd,
        model_args=args.model_arg,
        max_iters=args.max_iters,
        timeout_s=args.timeout,
        done_regex=re.compile(args.done_regex),
        log_path=Path(args.log),
        auto_approve=not args.no_auto_approve,
        approval_reply=args.approve_reply,
        extra_patterns=parse_extra_patterns(args.pattern),
        state_max_chars=args.state_max_chars,
    )

    final_output = ralph_loop(cfg, base_prompt)

    # Print final output to stdout so you can pipe it elsewhere.
    sys.stdout.write(final_output)
    if not final_output.endswith("\n"):
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
