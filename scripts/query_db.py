import os
import urllib.parse
import ssl
import pg8000.native
import sys
from dotenv import load_dotenv

load_dotenv() # Load from .env first
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True) # Override with secrets if exists

def get_db_connection():
    try:
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            print("❌ DATABASE_URL not found")
            return None
        
        result = urllib.parse.urlparse(db_url)
        username = result.username
        password = result.password
        host = result.hostname
        port = result.port or 5432
        database = result.path[1:]
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        con = pg8000.native.Connection(
            user=username,
            password=password,
            host=host,
            port=port,
            database=database,
            ssl_context=ssl_context
        )
        return con
    except Exception as e:
        print(f"❌ DB Error: {e}")
        return None

def run_query(query):
    con = get_db_connection()
    if not con:
        return
    
    try:
        print(f"🚀 Running: {query}")
        result = con.run(query)
        if result:
            print("\n📊 RESULTS:")
            print("-" * 40)
            for row in result:
                print(row)
            print("-" * 40)
            print(f"Total rows: {len(result)}")
        else:
            print("✅ Query executed successfully (no rows returned).")
        con.close()
    except Exception as e:
        print(f"❌ Query Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_db.py \"SELECT * FROM table\"")
    else:
        run_query(sys.argv[1])
