import os
import subprocess

def run_debug():
    # Run the debug script and capture stdout/stderr
    result = subprocess.run(
        ["python", "debug_memory_logic.py"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    
    with open("debug_results.txt", "w", encoding="utf-8") as f:
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\nSTDERR:\n")
        f.write(result.stderr)
    
    print("Debug run complete. Check debug_results.txt")

if __name__ == "__main__":
    run_debug()
