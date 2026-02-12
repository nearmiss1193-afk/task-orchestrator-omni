"""Test inserting into contacts_master with ghl_contact_id."""
from supabase import create_client
import os, json, uuid
from dotenv import load_dotenv
load_dotenv()

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

record = {
    "ghl_contact_id": f"prospector-{uuid.uuid4().hex[:12]}",
    "email": "test_prospector_99@example.com",
    "status": "new",
    "source": "prospector",
    "company_name": "Test Prospector Business",
    "phone": "555-999-0001",
    "website_url": "https://testbiz.com",
    "niche": "HVAC contractor",
    "lead_source": "google_places",
    "full_name": "",
    "raw_research": json.dumps({"test": True}),
}

try:
    r = sb.table("contacts_master").insert(record).execute()
    print(f"SUCCESS! ID: {r.data[0]['id']}")
    # Clean up test
    sb.table("contacts_master").delete().eq("id", r.data[0]["id"]).execute()
    print("Cleaned up test record.")
except Exception as e:
    with open("scripts/insert_error2.txt", "w") as f:
        f.write(str(e))
    print(f"ERROR: {type(e).__name__}: {str(e)[:300]}")
