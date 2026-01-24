
import os

files_to_check = ["deploy_mission_res.txt", "modal_log.txt", "ghl_debug.txt"]

print("🔍 SCANNING LOG FILES...")
for fname in files_to_check:
    if os.path.exists(fname):
        print(f"\n--- Reading {fname} ---")
        try:
            with open(fname, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if "sk_live" in content:
                    print(f"✅ FOUND 'sk_live' in {fname}!")
                    # Find the line
                    for line in content.splitlines():
                        if "sk_live" in line:
                            print(f"MATCH: {line.strip()[:50]}...") # Truncate for safety/brevity
                else:
                    print(f"❌ 'sk_live' not found in {fname}")
                
                if "STRIPE" in content:
                     print(f"✅ FOUND 'STRIPE' in {fname}!")
        except Exception as e:
            print(f"Error reading {fname}: {e}")
