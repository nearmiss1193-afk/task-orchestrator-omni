
import os
import pg8000.native
import ssl
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def setup_db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL missing.")
        return

    print("🔌 Connecting to Database...")
    try:
        result = urlparse(db_url)
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
        
        print("🛠️ Creating 'commands' table...")
        con.run("""
            CREATE TABLE IF NOT EXISTS commands (
                id SERIAL PRIMARY KEY,
                command TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Table 'commands' ready.")
        con.close()
        
    except Exception as e:
        print(f"❌ DB Error: {e}")

if __name__ == "__main__":
    setup_db()
