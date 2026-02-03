import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env")
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    # Force update the one lead the cloud can see
    lead_id = "c086f2ce-72f5-4f9f-b414-e0432908c6bc"
    user_phone = "+13529368152"
    
    cur.execute("UPDATE contacts_master SET phone = %s WHERE id = %s", (user_phone, lead_id))
    conn.commit()
    print(f"✅ Lead {lead_id} updated with phone {user_phone}")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
