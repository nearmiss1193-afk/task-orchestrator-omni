import os
import re

HEADER = "\033[95m[AUDIT]\033[0m"

def find_inline_css():
    print(f"{HEADER} Scanning for Inline CSS...")
    start_dir = "public"
    count = 0
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.readlines()
                    for i, line in enumerate(content):
                        if 'style="' in line:
                            print(f"  ⚠️  Inline CSS in {file}:{i+1}")
                            count += 1
    print(f"{HEADER} Found {count} instances of inline CSS.")

def check_process_resilience():
    print(f"{HEADER} Checking Process Resilience...")
    # Check if watchdog.py exists
    if os.path.exists("watchdog.py"):
        print("  ✅ watchdog.py exists.")
    else:
        print("  ❌ watchdog.py MISSING.")

def main():
    print("🔎 STARTING SYSTEM AUDIT")
    find_inline_css()
    check_process_resilience()
    print("✅ AUDIT COMPLETE")

if __name__ == "__main__":
    main()
