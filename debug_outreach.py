import os
import asyncio
import sys

# Inject Keys manually to ensure it works locally
os.environ["SUPABASE_URL"] = "https://rzcpfwkygdvoshtwxncs.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
os.environ["GEMINI_API_KEY"] = "AIzaSyB_xtLAdE49BYXrgWShwUc4zE2d133VxU0"
os.environ["GHL_LOCATION_ID"] = "RnK4OjX0oDcqtWw0VyLr"
os.environ["GHL_API_TOKEN"] = "pit-8c6cabd9-2c4a-4581-a664-ca2b6200e199"

# Add execution path
sys.path.append(os.getcwd())


print("[DEBUG] Importing Orchestrator...", flush=True)
try:
    from execution.v2.v2_outreach_orchestrator import V2OutreachOrchestrator
except Exception as e:
    import traceback
    print(f"[DEBUG] Import Failed: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

from supabase.client import Client, ClientOptions

def patched_get_supabase(self):
    print("[DEBUG] MONKEY PATCHED get_supabase active", flush=True)
    url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
    return Client(supabase_url=url, supabase_key=key)

V2OutreachOrchestrator._get_supabase = patched_get_supabase

async def main():
    print("[DEBUG] Triggering Manual Outreach Sequence...", flush=True)
    orch = V2OutreachOrchestrator()
    await orch.run_sequence()

if __name__ == "__main__":
    asyncio.run(main())
