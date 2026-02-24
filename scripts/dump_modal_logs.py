import subprocess
import os

def dump():
    # 1. run modal app list
    print("--- MODAL APPS ---")
    try:
        app_list = subprocess.run(["python", "-m", "modal", "app", "list"], capture_output=True, text=True)
        print(app_list.stdout)
        print(app_list.stderr)
    except Exception as e:
        print(e)

    # 2. redirect logs to file
    print("--- FETCHING LOGS ---")
    try:
        logs = subprocess.run(["python", "-m", "modal", "app", "logs", "ghl-omni-automation"], capture_output=True, text=True)
        with open("clean_modal_logs.txt", "w", encoding="utf-8") as f:
            f.write(logs.stdout)
            f.write(logs.stderr)
        print("Logs saved to clean_modal_logs.txt")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    dump()
