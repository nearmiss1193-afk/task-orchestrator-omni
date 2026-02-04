import os
import urllib.parse
import ssl
import pg8000.native
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def execute_sql_file(file_path):
    print(f"🚀 Executing {file_path}...")
    con = get_db_connection()
    if not con:
        return
    
    try:
        with open(file_path, 'r') as f:
            sql_commands = f.read()
        
        # Split by semicolon if needed or run as one block
        # pg8000.native.Connection.run can run multiple commands separated by semicolons if they don't depend on each other within the transaction in complex ways
        con.run(sql_commands)
        con.close()
        print("✅ SQL Executed Successfully.")
    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    execute_sql_file("sql/create_embeds_table.sql")
