import asyncio
import os
import json
from dotenv import load_dotenv

# Mock Modal Secret for local run
os.environ["GEMINI_API_KEY"] = "AIzaSyALaxJstr7hiyyC52zTZOd2ymow5v1-PKY"
os.environ["NEXT_PUBLIC_SUPABASE_URL"] = "https://rzcpfwkygdvoshtwxncs.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

load_dotenv('.env.local')

from deploy import _hiring_spartan_logic

async def test_local():
    print("Testing Hiring Logic Locally...")
    payload = {
        "type": "InboundMessage",
        "contact_id": "test_local_cont",
        "contact": {
            "tags": ["candidate"],
            "name": "Local Tester",
            "email": "local@test.com"
        },
        "message": {
            "body": "Hello, I want to apply for the AI role."
        }
    }
    
    try:
        result = await _hiring_spartan_logic(payload)
        print(f"SUCCESS Result: {result}")
    except Exception as e:
        import traceback
        print(f"FAILED: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_local())
