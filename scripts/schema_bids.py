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

# Create bids table
cur.execute("""
CREATE TABLE IF NOT EXISTS bids (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    closing_date TIMESTAMP,
    pdf_url TEXT,
    estimated_budget TEXT,
    required_certs TEXT,
    category TEXT,
    scope_summary TEXT,
    created_at TIMESTAMP DEFAULT now()
);
""")
print("Created bids table.")

# Create bid_matches table
cur.execute(f"""
CREATE TABLE IF NOT EXISTS bid_matches (
    id SERIAL PRIMARY KEY,
    bid_id INTEGER REFERENCES bids(id) ON DELETE CASCADE,
    business_id {id_type} REFERENCES contacts_master(id) ON DELETE CASCADE,
    match_score INTEGER,
    outreach_script TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT now()
);
""")
print("Created bid_matches table.")

cur.close()
conn.close()
