import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env")
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    # Find column names first
    cur.execute("SELECT * FROM contacts_master LIMIT 1")
    colnames = [desc[0] for desc in cur.description]
    print(f"📋 Columns: {colnames}")
    
    # Check for both IDs in the whole table (cast to text)
    id1 = "uFYcZA7Zk6EcBze5B4oH"
    id2 = "RnK4OjX0oDcqtWw0VyLr"
    
    # We'll just search all text columns for simplicity
    search_query = "SELECT count(*) FROM contacts_master WHERE cast(contacts_master as text) LIKE %s"
    
    cur.execute(search_query, (f"%{id1}%",))
    count1 = cur.fetchone()[0]
    
    cur.execute(search_query, (f"%{id2}%",))
    count2 = cur.fetchone()[0]
    
    print(f"📊 SEARCH for uFYc (Master ID): {count1}")
    print(f"📊 SEARCH for RnK4 (Env ID): {count2}")
    
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
