import csv
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

# Load environment variables
load_dotenv()

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ ERROR: Missing Supabase credentials in .env")
    exit(1)

supabase = create_client(url, key)

def import_leads():
    print(f"Starting import of Manus leads to {url}...")
    
    leads_to_insert = []
    count = 0
    skipped = 0
    
    try:
        with open('manus_leads.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                company_name = row.get('Company Name', '').strip()
                phone = row.get('Phone', '').strip()
                email = row.get('Email', '').strip()
                batch = row.get('Batch', '1')
                
                # Clean missing values
                if email.lower() in ['not found', 'n/a', 'null', 'none']:
                    email = None
                if not email:
                    email = None
                
                if phone.lower() in ['not found', 'n/a', 'null', 'none']:
                    phone = None
                if not phone:
                    phone = None

                lead_data = {
                    "company_name": company_name,
                    "phone": phone,
                    "email": email,
                    "status": "pending",
                    "created_at": datetime.now().isoformat()
                }
                
                # Simple insert
                try:
                    res = supabase.table('leads').insert(lead_data).execute()
                    count += 1
                    if count % 20 == 0:
                        print(f"Processed {count} leads...")
                except Exception as e:
                    print(f"Error inserting {company_name}: {e}")
                    skipped += 1
        
        print(f"✅ Successfully finished. Imported/Updated: {count}, Skipped: {skipped}")
        
    except FileNotFoundError:
        print("❌ ERROR: manus_leads.csv not found")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    import_leads()
