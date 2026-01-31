#!/bin/bash
# Wrapper script for discord_fetch.py that uses discord_venv
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${SCRIPT_DIR}/discord_venv/bin/python" "${SCRIPT_DIR}/discord_tools/discord_fetch.py" "$@"
