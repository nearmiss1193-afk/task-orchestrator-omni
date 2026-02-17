import os, csv, json, time
from datetime import datetime, timezone
import modal

# Re-use the existing image configuration from core engine
from core.engine import app, image, VAULT

@app.function(
    image=image,
    secrets=[VAULT],
    timeout=600
)
def run_ingestion_batch(batch_size: int = 50):
    """
    Worker to port businesses from CSV to:
    1. Supabase (contacts_master) for outreach - uses DATABASE_URL
    2. Neon (businesses) for the directory site - uses NEON_DATABASE_URL
    """
    from supabase import create_client
    import psycopg2
    
    # --- 1. System Setup & Credentials ---
    # DATABASE_URL in Modal environment is typically Supabase for this repo
    sb_url = os.environ.get("SUPABASE_URL")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase_db_url = os.environ.get("DATABASE_URL") # This is Supabase
    
    # NEON_DATABASE_URL is for the lakelandfinds.com production site
    neon_url = os.environ.get("NEON_DATABASE_URL")
    
    if not sb_url or not sb_key:
        print("❌ Error: Missing Supabase credentials")
        return {"error": "Missing Supabase credentials"}

    # Initialize Supabase client
    sb = create_client(sb_url, sb_key)
    
    # Initialize Neon connection (Optional - will skip if missing)
    conn = None
    cur = None
    if neon_url:
        try:
            conn = psycopg2.connect(neon_url)
            cur = conn.cursor()
            print("✅ Connected to Neon Directory Database")
        except Exception as e:
            print(f"⚠️ Warning: Failed to connect to Neon: {e}")
            neon_url = None
    else:
        print("ℹ️ Info: NEON_DATABASE_URL not set. Skipping directory updates.")

    # --- 2. Load Data ---
    csv_path = "/root/scripts/lakeland_businesses_enriched.csv"
    if not os.path.exists(csv_path):
        # Fallback for local testing
        csv_path = "scripts/lakeland_businesses_enriched.csv"
        
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV not found at {csv_path}")
        return {"error": f"CSV not found at {csv_path}"}
        
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_businesses = list(reader)
        
    print(f"📂 Loaded {len(all_businesses)} businesses from CSV.")
    
    # --- 3. Deduplication Logic ---
    # A. Neon Existing Place IDs
    existing_neon = set()
    if cur:
        try:
            cur.execute("SELECT place_id FROM businesses WHERE place_id IS NOT NULL")
            existing_neon = set(r[0] for r in cur.fetchall())
        except Exception as e:
            print(f"⚠️ Warning: Could not fetch existing Neon records: {e}")
            # Ensure table exists? Skip for now to keep it slim
    
    # B. Supabase Existing Emails
    existing_sb_emails = set()
    try:
        offset = 0
        while True:
            res = sb.table("contacts_master").select("email").range(offset, offset + 999).execute()
            for r in res.data:
                if r.get('email'): 
                    existing_sb_emails.add(r['email'].lower().strip())
            if len(res.data) < 1000: break
            offset += 1000
    except Exception as e:
        print(f"❌ Error fetching Supabase emails: {e}")
        return {"error": f"Supabase sync failed: {e}"}
        
    print(f"🔍 Current State: Neon={len(existing_neon)}, SupabaseEmails={len(existing_sb_emails)}")
    
    # --- 4. Processing Loop ---
    imported_neon = 0
    imported_sb = 0
    
    for biz in all_businesses:
        # Finish when we hit batch limit for BOTH or run out of data
        if imported_sb >= batch_size and (not neon_url or imported_neon >= batch_size):
            break
            
        place_id = biz.get('place_id', '').strip()
        email = biz.get('email', '').lower().strip()
        name = biz.get('name', 'Unknown Business')
        
        # --- Channel 1: Neon Directory (lakelandfinds.com) ---
        if neon_url and cur and place_id and place_id not in existing_neon and imported_neon < batch_size:
            try:
                cur.execute("""
                    INSERT INTO businesses (name, address, category, phone, website_url, 
                                            city, state, rating, total_ratings, lat, lng, place_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name, biz.get('address', 'Lakeland, FL'), biz.get('category', ''),
                    biz.get('phone', ''), biz.get('website', ''), 'Lakeland', 'FL',
                    float(biz.get('rating', 0) or 0), int(biz.get('total_ratings', 0) or 0),
                    float(biz.get('lat', 0) or 0), float(biz.get('lng', 0) or 0), place_id
                ))
                imported_neon += 1
                existing_neon.add(place_id)
            except Exception as e:
                conn.rollback()
                print(f"  Neon Skip: {name} - {e}")
        
        # --- Channel 2: Supabase Outreach (Sarah AI CRM) ---
        if email and email not in existing_sb_emails and imported_sb < batch_size:
            # Priority logic: fewer reviews = higher need for outreach
            total_ratings = int(biz.get('total_ratings', 0) or 0)
            priority = "high" if total_ratings < 10 else "medium" if total_ratings < 30 else "low"
            
            first_name = name.split()[0] if name else 'there'
            
            # Map enriched data to ai_strategy since 'notes' column is missing
            metadata = {
                "priority": priority,
                "google_rating": float(biz.get('rating', 0) or 0),
                "total_reviews": total_ratings,
                "address": biz.get('address', ''),
                "place_id": place_id,
                "imported_at": datetime.now(timezone.utc).isoformat(),
                "import_type": "automated_background"
            }
            
            lead = {
                "full_name": first_name,
                "company_name": name,
                "email": email,
                "phone": biz.get('phone', ''),
                "website_url": biz.get('website', ''),
                "niche": biz.get('category', 'Local Business'),
                "status": "new",
                "source": "lakeland_finds", 
                "lead_source": "lakeland_finds_directory",
                "ghl_contact_id": f"imported_{place_id[:30] if place_id else int(time.time())}", # Mandatory non-null
                "ai_strategy": json.dumps(metadata) # Using ai_strategy as the metadata bucket
            }
            try:
                sb.table("contacts_master").insert(lead).execute()
                imported_sb += 1
                existing_sb_emails.add(email)
            except Exception as e:
                print(f"  SB Skip: {name} - {e}")

    # Commit any pending Neon changes
    if conn:
        conn.commit()
        cur.close()
        conn.close()
    
    print(f"🚀 Batch Complete. Neon: +{imported_neon}, Supabase: +{imported_sb}")
    return {"neon": imported_neon, "sb": imported_sb}

if __name__ == "__main__":
    with app.run():
        run_ingestion_batch.remote(batch_size=10)
