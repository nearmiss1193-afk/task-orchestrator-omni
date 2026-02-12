"""Quick debug: try importing 1 lead to see the error"""
import csv, os, json
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
from supabase import create_client

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
sb = create_client(url, key)

# Read one business with email
with open(r'scripts/lakeland_businesses_enriched.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for biz in reader:
        if biz.get('email'):
            lead = {
                "full_name": biz.get('name', 'Test').split()[0],
                "company_name": biz.get('name', 'Test Business'),
                "email": biz['email'].lower().strip(),
                "phone": biz.get('phone', ''),
                "website_url": biz.get('website', ''),
                "niche": biz.get('category', 'Local Business'),
                "status": "new",
                "source": "lakeland_finds",
                "notes": json.dumps({"google_rating": float(biz.get('rating',0) or 0), "total_reviews": int(biz.get('total_ratings',0) or 0)})
            }
            print(f"Trying: {lead['email']} ({lead['company_name']})")
            try:
                result = sb.table("contacts_master").insert(lead).execute()
                print(f"SUCCESS: {result.data[0]['id']}")
            except Exception as e:
                print(f"ERROR: {e}")
            break
