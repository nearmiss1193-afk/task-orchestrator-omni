import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def find_table():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # Check all schemas for this table
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name = 'outbound_touches'")
        results = cur.fetchall()
        print(f"OUTBOUND_TOUCHES LOCATIONS: {results}")
        
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name = 'contacts_master'")
        results = cur.fetchall()
        print(f"CONTACTS_MASTER LOCATIONS: {results}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_table()
