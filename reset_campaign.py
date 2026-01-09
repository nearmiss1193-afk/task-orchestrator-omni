import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def reset_leads():
    print("RESETTING ALL LEADS TO 'ready_to_send'...")
    try:
        # Update all leads that represent actual prospects (excluding our test user perhaps, or just all)
        # We'll just reset everything for the full campaign launch.
        res = supabase.table("leads").update({
            "status": "ready_to_send",
            "last_contacted_at": None, # Clear timestamp
            "email_sent_at": None      # Clear email timestamp
        }).neq("id", "0000").execute() # effectively all
        
        print(f"SUCCESS: Campaign Reset. All leads ready for Email -> Call flow.")
    except Exception as e:
        print(f"Error resetting leads: {e}")

if __name__ == "__main__":
    reset_leads()
