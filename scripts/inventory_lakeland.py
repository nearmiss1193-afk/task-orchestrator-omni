"""Inventory Lakeland business data for outreach pivot"""
import csv
import json
import os

# Check both CSVs
csvs = [
    r'c:\Users\nearm\.gemini\antigravity\scratch\lakeland-local-prod\scripts\lakeland_businesses.csv',
    r'c:\Users\nearm\.gemini\antigravity\scratch\lakeland-local-prod\scripts\lakeland_businesses_expanded.csv',
]

for path in csvs:
    basename = os.path.basename(path)
    print(f"\n=== {basename} ===")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"Total rows: {len(rows)}")
        if rows:
            print(f"Columns: {list(rows[0].keys())}")
            emails = sum(1 for r in rows if r.get('email'))
            phones = sum(1 for r in rows if r.get('phone'))
            websites = sum(1 for r in rows if r.get('website'))
            print(f"Has email: {emails}")
            print(f"Has phone: {phones}")
            print(f"Has website: {websites}")
            print(f"\nSample row:")
            print(json.dumps(rows[0], indent=2))
    except Exception as e:
        print(f"Error: {e}")

# Also check Neon/Supabase for lakeland-local businesses
print("\n\n=== SUPABASE: contacts_master total ===")
try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv('.env.local')
    from supabase import create_client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
    sb = create_client(url, key)
    r = sb.table('contacts_master').select('id', count='exact').execute()
    print(f"Total contacts_master: {r.count}")
except Exception as e:
    print(f"Error: {e}")
