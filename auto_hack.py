#!/usr/bin/env python3
"""
Automated T2 NPC hacker for hackmud
"""

import subprocess
import time
import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
LOG_FILE = SCRIPT_DIR / "responses.log"

# Known lock solutions
COLORS = ["red", "orange", "yellow", "lime", "green", "cyan", "blue", "purple"]
L0CKET_KEYS = ["cmppiq", "6hh8xw", "uphlaw", "vc2c7q", "tvfkyq", "xwz7ja", "sa23uw", "ellux0", "72umy0"]
EZ_LOCKS = ["open", "unlock", "release"]

# Corps and their password/project info
CORPS = [
    {"script": "weyland.public", "cmd_key": "cmd", "pass_key": "pass", "password": "knowyourteam", "dir_cmd": "directory"},
    {"script": "tyrell.public", "cmd_key": "nav", "pass_key": "p", "password": "bethebest", "dir_cmd": "list"},
]

# Projects to try for T2 locs
PROJECTS = ["thefloood", "forgetme_nt", "Free_BFG", "H0meEntert4inment", "ls_rites", "ragnaroxx.sh", "LUNARLANDER_01.11.bat"]

def find_hackmud_window():
    """Find the hackmud window ID"""
    try:
        result = subprocess.run(['xdotool', 'search', '--name', 'hackmud'], capture_output=True, text=True)
        windows = result.stdout.strip().split('\n')
        if windows and windows[0]:
            return windows[0]
    except Exception as e:
        print(f"Error finding window: {e}")
    return None

