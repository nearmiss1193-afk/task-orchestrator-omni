"""
Lakeland Bulk Import — Local script to import all 3,300+ businesses from 
lakeland_businesses_enriched.csv into Supabase contacts_master.
Deduplicates against existing records by email.
"""
import os, sys, csv, json, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

from supabase import create_client

def main():
    sb_url = os.environ["SUPABASE_URL"]
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_KEY"]
    sb = create_client(sb_url, sb_key)
    
    # 1. Load CSV
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lakeland_businesses_enriched.csv")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        businesses = list(reader)
    
    print(f"Loaded {len(businesses)} businesses from CSV")
    
    # 2. Get existing emails in Supabase to deduplicate
    existing_emails = set()
    existing_phones = set()
    offset = 0
    while True:
        res = sb.table("contacts_master").select("email,phone").range(offset, offset + 999).execute()
        for r in res.data:
            if r.get('email'):
                existing_emails.add(r['email'].lower().strip())
            if r.get('phone'):
                existing_phones.add(r['phone'].strip())
        if len(res.data) < 1000:
            break
        offset += 1000
    
    print(f"Existing in Supabase: {len(existing_emails)} emails, {len(existing_phones)} phones")
    
    # 3. Prepare batch inserts
    to_insert = []
    skipped_dup = 0
    skipped_no_contact = 0
    
    for biz in businesses:
        email = biz.get('email', '').lower().strip()
        phone = biz.get('phone', '').strip()
        name = biz.get('name', '').strip()
        
        if not name:
            continue
            
        # Skip if no contact info at all
        if not email and not phone:
            skipped_no_contact += 1
            continue
        
        # Deduplicate by email
        if email and email in existing_emails:
            skipped_dup += 1
            continue
        
        # Deduplicate by phone if no email
        if not email and phone and phone in existing_phones:
            skipped_dup += 1
            continue
        
        place_id = biz.get('place_id', '').strip()
        total_ratings = int(biz.get('total_ratings', 0) or 0)
        priority = "high" if total_ratings < 10 else "medium" if total_ratings < 30 else "low"
        
        metadata = {
            "priority": priority,
            "google_rating": float(biz.get('rating', 0) or 0),
            "total_reviews": total_ratings,
            "address": biz.get('address', ''),
            "place_id": place_id,
            "imported_at": datetime.now(timezone.utc).isoformat(),
            "import_type": "bulk_local_import"
        }
        
        # Use company name first word as first_name placeholder
        first_word = name.split()[0] if name else 'there'
        
        lead = {
            "full_name": first_word,
            "company_name": name,
            "email": email if email else None,
            "phone": phone if phone else None,
            "website_url": biz.get('website', ''),
            "niche": biz.get('category', 'Local Business'),
            "status": "new",
            "source": "lakeland_finds",
            "lead_source": "lakeland_finds_directory",
            "ghl_contact_id": f"lkld_{place_id[:30] if place_id else str(int(time.time()))}",
            "ai_strategy": json.dumps(metadata)
        }
        
        to_insert.append(lead)
        
        # Track for dedup within batch
        if email:
            existing_emails.add(email)
        if phone:
            existing_phones.add(phone)
    
    print(f"\nReady to insert: {len(to_insert)}")
    print(f"Skipped (duplicate): {skipped_dup}")
    print(f"Skipped (no contact info): {skipped_no_contact}")
    
    if not to_insert:
        print("Nothing to insert!")
        return
    
    # 4. Batch insert (Supabase supports bulk upsert, do 50 at a time)
    inserted = 0
    errors = 0
    batch_size = 50
    
    for i in range(0, len(to_insert), batch_size):
        batch = to_insert[i:i + batch_size]
        try:
            sb.table("contacts_master").insert(batch).execute()
            inserted += len(batch)
            if (i // batch_size) % 10 == 0:
                print(f"  Inserted {inserted}/{len(to_insert)}...")
        except Exception as e:
            # Try one by one on batch failure
            for lead in batch:
                try:
                    sb.table("contacts_master").insert(lead).execute()
                    inserted += 1
                except Exception as e2:
                    errors += 1
                    if errors <= 5:
                        print(f"  Error: {lead.get('company_name')}: {str(e2)[:100]}")
    
    print(f"\n{'='*50}")
    print(f"IMPORT COMPLETE")
    print(f"  Inserted: {inserted}")
    print(f"  Errors: {errors}")
    print(f"  Total now in Supabase: {inserted + len(existing_emails)}")
    print(f"{'='*50}")
    
    # Write result to file
    result = f"IMPORT RESULT: Inserted {inserted}, Errors {errors}, Skipped dup {skipped_dup}, Skipped no-contact {skipped_no_contact}"
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_result.txt"), 'w') as f:
        f.write(result)

if __name__ == "__main__":
    main()
