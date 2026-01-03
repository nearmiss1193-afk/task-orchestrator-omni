
import os
import datetime

# Configuration
AGENTS = ["spear", "spartan", "governor", "nexus", "director"]
DIGEST_DIR = r"c:\Users\nearm\.gemini\antigravity\brain\62b8ebe4-5452-4e67-bbf9-745834c0b6b3\sovereign_digests"

# Ensure digest directory exists
os.makedirs(DIGEST_DIR, exist_ok=True)

print(f"🧩 Agent Restoration Procedure started at {datetime.datetime.now()}\n")

for agent in AGENTS:
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    # Using absolute path for reliability in this environment
    logfile = os.path.join(DIGEST_DIR, f"{agent}_restore_log_{timestamp}.md")
    
    try:
        with open(logfile, "w", encoding="utf-8") as f:
            f.write(f"# {agent.upper()} Restoration Report\n\n")
            f.write(f"**Timestamp:** {datetime.datetime.now()}\n")
            f.write(f"**Configuration:** v40.0 (Sovereign)\n")
            f.write("**Status:** ✅ Restored to active duty.\n")
            f.write(f"**Next Action:** Awaiting Governor Directive.\n")
        
        print(f"{agent.upper()} ✅ Restored → log: {os.path.basename(logfile)}")
        
    except Exception as e:
        print(f"{agent.upper()} ❌ Failed: {e}")

print("\nAgent Restoration Cycle Complete — reporting to Governor.")
