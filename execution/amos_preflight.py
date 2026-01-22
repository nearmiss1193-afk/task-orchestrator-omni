import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

# Explicitly load from current directory .env.local
load_dotenv('.env.local')

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not url or not key:
    print("Missing creds in .env.local")
    sys.exit(1)

try:
    client = create_client(url, key)
except Exception as e:
    print(f"Failed to create client: {e}")
    sys.exit(1)

output = []
def log(s):
    print(s)
    output.append(str(s))

log(f"AMOS PRE-FLIGHT - {datetime.now()}")

# 1. Health
log("\n1. SYSTEM HEALTH")
try:
    res = client.table("system_health").select("*").execute()
    if res.data:
        for h in res.data:
            log(f"- {h.get('component')}: {h.get('status')} ({h.get('metric') or ''})")
    else:
        log("No health records found.")
except Exception as e:
    log(f"Error fetching health: {e}")

# 2. State
log("\n2. BROKEN/NOT BUILT")
try:
    res = client.table("system_state").select("*").neq("status", "working").execute()
    data = res.data or []
    # Sort broken first
    data.sort(key=lambda x: 0 if x.get('status')=='broken' else 1)
    
    if data:
        for item in data:
            log(f"- [{item.get('status')}] {item.get('key')} (Attempts: {item.get('build_attempts')})")
            if item.get('last_error'):
                log(f"  Error: {item.get('last_error')}")
    else:
        log("No broken or unbuilt components found.")
except Exception as e:
    log(f"Error fetching state: {e}")

# 3. Buildable
log("\n3. BUILDABLE")
try:
    res = client.table("buildable_components").select("*").eq("status", "pending").limit(5).execute()
    if res.data:
        for item in res.data:
            log(f"- {item.get('component_name') or item.get('key')}")
    else:
        log("No buildable components found.")
except Exception as e:
    log(f"Error fetching buildable: {e}")

# Write absolute path just to be safe, assuming CWD is correct but explicit is better
import os
cwd = os.getcwd()
path = os.path.join(cwd, "preflight_report.txt")
log(f"\nWriting to {path}")

with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("Done.")