def send_command(command, press_enter=True):
    """Send a command to hackmud"""
    window_id = find_hackmud_window()
    if not window_id:
        print("Hackmud window not found!")
        return False

    try:
        subprocess.run(['xdotool', 'type', '--window', window_id, '--delay', '20', command], check=True)
        if press_enter:
            time.sleep(0.1)
            subprocess.run(['xdotool', 'key', '--window', window_id, 'Return'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error sending command: {e}")
        return False

def get_latest_response(timeout=3):
    """Get the latest response from the log"""
    start_time = time.time()
    last_size = LOG_FILE.stat().st_size if LOG_FILE.exists() else 0

    while time.time() - start_time < timeout:
        if LOG_FILE.exists():
            current_size = LOG_FILE.stat().st_size
            if current_size > last_size:
                with open(LOG_FILE, 'r') as f:
                    content = f.read()
                # Get last entry
                pattern = r'--- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(0x[0-9a-f]+)\] ---\n(.+?)(?=\n---|\Z)'
                matches = list(re.finditer(pattern, content, re.DOTALL))
                if matches:
                    last = matches[-1]
                    try:
                        return json.loads(last.group(3).strip())
                    except:
                        pass
        time.sleep(0.3)
    return None

def wait_for_response(script_name, timeout=5):
    """Wait for a specific script response"""
    start_time = time.time()
    seen_timestamps = set()

    while time.time() - start_time < timeout:
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r') as f:
                content = f.read()
            pattern = r'--- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(0x[0-9a-f]+)\] ---\n(.+?)(?=\n---|\Z)'
            for match in re.finditer(pattern, content, re.DOTALL):
                ts = match.group(1)
                if ts in seen_timestamps:
                    continue
                try:
                    data = json.loads(match.group(3).strip())
                    if data.get('script_name', '').startswith(script_name) or script_name in data.get('script_name', ''):
                        seen_timestamps.add(ts)
                        return data
                except:
                    pass
        time.sleep(0.3)
    return None

def do_hardline():
    """Establish hardline connection"""
    print("Establishing hardline...")
    window_id = find_hackmud_window()
    if not window_id:
        return False

    # Send kernel.hardline
    subprocess.run(['xdotool', 'type', '--window', window_id, 'kernel.hardline'], check=True)
    time.sleep(0.1)
    subprocess.run(['xdotool', 'key', '--window', window_id, 'Return'], check=True)

    # Wait for hardline animation
    time.sleep(10)

    # Spam 0-9 keys
    for _ in range(30):
        for key in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            subprocess.run(['xdotool', 'key', '--window', window_id, key], check=True)

    time.sleep(2)

    # Check if connected
    send_command('kernel.hardline')
    time.sleep(2)
    resp = get_latest_response()
    if resp and resp.get('retval', {}).get('remaining'):
        print(f"Hardline active: {resp['retval']['remaining']}s remaining")
        return True
    return False

def disconnect_hardline():
    """Disconnect hardline"""
    send_command('kernel.hardline{dc:true}')
    time.sleep(1)

def get_t2_locs():
    """Get T2 NPC locations from corp scripts"""
    locs = []

    for corp in CORPS:
        for project in PROJECTS:
            cmd = f'{corp["script"]}{{{corp["cmd_key"]}:"{corp["dir_cmd"]}", {corp["pass_key"]}:"{corp["password"]}", project:"{project}"}}'
            send_command(cmd)
            time.sleep(2)

            resp = get_latest_response()
            if resp and isinstance(resp.get('retval'), list):
                for loc in resp['retval']:
                    # Clean up corrupted characters
                    clean_loc = re.sub(r'`[^`]*`', '', loc)
                    if '.' in clean_loc and len(clean_loc) > 10:
                        locs.append(clean_loc)
                print(f"Found {len(resp['retval'])} locs from {project}")

    return list(set(locs))

def try_crack_npc(npc_loc):
    """Try to crack an NPC with known lock solutions"""
    print(f"\nTrying: {npc_loc}")

    # First, see what locks it has
    send_command(f'{npc_loc}{{}}')
    time.sleep(2)
    resp = get_latest_response()

    if not resp:
        return False

    retval = resp.get('retval', '')
    if isinstance(retval, dict):
        retval = str(retval)

    # Check for success
    if 'LOCK_UNLOCKED' in retval and 'Connection terminated' in retval:
        print(f"SUCCESS: {npc_loc} - No locks!")
        return True

    # Check for hardline required
    if 'hardline required' in retval:
        print("Hardline required but not active")
        return False

    # Build lock solution
    locks = {}

    # Detect lock types
    if 'l0cket' in retval.lower():
        # Try l0cket keys
        for key in L0CKET_KEYS:
            locks['l0cket'] = key
            cmd = f'{npc_loc}{{{",".join(f"{k}:\\"{v}\\"" for k,v in locks.items())}}}'
            send_command(cmd)
            time.sleep(2)
            resp = get_latest_response()
            if resp and 'LOCK_UNLOCKED' in str(resp.get('retval', '')):
                if 'Connection terminated' in str(resp.get('retval', '')):
                    print(f"SUCCESS with l0cket:{key}")
                    return True
                break  # l0cket passed, continue to next lock

    if 'EZ_21' in retval or 'EZ_35' in retval or 'EZ_40' in retval:
        for ez in ['EZ_21', 'EZ_35', 'EZ_40']:
            if ez in retval:
                locks[ez] = 'unlock'
                break

    if 'c001' in retval.lower():
        for color in COLORS:
            locks['c001'] = color
            cmd = f'{npc_loc}{{{",".join(f"{k}:\\"{v}\\"" for k,v in locks.items())}}}'
            send_command(cmd)
            time.sleep(1.5)
            resp = get_latest_response()
            if resp and 'not the correct color' not in str(resp.get('retval', '')):
                break

    if 'c002' in retval.lower():
        for color in COLORS:
            locks['c002'] = color
            cmd = f'{npc_loc}{{{",".join(f"{k}:\\"{v}\\"" for k,v in locks.items())}}}'
            send_command(cmd)
            time.sleep(1.5)
            resp = get_latest_response()
            if resp and 'not the correct color' not in str(resp.get('retval', '')):
                break

    if 'c003' in retval.lower():
        for color in COLORS:
            locks['c003'] = color
            cmd = f'{npc_loc}{{{",".join(f"{k}:\\"{v}\\"" for k,v in locks.items())}}}'
            send_command(cmd)
            time.sleep(1.5)
            resp = get_latest_response()
            if resp and 'not the correct color' not in str(resp.get('retval', '')):
                break

    # Final attempt with all found locks
    if locks:
        cmd = f'{npc_loc}{{{",".join(f"{k}:\\"{v}\\"" for k,v in locks.items())}}}'
        send_command(cmd)
        time.sleep(2)
        resp = get_latest_response()
        if resp and 'Connection terminated' in str(resp.get('retval', '')):
            print(f"SUCCESS: {locks}")
            return True

    print(f"Could not crack: {retval[:100]}")
    return False

def check_and_transfer():
    """Check balance and transfer to zenchess"""
    send_command('accts.balance{}')
    time.sleep(2)
    resp = get_latest_response()

    if resp and resp.get('retval'):
        balance = resp['retval']
        print(f"Current balance: {balance}")

        if balance != '0GC':
            send_command(f'accts.xfer_gc_to{{to:"zenchess", amount:"{balance}"}}')
            time.sleep(2)
            print(f"Transferred {balance} to zenchess")

def main():
    print("=== Automated T2 NPC Hacker ===")
    print("Press Ctrl+C to stop\n")

    hacked_npcs = set()

    while True:
        try:
            # Get T2 locs
            print("\n--- Getting T2 NPC locations ---")
            locs = get_t2_locs()
            print(f"Found {len(locs)} total locs")

            # Filter out already hacked
            new_locs = [l for l in locs if l not in hacked_npcs]
            print(f"{len(new_locs)} new locs to try")

            if not new_locs:
                print("No new locs, waiting 5 minutes...")
                time.sleep(300)
                continue

            # Establish hardline
            if not do_hardline():
                print("Failed to establish hardline, waiting 20s...")
                time.sleep(20)
                continue

            # Try each loc
            hardline_start = time.time()
            for loc in new_locs:
                # Check if hardline expired (2 min max)
                if time.time() - hardline_start > 100:
                    print("Hardline expiring, reconnecting...")
                    disconnect_hardline()
                    time.sleep(17)
                    if not do_hardline():
                        break
                    hardline_start = time.time()

                if try_crack_npc(loc):
                    hacked_npcs.add(loc)
                else:
                    # Mark as tried even if failed
                    hacked_npcs.add(loc)

            # Disconnect and transfer
            disconnect_hardline()
            time.sleep(2)
            check_and_transfer()

            print(f"\n--- Cycle complete. Hacked {len(hacked_npcs)} NPCs total ---")
            print("Waiting 60s before next cycle...")
            time.sleep(60)

        except KeyboardInterrupt:
            print("\nStopping...")
            check_and_transfer()
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == '__main__':
    main()
