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

def reslug_database():
    print("🚀 Starting Database Re-slugging for Clean URLs...")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    cur.execute("SELECT slug, industry, location FROM seo_landing_pages")
    rows = cur.fetchall()
    
    count = 0
    for row in rows:
        old_slug, industry, location = row
        
        # Create new clean slug: location/industry
        # Example: Tampa, FL -> tampa-fl
        city = location.split(',')[0].strip()
        new_slug = f"{slugify(city)}/{slugify(industry)}"
        
        if old_slug != new_slug:
            try:
                # We need to use a temporary update because slug is PRIMARY KEY
                # Actually, we can just update it.
                cur.execute("""
                    UPDATE seo_landing_pages
                    SET slug = %s
                    WHERE slug = %s
                """, (new_slug, old_slug))
                count += 1
            except Exception as e:
                print(f"Error updating {old_slug} to {new_slug}: {e}")
                conn.rollback()
                continue
        
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Re-slugging complete. Updated {count} records.")

if __name__ == '__main__':
    reslug_database()
