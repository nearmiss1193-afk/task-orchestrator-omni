import os
from dotenv import load_dotenv
import psycopg2
import json

# Load env
load_dotenv('C:/Users/nearm/.gemini/antigravity/scratch/empire-unified/.env')
db_url = os.environ.get('DATABASE_URL')

if not db_url:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

def parse_slug(slug):
    # slug looks like: "ai-phone-agent-for-cleaning-services-in-bradenton"
    try:
        parts = slug.split("-for-")
        if len(parts) != 2:
            return None, None, None
        
        prefix_slug = parts[0] # "ai-phone-agent"
        
        sub_parts = parts[1].split("-in-")
        if len(sub_parts) != 2:
            return None, None, None
            
        industry_slug = sub_parts[0] # "cleaning-services"
        city_slug = sub_parts[1] # "bradenton"
        
        # Format for readability
        keyword = prefix_slug.replace('-', ' ').title()
        # Edge cases for AI
        keyword = keyword.replace('Ai ', 'AI ')
        
        industry = industry_slug.replace('-', ' ').title()
        if industry.lower() == 'hvac':
            industry = 'HVAC'
            
        city = city_slug.replace('-', ' ').title()
        
        # Florida assumed based on user context
        location = f"{city}, FL"
        
        return keyword, industry, location
    except Exception as e:
        print(f"Failed to parse {slug}: {e}")
        return None, None, None

def migrate():
    print("🚀 Connecting to Supabase Postgres...")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # 1. Create Table
    print("📦 Ensuring 'seo_landing_pages' table exists...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seo_landing_pages (
            slug TEXT PRIMARY KEY,
            keyword TEXT,
            industry TEXT,
            location TEXT,
            page_title TEXT,
            meta_description TEXT,
            content_data JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    conn.commit()
    
    # 2. Read Local Routes
    routes_path = 'C:/Users/nearm/.gemini/antigravity/scratch/empire-unified/apps/portal/src/app/dashboard/seo_routes.json'
    if not os.path.exists(routes_path):
        print(f"❌ Could not find {routes_path}")
        return
        
    with open(routes_path, 'r') as f:
        routes = json.load(f)
        
    print(f"🔍 Found {len(routes)} local SEO routes. Parsing and inserting...")
    
    inserted = 0
    for route in routes:
        slug = route.strip('/')
        
        # Ignore non-SEO routes if any slipped in
        if 'for' not in slug or 'in' not in slug:
            continue
            
        keyword, industry, location = parse_slug(slug)
        if not keyword:
            continue
        
        title = f"{keyword} for {industry} in {location} | Sovereign Empire AI"
        desc = f"Looking for an {keyword.lower()} for {industry.lower()}? We provide 24/7 automated booking and lead capture specifically tuned for contractors in {location}."
        
        # Default content data structure
        content = json.dumps({
            "hero_headline": f"Never Miss a Job in {location} Again",
            "hero_subheadline": f"The #1 {keyword} built exclusively for {industry}.",
            "features": [
                "24/7 Inbound Call Answering",
                "Automated Calendar Booking",
                "Lead Qualification & FAQ",
                "SMS Follow-up Workflows"
            ]
        })
        
        # Upsert
        cur.execute("""
            INSERT INTO seo_landing_pages (slug, keyword, industry, location, page_title, meta_description, content_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (slug) DO UPDATE SET
                keyword = EXCLUDED.keyword,
                industry = EXCLUDED.industry,
                location = EXCLUDED.location,
                page_title = EXCLUDED.page_title,
                meta_description = EXCLUDED.meta_description,
                content_data = COALESCE(seo_landing_pages.content_data, EXCLUDED.content_data),
                updated_at = NOW();
        """, (slug, keyword, industry, location, title, desc, content))
        
        inserted += 1
        if inserted % 100 == 0:
            print(f"   ... migrated {inserted} routes")
            
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✅ Migration complete! {inserted} programmatic SEO pages stored securely in Supabase.")

if __name__ == '__main__':
    migrate()
