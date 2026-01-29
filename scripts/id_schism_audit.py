import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env")
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    # Check for both IDs in the whole table (as strings)
    id1 = "uFYcZA7Zk6EcBze5B4oH"
    id2 = "RnK4OjX0oDcqtWw0VyLr"
    
    cur.execute("SELECT count(*) FROM contacts_master WHERE cast(ghl_id as text) LIKE %s", (f"%{id1}%",))
    count1 = cur.fetchone()[0]
    
    cur.execute("SELECT count(*) FROM contacts_master WHERE cast(ghl_id as text) LIKE %s", (f"%{id2}%",))
    count2 = cur.fetchone()[0]
    
    print(f"📊 LEADS for uFYc (Master ID): {count1}")
    print(f"📊 LEADS for RnK4 (Env ID): {count2}")
    
    # Check metadata similarly if ghl_id search is 0
    if count1 == 0 and count2 == 0:
        cur.execute("SELECT count(*) FROM contacts_master WHERE cast(metadata as text) LIKE %s", (f"%{id1}%",))
        m_count1 = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM contacts_master WHERE cast(metadata as text) LIKE %s", (f"%{id2}%",))
        m_count2 = cur.fetchone()[0]
        print(f"📊 METADATA for uFYc: {m_count1}")
        print(f"📊 METADATA for RnK4: {m_count2}")

    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
