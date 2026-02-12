"""
Import Lakeland Finds businesses into contacts_master.
- Uses the enriched CSV with scraped emails
- Segments by Google review count for prioritized outreach
- Sets source='lakeland_finds' for tracking
- Imports in batches of 50 (daily throttle matches board-approved rate)
"""
import csv, os, json, sys
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

from supabase import create_client

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
sb = create_client(url, key)

def import_lakeland_leads(batch_size=50):
    """Import Lakeland businesses with emails into contacts_master"""
    
    csv_path = r'c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\scripts\lakeland_businesses_enriched.csv'
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        businesses = list(reader)
    
    # Filter to those with emails
    with_email = [b for b in businesses if b.get('email')]
    print(f"Total businesses: {len(businesses)}")
    print(f"With email: {len(with_email)}")
    
    # Check existing to avoid duplicates
    existing_emails = set()
    try:
        # Fetch all existing emails in batches
        offset = 0
        while True:
            res = sb.table("contacts_master").select("email").range(offset, offset + 999).execute()
            for r in res.data:
                if r.get('email'):
                    existing_emails.add(r['email'].lower())
            if len(res.data) < 1000:
                break
            offset += 1000
        print(f"Existing contacts: {len(existing_emails)}")
    except Exception as e:
        print(f"Warning: Could not check existing: {e}")
    
    # Prepare leads for import
    new_leads = []
    skipped_existing = 0
    
    for biz in with_email:
        email = biz.get('email', '').lower().strip()
        if not email or email in existing_emails:
            skipped_existing += 1
            continue
        
        # Parse rating for segmentation
        rating = 0
        try:
            rating = float(biz.get('rating', 0) or 0)
        except:
            pass
        
        total_ratings = 0
        try:
            total_ratings = int(biz.get('total_ratings', 0) or 0)
        except:
            pass
        
        # Segment by review count
        if total_ratings < 10:
            priority = "high"  # Most need help
        elif total_ratings < 30:
            priority = "medium"
        else:
            priority = "low"
        
        name = biz.get('name', 'Unknown Business')
        first_name = name.split()[0] if name else 'there'
        
        lead = {
            "full_name": first_name,
            "company_name": name,
            "email": email,
            "phone": biz.get('phone', ''),
            "website_url": biz.get('website', ''),
            "niche": biz.get('category', 'Local Business'),
            "status": "new",
            "source": "lakeland_finds",
            "notes": json.dumps({
                "google_rating": rating,
                "total_reviews": total_ratings,
                "priority": priority,
                "address": biz.get('address', ''),
                "place_id": biz.get('place_id', ''),
                "imported_at": datetime.now(timezone.utc).isoformat()
            })
        }
        new_leads.append(lead)
        existing_emails.add(email)  # Track to prevent dupes within this batch
    
    print(f"\nSkipped (already in DB): {skipped_existing}")
    print(f"New leads to import: {len(new_leads)}")
    
    # Sort by priority: high first (fewest reviews = most need)
    new_leads.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(
        json.loads(x['notes']).get('priority', 'low'), 3
    ))
    
    # Import first batch
    batch = new_leads[:batch_size]
    print(f"\nImporting first batch of {len(batch)} leads...")
    
    imported = 0
    errors = 0
    for lead in batch:
        try:
            sb.table("contacts_master").insert(lead).execute()
            imported += 1
        except Exception as e:
            if 'duplicate' in str(e).lower() or '23505' in str(e):
                skipped_existing += 1
            else:
                errors += 1
                if errors <= 3:
                    print(f"  Error: {e}")
    
    print(f"\n=== IMPORT RESULTS ===")
    print(f"Imported: {imported}")
    print(f"Skipped (dupe): {skipped_existing}")
    print(f"Errors: {errors}")
    print(f"Remaining in queue: {len(new_leads) - batch_size}")
    
    # Show priority breakdown
    priorities = {"high": 0, "medium": 0, "low": 0}
    for lead in new_leads:
        p = json.loads(lead['notes']).get('priority', 'low')
        priorities[p] = priorities.get(p, 0) + 1
    
    print(f"\nPriority breakdown (all {len(new_leads)} leads):")
    print(f"  HIGH (<10 reviews): {priorities.get('high', 0)}")
    print(f"  MEDIUM (10-30 reviews): {priorities.get('medium', 0)}")
    print(f"  LOW (30+ reviews): {priorities.get('low', 0)}")
    
    return {"imported": imported, "total_ready": len(new_leads), "errors": errors}

if __name__ == '__main__':
    # Import first 50 (the CRON will pick them up automatically)
    result = import_lakeland_leads(batch_size=50)
    print(f"\nResult: {json.dumps(result)}")
