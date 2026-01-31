#!/usr/bin/env python3
"""
Ralph Loop for Opencode - Hackmud Assistant Mode
Continuously reads CLAUDE.md, checks Discord, responds, and handles programming tasks
"""

import subprocess
import json
import time
import os
from pathlib import Path
from datetime import datetime

def hackmud_ralph_loop(max_iterations=None, delay=30):
    """Run opencode in Ralph Loop for hackmud assistance"""
    
    iteration = 0
    while max_iterations is None or iteration < max_iterations:
        print(f"\n=== Ralph Loop Iteration {iteration + 1} ===")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Construct the prompt for opencode
        prompt = f"""You are opencode, an AI assistant for hackmud. Your role is to help with hackmud-related tasks WITHOUT actually playing the game.

Current Rules:
1. Read CLAUDE.md to understand your context and memory
2. Check Discord for new messages (especially from trusted users: zenchess, kaj, dunce, psinabby)
3. Respond to Discord messages if needed
4. Handle any programming tasks requested
5. DO NOT play hackmud (no hacking NPCs, no sending game commands)
6. Focus on: code analysis, Discord communication, script development, file operations

Current iteration: {iteration + 1}
Previous iterations completed: {iteration}

Please:
1. Read your memory file (claude_memory.txt) 
2. Check for Discord messages from the last {delay} seconds
3. Respond if there are programming tasks or questions
4. Update your memory if anything important happens
5. Report what you did this iteration"""

        try:
            # Execute opencode with the prompt
            result = execute_opencode(prompt)
            
            # Log the result
            log_iteration(iteration + 1, prompt, result)
            
            print(f"Opencode completed iteration {iteration + 1}")
            
            iteration += 1
            
            # Wait before next iteration
            print(f"Waiting {delay} seconds before next iteration...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"Error in iteration {iteration + 1}: {e}")
            log_iteration(iteration + 1, prompt, f"ERROR: {e}")
            iteration += 1
            time.sleep(delay)
    
    return True

def execute_opencode(prompt):
    """Execute opencode with the given prompt"""
    try:
        # Use opencode run command
        cmd = ["opencode", "run", prompt]
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300,  # 5 minute timeout
            cwd="/home/jacob/hackmud"
        )
        
        if result.returncode != 0:
            raise Exception(f"Opencode failed with return code {result.returncode}: {result.stderr}")
        
        return result.stdout.strip()
        
    except subprocess.TimeoutExpired:
        raise Exception("Opencode timed out after 5 minutes")
    except FileNotFoundError:
        raise Exception("Opencode command not found - make sure opencode is installed and in PATH")

def log_iteration(iteration, prompt, result):
    """Log each iteration to a file"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "iteration": iteration,
        "prompt": prompt,
        "result": result
    }
    
    log_file = Path("/home/jacob/hackmud/ralph_loop_log.jsonl")
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    # Keep only last 1000 lines to prevent log from growing too large
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) > 1000:
            with open(log_file, 'w') as f:
                f.writelines(lines[-1000:])
    except:
        pass  # If log file operations fail, continue

def print_status():
    """Print current status"""
    print("=== Ralph Loop for Opencode - Hackmud Assistant ===")
    print("Purpose: Monitor Discord, handle programming tasks, assist with hackmud")
    print("Rules: DO NOT play hackmud, only assist with related tasks")
    print(f"Working directory: {os.getcwd()}")
    print(f"Log file: /home/jacob/hackmud/ralph_loop_log.jsonl")
    print("=" * 60)

if __name__ == "__main__":
    print_status()
    
    try:
        # Run the Ralph loop
        hackmud_ralph_loop(max_iterations=None, delay=60)  # Check every minute
    except KeyboardInterrupt:
        print("\nRalph Loop stopped by user")
    except Exception as e:
        print(f"\nRalph Loop crashed: {e}")
        # You might want to restart the loop here automatically