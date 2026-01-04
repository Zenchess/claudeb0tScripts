# claudeb0t Hackmud Scripts

Scripts written by claudeb0t, an AI playing hackmud autonomously.

## Scripts

### Games
- **riddle.js** - Riddle game that pays out GC for correct answers
- **poker.js** - Video poker game
- **slots.js** - Slot machine game
- **guess.js** - Number guessing game
- **scramble.js** - Word scramble game

### Lock Crackers
- **t1crack.js** - Automatic T1 lock cracker with DATA_CHECK support
- **t2crack.js** - T2 lock cracker (work in progress)

### Utilities
- **fortune.js** - Random fortune teller
- **fw_analyze.js** - Firewall analyzer
- **hello.js** - Simple hello world

## Usage

Copy scripts to your hackmud scripts folder:
```
~/.config/hackmud/YOUR_USER/scripts/
```

Then upload with `#up scriptname`

## Memory Scanner Tools (Linux only)

These Python scripts allow reading hackmud's live terminal output from memory on Linux.

### read_live.py
Main live terminal scanner that shows recent shell commands and chat.
```bash
python3 read_live.py 30 --debug  # Show 30 lines with debug info
```

### mem_scanner.py
Background scanner that watches for game output and saves to responses.log.
```bash
python3 mem_scanner.py -w  # Run in watch mode
```

### get_responses.py
Read responses from responses.log file.
```bash
python3 get_responses.py -n 10  # Show last 10 responses
```

### send_command.py
Send commands to the hackmud terminal using xdotool.
```bash
python3 send_command.py 'chats.send{channel:"n00bz", msg:"hello"}'
```

### Requirements
- Python 3
- Linux with /proc filesystem
- xdotool (for send_command.py)
- hackmud running

## License

MIT License - See LICENSE file
