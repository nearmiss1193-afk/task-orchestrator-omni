import os
import json
from dotenv import load_dotenv
from supabase import create_client

# Load from the Next.js portal .env
load_dotenv('apps/portal/.env.local')

# Explicit Supabase initialization
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_KEY or not SUPABASE_URL:
    print("Error: SUPABASE_KEY or SUPABASE_URL environment variable is missing. Ensure SUPABASE_SERVICE_ROLE_KEY is set in .env.local")
    exit(1)

print(f"Loaded Key Prefix: {SUPABASE_KEY[:10]}...")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def recover_payloads():
    print("Starting historical payload recovery...")
    count_updated = 0
    count_skipped = 0

    # Fetch touches where body is logically null (might be explicitly 'null' string in DB)
    response = supabase.table("outbound_touches").select("id, channel, payload, body").execute()
    touches = response.data

    if not touches:
        print("No touches found.")
        return

    for touch in touches:
        # Check if body is missing or literally the string 'null'
        if touch.get("body") is None or str(touch.get("body")).strip() == "" or touch.get("body") == "null":
            payload = touch.get("payload")
            extracted_body = None

            if payload and isinstance(payload, dict):
                # Try to extract from known payload structures
                if touch["channel"] == "sms":
                    extracted_body = payload.get("message")
                elif touch["channel"] == "email":
                    # Resend might have html_body or we might have logged it under 'html' or 'text'
                    extracted_body = payload.get("html_body") or payload.get("text") or payload.get("html")
                
                # Inbound webhook recovery
                if payload.get("direction") == "inbound" and payload.get("text"):
                    extracted_body = payload.get("text")

            if extracted_body:
                # Update the record
                try:
                    # Truncate to reasonable length just in case
                    update_response = supabase.table("outbound_touches").update({"body": str(extracted_body)[:1000]}).eq("id", touch["id"]).execute()
                    count_updated += 1
                except Exception as e:
                    print(f"Failed to update ID {touch['id']}: {e}")
            else:
                count_skipped += 1
        else:
            count_skipped += 1

    print(f"Recovery complete. Updated {count_updated} records. Skipped {count_skipped} records.")

if __name__ == "__main__":
    recover_payloads()
