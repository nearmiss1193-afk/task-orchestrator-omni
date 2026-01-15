import os
import json
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not url or not key:
    print("Error: Missing Supabase credentials in .env")
    exit(1)

client = create_client(url, key)

def get_stats():
    res = client.table('leads').select('status').execute()
    stats = {}
    for item in res.data:
        s = item['status']
        stats[s] = stats.get(s, 0) + 1
    print(f"Lead Stats: {json.dumps(stats, indent=2)}")

def get_backlog():
    # Show top 5 enriched/audited leads
    res = client.table('leads').select('*').in_('status', ['enriched', 'audited']).limit(5).execute()
    print("\nBacklog Leads:")
    for lead in res.data:
        print(f" - {lead['company_name']} ({lead['status']}) | Phone: {lead.get('phone')}")

if __name__ == "__main__":
    get_stats()
    get_backlog()
