#!/usr/bin/env python3
"""
gemini_ralph_loop.py

A "RALPH loop" wrapper around gemini-cli that:
- repeatedly runs gemini-cli until it outputs DONE (or matches a regex)
- auto-approves tool calls / confirmations (best-effort)
- logs every run
- carries forward a compact transcript tail as "state" each iteration

This assumes gemini-cli is already configured with your tools (Discord tools etc).

Install:
  python -m venv .venv && source .venv/bin/activate
  pip install pexpect

Usage:
  python gemini_ralph_loop.py \
    --model gemini-2.0-flash \
    --prompt-file task.txt \
    --done-regex '(?m)^DONE\\s*$' \
    --log gemini_ralph.log

If you want a single run:
  python gemini_ralph_loop.py --model gemini-2.0-flash --prompt "Hello. Output DONE"
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Pattern, Tuple

import pexpect


@dataclass
class Config:
    gemini_cmd: str
    model: Optional[str]
    max_iters: int
    timeout_s: int
    done_re: Pattern[str]
    log_path: Path
    auto_approve: bool
    approve_reply: str
    state_tail_chars: int
    quiet: bool


def read_prompt(args) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if args.prompt:
        return args.prompt
    raise SystemExit("Provide --prompt or --prompt-file")


def open_log(cfg: Config):
    cfg.log_path.parent.mkdir(parents=True, exist_ok=True)
    return cfg.log_path.open("a", encoding="utf-8", errors="replace")


def spawn_gemini(cfg: Config, prompt: str, logf) -> pexpect.spawn:
    cmd = [cfg.gemini_cmd]

    if cfg.model:
        cmd += ["--model", cfg.model]

    # 🔥 YOLO MODE: auto-approve all tools
    cmd += ["--approval-mode", "yolo"]
    # (equivalent to: cmd += ["-y"])

    cmd += [prompt]

    child = pexpect.spawn(cmd[0], cmd[1:], encoding="utf-8", echo=False)
    child.logfile = logf
    child.logfile_read = logf
    child.logfile_send = logf
    return child


def ralph_loop(cfg: Config, base_prompt: str) -> str:
    state = ""
    final_text = ""

    # Approval prompt patterns (best-effort; adjust if your CLI differs)
    approve_pats = [
        re.compile(r"(?i)\bapprove\b.*\?\s*$"),
        re.compile(r"(?i)\ballow\b.*\?\s*$"),
        re.compile(r"(?i)\bproceed\b.*\?\s*$"),
        re.compile(r"(?i)\bcontinue\b.*\?\s*$"),
        re.compile(r"(?i)\bconfirm\b.*\?\s*$"),
        re.compile(r"(?i)\b(y/n|yes/no)\b"),
        re.compile(r"(?i)\baccept\b.*\?\s*$"),
    ]

    # If gemini-cli emits explicit tool approval lines, match them too
    toolcall_pats = [
        re.compile(r"(?i)\btool\b.*\bcall\b"),
        re.compile(r"(?i)\bexecut(e|ing)\b.*\btool\b"),
        re.compile(r"(?i)\brequesting\b.*\bpermission\b"),
    ]

    for i in range(1, cfg.max_iters + 1):
        with open_log(cfg) as logf:
            header = f"\n\n===== RALPH ITER {i}/{cfg.max_iters} @ {time.strftime('%Y-%m-%d %H:%M:%S')} =====\n"
            logf.write(header)
            logf.flush()
            if not cfg.quiet:
                sys.stderr.write(header)
                sys.stderr.flush()

            prompt = base_prompt.strip()
            if state:
                prompt += (
                    "\n\n---\n"
                    "STATE (carry-forward, do not restate unless needed):\n"
                    f"{state}\n"
                    "---\n"
                )
            prompt += "\n\nWhen you are completely finished, output exactly: DONE\n"

            child = spawn_gemini(cfg, prompt, logf)

            chunks = []

            # Order matters: DONE first so we stop immediately
            patterns = [cfg.done_re]

            if cfg.auto_approve:
                patterns += approve_pats + toolcall_pats

            patterns += [pexpect.EOF, pexpect.TIMEOUT]

            while True:
                idx = child.expect(patterns, timeout=cfg.timeout_s)
                before = child.before or ""
                if before:
                    chunks.append(before)
                    if not cfg.quiet:
                        sys.stdout.write(before)
                        sys.stdout.flush()

                matched = patterns[idx]

                # DONE hit
                if isinstance(matched, re.Pattern) and matched.pattern == cfg.done_re.pattern:
                    # include match itself if available
                    try:
                        chunks.append(child.match.group(0))
                        if not cfg.quiet:
                            sys.stdout.write(child.match.group(0))
                            sys.stdout.flush()
                    except Exception:
                        pass
                    child.close(force=True)
                    final_text = "".join(chunks)
                    return final_text

                # Auto-approve
                if cfg.auto_approve and isinstance(matched, re.Pattern):
                    child.sendline(cfg.approve_reply)
                    continue

                if matched is pexpect.EOF:
                    child.close()
                    break

                if matched is pexpect.TIMEOUT:
                    try:
                        child.sendcontrol("c")
                    except Exception:
                        pass
                    child.close(force=True)
                    break

            # Not DONE: carry forward tail as state
            final_text = "".join(chunks)
            tail = final_text[-cfg.state_tail_chars:].strip()
            state = (
                "Gemini did not output DONE. Tail of last output:\n"
                + tail
            )

            time.sleep(0.5)

    return final_text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", help="Prompt text (quotes recommended)")
    ap.add_argument("--prompt-file", help="Read prompt from file")
    ap.add_argument("--gemini-cmd", default="gemini", help="gemini executable name/path")
    ap.add_argument("--model", default=None, help="Model name for gemini-cli, e.g. gemini-2.0-flash")
    ap.add_argument("--max-iters", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--done-regex", default=r"(?m)^\s*DONE\s*$")
    ap.add_argument("--log", default="gemini_ralph.log")
    ap.add_argument("--no-auto-approve", action="store_true")
    ap.add_argument("--approve-reply", default="y")
    ap.add_argument("--state-tail-chars", type=int, default=3000)
    ap.add_argument("--quiet", action="store_true", help="Don't stream output live; only final result")
    args = ap.parse_args()

    cfg = Config(
        gemini_cmd=args.gemini_cmd,
        model=args.model,
        max_iters=args.max_iters,
        timeout_s=args.timeout,
        done_re=re.compile(args.done_regex),
        log_path=Path(args.log),
        auto_approve=not args.no_auto_approve,
        approve_reply=args.approve_reply,
        state_tail_chars=args.state_tail_chars,
        quiet=bool(args.quiet),
    )

    base_prompt = read_prompt(args)
    out = ralph_loop(cfg, base_prompt)

    # Ensure final newline
    if out and not out.endswith("\n"):
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
