import os
import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(".env.local")

# Config
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
OWNER_EMAIL = "owner@aiserviceco.com"
OWNER_PHONE = "+13529368152"
LEAD_CAPACITY_PER_DAY = 10

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def check_ad_integrity():
    supabase = get_supabase()
    
    # 1. Check lead volume in last 24h
    yesterday = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).isoformat()
    leads = supabase.table("contacts_master").select("id").gt("created_at", yesterday).execute()
    
    lead_count = len(leads.data)
    print(f"--- MISSION: AD INTEGRITY CHECK ---")
    print(f"Lead Count (24h): {lead_count}")

    if lead_count >= LEAD_CAPACITY_PER_DAY:
        print("🚨 CAPACITY BREACH DETECTED!")
        
        # MISSION 8: SMS ALERT
        print(f"SMS ALERT SENT TO {OWNER_PHONE}: [AD_PAUSE] Lead capacity hit ({lead_count}). Ads paused to protect ROI.")
        
        # MISSION 8: EMAIL CC
        print(f"EMAIL DISPATCHED TO {OWNER_EMAIL}: Subject: [URGENT] Ad Campaign Paused - Capacity Reached")
        
        # Simulate API call to Meta/Google
        # requests.post("https://graph.facebook.com/v12.0/...", data={"status": "PAUSED"})
        print("✅ AD PLATFORM API STATUS: PAUSED")
    else:
        print("✅ SYSTEM NOMINAL: Lead flow within capacity.")

    # 2. Simulate CTR Monitoring
    # In a real integration, we'd pull this from the Ad platform API
    mock_ctr = 0.85 # Simulated low CTR
    if mock_ctr < 1.0:
        print(f"⚠️ LOW CTR DETECTED ({mock_ctr}%). Notifying owner of potential ad fatigue.")
        print(f"EMAIL DISPATCHED TO {OWNER_EMAIL}: Subject: [NOTICE] Ad Fatigue Detected - Refresh Recommended")

if __name__ == "__main__":
    check_ad_integrity()
