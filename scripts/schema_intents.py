import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Connect to the database
conn = psycopg2.connect(os.environ["DATABASE_URL"])
conn.autocommit = True
cur = conn.cursor()

# Get contacts_master id type
cur.execute("SELECT data_type FROM information_schema.columns WHERE table_name = 'contacts_master' AND column_name = 'id';")
res = cur.fetchone()
id_type = res[0] if res else "INTEGER"
print(f"contacts_master.id is of type: {id_type}")

# Create estate_sales table
cur.execute("""
CREATE TABLE IF NOT EXISTS estate_sales (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    event_date TEXT,
    address TEXT,
    url TEXT,
    sale_type TEXT,
    intent_classification TEXT, 
    description_summary TEXT,
    created_at TIMESTAMP DEFAULT now()
);
""")
print("Created estate_sales table.")

# Create estate_matches table
cur.execute(f"""
CREATE TABLE IF NOT EXISTS estate_matches (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER REFERENCES estate_sales(id) ON DELETE CASCADE,
    business_id {id_type} REFERENCES contacts_master(id) ON DELETE CASCADE,
    match_score INTEGER,
    outreach_script TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT now()
);
""")
print("Created estate_matches table.")

cur.close()
conn.close()
