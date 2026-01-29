import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env")
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    # Check one lead's metadata to find the location ID
    cur.execute("SELECT metadata FROM contacts_master WHERE metadata IS NOT NULL LIMIT 1")
    row = cur.fetchone()
    if row:
        import json
        metadata = row[0]
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        location_id = metadata.get("locationId")
        print(f"✅ FOUND LOCATION_ID IN DATABASE: {location_id}")
    else:
        print("⚠️ No metadata found to extract Location ID.")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
