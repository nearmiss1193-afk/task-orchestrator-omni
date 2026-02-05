"""
EMERGENCY: Rapid Lead Check and Email Generation
Get leads ready for Dan's 8:30 AM review
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def check_table(table_name: str):
    """Check a table for leads"""
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=*&limit=20"
    resp = httpx.get(url, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        return data
    else:
        return None

def main():
    print("=" * 60)
    print("🔍 LEAD INVENTORY CHECK - 8:30 AM DEADLINE")
    print("=" * 60)
    
    # Check multiple tables for leads
    tables_to_check = ["contacts_master", "leads", "prospect_targets", "contacts"]
    
    for table in tables_to_check:
        print(f"\n📊 Checking {table}...")
        data = check_table(table)
        if data:
            print(f"   ✅ Found {len(data)} records")
            if len(data) > 0:
                # Show sample columns
                sample = data[0]
                cols = list(sample.keys())[:8]
                print(f"   Columns: {', '.join(cols)}")
                
                # Look for email field
                email_fields = [k for k in sample.keys() if 'email' in k.lower()]
                if email_fields:
                    with_email = [r for r in data if r.get(email_fields[0])]
                    print(f"   📧 Records with email: {len(with_email)}")
        else:
            print(f"   ❌ No data or error")
    
    # Check outbound_touches for recent outreach
    print(f"\n📤 Checking outbound_touches (recent outreach)...")
    url = f"{SUPABASE_URL}/rest/v1/outbound_touches?select=*&limit=5&order=ts.desc"
    resp = httpx.get(url, headers=HEADERS)
    if resp.status_code == 200:
        touches = resp.json()
        print(f"   Recent touches: {len(touches)}")
        for t in touches[:3]:
            print(f"   - {t.get('channel', '?')}: {t.get('ts', '?')[:19]}")
    
    print("\n" + "=" * 60)
    print("📊 NEXT STEPS")
    print("=" * 60)

if __name__ == "__main__":
    main()
