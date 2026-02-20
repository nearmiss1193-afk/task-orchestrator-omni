"""
Import 1000 Jacksonville leads from CSV into contacts_master.
Schema-matched columns: company_name, email, phone, full_name, niche, status, lead_source, ghl_contact_id, source, funnel_stage, total_touches, lead_score
"""
import sys, csv, re
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

CSV_PATH = r"C:\Users\nearm\Downloads\JACKSONVILLE_1000_LEADS.csv"
LEAD_SOURCE = "manus_jacksonville"
BATCH_SIZE = 50

def clean_phone(phone_str):
    if not phone_str:
        return None
    cleaned = re.sub(r'\D', '', str(phone_str))
    if len(cleaned) < 10:
        return None
    if len(cleaned) == 10:
        return f"+1{cleaned}"
    if len(cleaned) == 11 and cleaned.startswith("1"):
        return f"+{cleaned}"
    return f"+1{cleaned[-10:]}"

def main():
    sb = get_supabase()
    
    # Read CSV
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"CSV rows read: {len(rows)}")
    
    # Get existing emails to deduplicate
    existing_emails_resp = sb.table("contacts_master").select("email").not_.is_("email", "null").execute()
    existing_emails = set(r["email"].lower() for r in existing_emails_resp.data if r.get("email"))
    print(f"Existing emails in DB: {len(existing_emails)}")
    
    to_insert = []
    skipped_dupes = 0
    skipped_no_email = 0
    
    for row in rows:
        email = row.get("Email", "").strip()
        if not email:
            skipped_no_email += 1
            continue
        
        if email.lower() in existing_emails:
            skipped_dupes += 1
            continue
        
        phone = clean_phone(row.get("Phone", ""))
        owner_name = row.get("Owner Name", "").strip()
        full_name = owner_name if owner_name and owner_name != "Owner" else ""
        
        record = {
            "company_name": row.get("Business Name", "").strip(),
            "email": email,
            "phone": phone,
            "full_name": full_name,
            "niche": row.get("Category", "").strip(),
            "status": "new",
            "lead_source": LEAD_SOURCE,
            "source": LEAD_SOURCE,
            "funnel_stage": "new",
            "lead_score": 0,
            "total_touches": 0,
            "ghl_contact_id": f"SCRAPED_{hash(email) & 0xFFFFFFFF:08x}",
        }
        
        to_insert.append(record)
        existing_emails.add(email.lower())
    
    print(f"\nReady to insert: {len(to_insert)}")
    print(f"Skipped (duplicate email): {skipped_dupes}")
    print(f"Skipped (no email): {skipped_no_email}")
    
    if not to_insert:
        print("Nothing to insert!")
        return
    
    # Batch insert
    inserted = 0
    failed = 0
    for i in range(0, len(to_insert), BATCH_SIZE):
        batch = to_insert[i:i + BATCH_SIZE]
        try:
            result = sb.table("contacts_master").insert(batch).execute()
            inserted += len(result.data)
            pct = round((i + len(batch)) / len(to_insert) * 100)
            print(f"  Batch {i // BATCH_SIZE + 1}: +{len(result.data)} rows ({pct}%)")
        except Exception as e:
            failed += len(batch)
            print(f"  Batch {i // BATCH_SIZE + 1} FAILED: {e}")
    
    print(f"\n{'='*50}")
    print(f"IMPORT COMPLETE")
    print(f"  Inserted: {inserted}")
    print(f"  Failed:   {failed}")
    print(f"  Skipped:  {skipped_dupes + skipped_no_email}")
    
    # Verify
    total = sb.table("contacts_master").select("*", count="exact").limit(0).execute()
    jax = sb.table("contacts_master").select("*", count="exact").eq("lead_source", LEAD_SOURCE).limit(0).execute()
    new_leads = sb.table("contacts_master").select("*", count="exact").eq("status", "new").limit(0).execute()
    print(f"\nPost-import stats:")
    print(f"  Total contacts_master: {total.count}")
    print(f"  Jacksonville leads:    {jax.count}")
    print(f"  Contactable (new):     {new_leads.count}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
