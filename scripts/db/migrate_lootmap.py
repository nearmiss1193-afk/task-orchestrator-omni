import os
import sys
import psycopg2
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, '.')
load_dotenv('.env')
load_dotenv('.env.local')

DB_URL = os.getenv('DATABASE_URL')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print("🚀 Initiating LootMap Storage and Schema Migration...")

# 1. Create Supabase Storage Bucket
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    buckets = supabase.storage.list_buckets()
    bucket_names = [b.name for b in buckets]
    
    if "yard_sale_photos" not in bucket_names:
        print("🪣 Creating 'yard_sale_photos' public bucket...")
        supabase.storage.create_bucket("yard_sale_photos", {"public": True})
        print("✅ Bucket created.")
    else:
        print("✅ Bucket 'yard_sale_photos' already exists.")
except Exception as e:
    print(f"⚠️ Storage Bucket Error: {e}")
    print("Please ensure the service_role key has sufficient permissions or create manually.")


# 2. Create Postgres Tables
sql = """
-- Yard Sales Table
CREATE TABLE IF NOT EXISTS yard_sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_name TEXT,
    address TEXT,
    lat FLOAT,
    lng FLOAT,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    description TEXT,
    boosted BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Yard Sale Photos Table
CREATE TABLE IF NOT EXISTS yard_sale_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sale_id UUID REFERENCES yard_sales(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    ai_tags JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for spatial and tag queries
CREATE INDEX IF NOT EXISTS idx_yard_sales_lat_lng ON yard_sales (lat, lng);
CREATE INDEX IF NOT EXISTS idx_yard_sale_photos_sale_id ON yard_sale_photos (sale_id);
"""

try:
    print("💽 Connecting to Neon Postgres...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    cur.execute(sql)
    conn.commit()
    
    cur.close()
    conn.close()
    print("✅ LootMap tables created successfully.")
except Exception as e:
    print(f"❌ Database error: {e}")
