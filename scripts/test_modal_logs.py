import os
import sys

def force_logs():
    import subprocess
    # Run the equivalent of `modal app logs ghl-omni-automation` but export to file
    try:
        res = subprocess.run(
            ["python", "-m", "modal", "app", "logs", "ghl-omni-automation"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        with open("modal_native_trace.txt", "w", encoding="utf-8") as f:
            f.write("STDOUT:\n")
            f.write(res.stdout[-15000:])
            f.write("\nSTDERR:\n")
            f.write(res.stderr[-15000:])
        print("Exported to modal_native_trace.txt")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    force_logs()
