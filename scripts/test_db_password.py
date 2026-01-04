
import os
import pg8000.native
import ssl
from urllib.parse import urlparse

# Candidate Passwords
passwords = [
    "1vonN2C5s0jmiIjbn", # Current .env (Failing)
    "Inez11752990@",     # GHL Password (Common reuse)
    "postgres",          # Default
    "root"
]

host = "db.rzcpfwkygdvoshtwxncs.supabase.co"
user = "postgres"
db_name = "postgres"

def test_connection():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    for p in passwords:
        print(f"🔑 Testing Password: {p[:4]}***...")
        try:
            con = pg8000.native.Connection(
                user=user,
                password=p,
                host=host,
                port=5432,
                database=db_name,
                ssl_context=ssl_context,
                timeout=5
            )
            con.run("SELECT 1")
            print(f"✅ SUCCESS! Valid Password: {p}")
            con.close()
            return
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_connection()
