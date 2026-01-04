# Hackmud Linux Automation Plan

## Goal
Use a second user to hack NPCs and transfer GC + upgrades back to `zenchess` (main user), keeping zenchess safe to run the chess script.

---

## Tools We Have

1. **mem_scanner.py** - Reads JSON responses from hackmud memory
   - Run: `python3 mem_scanner.py` (one-time scan)
   - Run: `python3 mem_scanner.py --watch` (continuous, writes to ~/hackmud_responses.txt)

2. **send_command.py** - Sends commands to hackmud window via xdotool
   - Run: `python3 send_command.py "command"` (types and presses Enter)
   - Run: `python3 send_command.py "command" --no-enter` (types only)

---

## Workflow

### Phase 1: Setup Second User
1. `create_user` - Create the hacking alt
2. `marks.sync` - Skip the tutorial
3. Note the username for transfers

### Phase 2: Find NPC Locs
1. Run `scripts.fullsec` to see available sectors
2. Join sectors: `chats.join{channel:"SECTOR_NAME"}`
3. Browse sector scripts: `scripts.fullsec{sector:"SECTOR_NAME"}`
4. Run `.pub` / `.public` scripts and solve puzzles to get locs

### Phase 3: Crack Locks & Steal
1. Call the loc to see what locks it has
2. Run cracking script to brute-force the locks
3. Once breached:
   - `sys.xfer_gc_from{target:"npc.loc"}` - Steal GC (needs transfer_v1 upgrade)
   - Or loot upgrades directly

### Phase 4: Transfer to zenchess
```
accts.xfer_gc_to{to:"zenchess", amount:"XXXGC"}
sys.xfer_upgrade_to{to:"zenchess", i:INDEX}
```

---

## Lock Solutions Reference

### Tier 1 Locks

#### EZ_21
```
EZ_21: "open" | "release" | "unlock"
```

#### EZ_35
```
EZ_35: "open" | "release" | "unlock"
digit: 0-9
```

#### EZ_40
```
EZ_40: "open" | "release" | "unlock"
ez_prime: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
```

#### c001
```
c001: "red" | "orange" | "yellow" | "lime" | "green" | "cyan" | "blue" | "purple"
color_digit: 0-9 (try all, one will work)
```

#### c002
```
c002: color
c002_complement: opposite color
  red <-> green
  orange <-> cyan
  yellow <-> blue
  lime <-> purple
```

#### c003
```
c003: color
c003_triad_1: (colorIndex + 5) % 8
c003_triad_2: (colorIndex + 3) % 8

Color indices: red=0, orange=1, yellow=2, lime=3, green=4, cyan=5, blue=6, purple=7
```

#### l0cket
```
l0cket: password from k3y upgrades
T1 passwords: vc2c7q, cmppiq, tvfkyq, euphlaw, 6hh8xw, xwz7ja, sa23uw, 72umy0
```

#### DATA_CHECK
```
1. Call with DATA_CHECK:""  (empty string to get questions)
2. Answer lore questions, combine answers into single word
```

---

## Scripts To Write

### 1. t1_cracker.js
Brute-force T1 locks automatically. Takes a loc, tries all combinations.

### 2. loc_scanner.js
Automate running public scripts to collect locs.

### 3. auto_transfer.js
After a successful breach, automatically transfer GC and upgrades to zenchess.

---

## Automation Flow (Future)

```
[mem_scanner.py] --> reads game responses
        |
        v
[Python controller] --> parses locs, lock types
        |
        v
[send_command.py] --> sends cracking commands
        |
        v
[mem_scanner.py] --> reads result (success/fail)
        |
        v
[send_command.py] --> transfer loot to zenchess
```

---

## Safety Notes

- Keep zenchess out of PvP - only use for receiving transfers and running chess
- The alt takes all the risk of being hacked back
- Don't store large amounts of GC on the alt - transfer immediately
