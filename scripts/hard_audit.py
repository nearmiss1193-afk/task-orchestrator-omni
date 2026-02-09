import pg8000.native
import ssl
import urllib.parse

def run_hard_audit():
    db_url = "postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres"
    print("📋 EMPIRE HARD AUDIT\n" + "="*50)
    
    try:
        result = urllib.parse.urlparse(db_url)
        username = result.username
        password = urllib.parse.unquote(result.password)
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
        
        # 1. Outreach Counts
        print("\n📊 STATUS COUNTS:")
        rows = con.run("SELECT status, count(*) FROM contacts_master GROUP BY status")
        for row in rows:
            print(f" - {row[0]}: {row[1]}")
            
        # 2. Contacted Leads
        print("\n📡 CONTACTED LEADS (Email/SMS):")
        rows = con.run("SELECT full_name, email, phone, status FROM contacts_master WHERE status IN ('outreach_sent', 'outreach_dispatched', 'calling_initiated') ORDER BY status DESC LIMIT 50")
        if rows:
            for row in rows:
                print(f" - {row[3]:<20} | {row[0]:<25} | {row[1] or row[2]}")
        else:
            print(" ⚠️ No leads found with outreach status.")
            
        # 3. Dan's Memory
        print("\n🧠 DAN'S MEMORY CHECK (+13529368152):")
        rows = con.run("SELECT customer_name, context_summary FROM customer_memory WHERE phone_number = '+13529368152'")
        if rows:
            print(f" - Name: {rows[0][0]}")
            print(f" - Context: {rows[0][1]}")
        else:
            print(" ❌ No record found.")
            
        con.close()
    except Exception as e:
        print(f"❌ Hard Audit Error: {e}")

if __name__ == "__main__":
    run_hard_audit()
