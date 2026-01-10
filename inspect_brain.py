from supabase import create_client
import os
import json

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    # Fallback to hardcoded if env vars missing in this shell session (safety net)
    url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1OTA0MjQsImV4cCI6MjA4MjE2NjQyNH0.dluuiK-jr-3Z_oksYHS4saSthpkppLHQGnl6YtploPU"

client = create_client(url, key)

print("🧠 CONSULTING BRAIN MEMORY (system_logs)...")

try:
    # Try to fetch one row to see the keys (columns)
    response = client.table("system_logs").select("*").limit(1).execute()
    
    if len(response.data) > 0:
        print("✅ Connection Successful.")
        print("📋 Table Schema (Inferred from Row 1):")
        keys = response.data[0].keys()
        for k in keys:
            print(f"   - {k}")
            
        print("\n🔍 Recent Brain Activity:")
        recent = client.table("system_logs").select("*").order("created_at", desc=True).limit(3).execute()
        for log in recent.data:
            print(f"   [{log.get('level')}] {log.get('message', '')[:50]}... ({log.get('created_at')})")
            
    else:
        print("⚠️ Table is empty. Cannot infer schema.")
        # Try inserting a dummy row to test columns if empty
        print("   Attempting test insert...")
        try:
            test_data = {"level": "INFO", "message": "Schema Probe"}
            client.table("system_logs").insert(test_data).execute()
            print("   ✅ Insert 'level, message' SUCCESS.")
        except Exception as e:
            print(f"   ❌ Insert Failed: {e}")

except Exception as e:
    print(f"❌ BRAIN DAMAGE DETECTED: {e}")
