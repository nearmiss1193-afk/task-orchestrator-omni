"""Probe the actual Supabase leads table schema - FULL OUTPUT."""
import os
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

client = create_client(url, key)

print("🔍 Probing leads table schema...")

try:
    result = client.table("leads").select("*").limit(1).execute()
    
    if result.data:
        print("✅ Found existing row. Columns:")
        cols = list(result.data[0].keys())
        for col in cols:
            print(f"   - {col}: {type(result.data[0].get(col)).__name__}")
        
        # Write to file for analysis
        with open("leads_schema.json", "w") as f:
            json.dump({"columns": cols, "sample_row": result.data[0]}, f, indent=2, default=str)
        print("\n📄 Full schema saved to leads_schema.json")
    else:
        print("⚠️ Table is empty")
        
except Exception as e:
    print(f"❌ Error: {e}")
