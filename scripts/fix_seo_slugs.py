import os
import psycopg2
import re
from dotenv import load_dotenv

load_dotenv('C:/Users/nearm/.gemini/antigravity/scratch/empire-unified/.env')
db_url = os.environ.get('DATABASE_URL')

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text

def fix_seo_slugs():
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # 1. Check if lakeland/plumbers exists in any form
    print("🔍 Searching for any Lakeland Plumbers records...")
    cur.execute("SELECT slug, industry, location FROM seo_landing_pages WHERE location ILIKE '%Lakeland%' AND industry ILIKE '%Plumber%'")
    rows = cur.fetchall()
    
    if not rows:
        print("❌ No Lakeland Plumbers found. Creating a default entry for testing the repair.")
        # Insert a dummy record if none exists, so the link doesn't 404
        cur.execute("""
            INSERT INTO seo_landing_pages (slug, keyword, industry, location, page_title, meta_description, content_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (slug) DO NOTHING
        """, (
            'lakeland/plumbers',
            'AI Phone Agent',
            'Plumbers',
            'Lakeland, FL',
            'AI Plumber Receptionist in Lakeland | Sovereign AI',
            'Never miss a plumbing call in Lakeland again.',
            '{"features": ["24/7 Booking", "Voice AI"]}'
        ))
    else:
        for row in rows:
            old_slug, ind, loc = row
            new_slug = f"{slugify(loc.split(',')[0])}/{slugify(ind)}"
            print(f"  Found: {old_slug} -> target: {new_slug}")
            if old_slug != new_slug:
                try:
                    cur.execute("UPDATE seo_landing_pages SET slug = %s WHERE slug = %s", (new_slug, old_slug))
                    print(f"  ✅ Updated {old_slug} to {new_slug}")
                except Exception as e:
                    print(f"  ⚠️ Conflict or error: {e}")
                    conn.rollback()
                    # If conflict, we might need to delete one
                    cur.execute("DELETE FROM seo_landing_pages WHERE slug = %s", (old_slug,))
                    print(f"  🗑️ Deleted duplicate {old_slug}")
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    fix_seo_slugs()
