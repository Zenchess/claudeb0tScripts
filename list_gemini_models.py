
import subprocess
import sys

def run_cmd(cmd: list[str], timeout: int = 120) -> tuple[int, str, str]:
    """Run a subprocess, capture stdout/stderr."""
    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    return p.returncode, p.stdout, p.stderr

def main():
    gemini_cmd = "gemini" # Assuming 'gemini' is the executable name

    try:
        rc, out, err = run_cmd([gemini_cmd, "--help"])
        if rc == 0:
            print("Gemini CLI Help Output:")
            print(out)
        else:
            print(f"Error getting Gemini CLI help (exit code {rc}):")
            print("STDOUT:")
            print(out)
            print("STDERR:")
            print(err)
    except FileNotFoundError:
        print(f"Error: '{gemini_cmd}' command not found. Is gemini-cli installed and in your PATH?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
