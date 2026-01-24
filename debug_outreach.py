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

from execution.v2.v2_outreach_orchestrator import V2OutreachOrchestrator

async def main():
    print("[DEBUG] Triggering Manual Outreach Sequence...")
    orch = V2OutreachOrchestrator()
    await orch.run_sequence()

if __name__ == "__main__":
    asyncio.run(main())
