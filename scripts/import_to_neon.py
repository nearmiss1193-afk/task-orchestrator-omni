"""
Bulk import lakeland_master_5500.csv into Neon DB (businesses table) for LakelandFinds.com.
Deduplicates against existing records by name+address.
"""
import csv, json, os, re, sys

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    os.system("pip install psycopg2-binary")
    import psycopg2
    from psycopg2.extras import execute_values

# Neon connection
DATABASE_URL = "postgresql://neondb_owner:npg_1EndsBLzF8Kp@ep-small-hall-aefqgxkp-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"

def parse_city_state(address):
    """Extract city and state from address like 'xxx, Lakeland, FL 33801, USA'"""
    city = "Lakeland"
    state = "FL"
    if address:
        parts = [p.strip() for p in address.split(",")]
        # Try to find city, state from address pattern
        for i, part in enumerate(parts):
            m = re.match(r'^([A-Z]{2})\s+\d{5}', part)
            if m:
                state = m.group(1)
                if i > 0:
                    city = parts[i-1].strip()
                break
    return city, state

def main():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lakeland_master_5500.csv')
    
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"CSV loaded: {len(rows)} businesses")
    
    # Connect to Neon
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()
    
    # Get existing name+address combos to avoid dupes
    cur.execute("SELECT name, address FROM businesses")
    existing = set()
    for row in cur.fetchall():
        key = f"{(row[0] or '').strip().lower()}|{(row[1] or '').strip().lower()}"
        existing.add(key)
    print(f"Existing in DB: {len(existing)} businesses")
    
    # Filter new businesses
    new_rows = []
    for r in rows:
        name = (r.get('name','') or '').strip()
        address = (r.get('address','') or '').strip()
        key = f"{name.lower()}|{address.lower()}"
        if key not in existing and name:
            new_rows.append(r)
            existing.add(key)  # Prevent intra-batch dupes
    
    print(f"New to insert: {len(new_rows)}")
    
    if not new_rows:
        print("Nothing new to insert!")
        return
    
    # Prepare batch inserts
    batch_size = 100
    inserted = 0
    errors = 0
    
    for i in range(0, len(new_rows), batch_size):
        batch = new_rows[i:i+batch_size]
        values = []
        for r in batch:
            name = r.get('name','').strip()
            address = r.get('address','').strip()
            category = r.get('category','').strip() or None
            phone = r.get('phone','').strip() or None
            email = r.get('email','').strip() or None
            website = r.get('website','').strip() or None
            rating_str = r.get('rating','').strip()
            rating = float(rating_str) if rating_str else None
            total_ratings_str = r.get('total_ratings','').strip()
            total_ratings = int(total_ratings_str) if total_ratings_str else None
            
            city, state = parse_city_state(address)
            
            # Build contact_info JSONB
            contact_info = {}
            if phone: contact_info['phone'] = phone
            if email: contact_info['email'] = email
            if website: contact_info['website'] = website
            
            values.append((
                name, address, category, city, state,
                phone, email, website,
                json.dumps(contact_info) if contact_info else None,
                rating, total_ratings
            ))
        
        try:
            execute_values(cur, """
                INSERT INTO businesses (name, address, category, city, state, phone, email, website_url, contact_info, rating, total_ratings)
                VALUES %s
            """, values)
            conn.commit()
            inserted += len(batch)
            if (i + batch_size) % 500 == 0 or i + batch_size >= len(new_rows):
                print(f"  Inserted: {inserted}/{len(new_rows)}")
        except Exception as e:
            conn.rollback()
            errors += len(batch)
            print(f"  ERROR batch {i}: {str(e)[:100]}")
    
    # Final count
    cur.execute("SELECT COUNT(*) FROM businesses")
    total = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    summary = f"""IMPORT COMPLETE:
New inserted: {inserted}
Errors: {errors}
Total in DB: {total}
"""
    print(f"\n{summary}")
    
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'neon_import_result.txt'), 'w') as f:
        f.write(summary)

if __name__ == "__main__":
    main()
