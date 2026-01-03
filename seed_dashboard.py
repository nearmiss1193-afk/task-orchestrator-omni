import sqlite3
import datetime
import uuid

# Database Path (adjust if your actual DB is elsewhere, assuming local SQLite for the dash)
DB_PATH = "c:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified\\empire.db"

def seed_dashboard():
    print("🌱 Seeding Dashboard with Initial Data...")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Ensure Tables Exist (simplified schema for display)
    c.execute('''CREATE TABLE IF NOT EXISTS leads 
                 (id TEXT PRIMARY KEY, name TEXT, email TEXT, status TEXT, created_at DATETIME)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns 
                 (id TEXT PRIMARY KEY, name TEXT, status TEXT, leads_count INTEGER)''')

    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (id TEXT PRIMARY KEY, lead_id TEXT, summary TEXT, last_message DATETIME)''')

    # 2. Insert Dummy "Growth Engine" Campaign
    try:
        c.execute("INSERT INTO campaigns (id, name, status, leads_count) VALUES (?, ?, ?, ?)",
                  (str(uuid.uuid4()), "Veo Visionary Ads (Q1)", "Active", 12))
        c.execute("INSERT INTO campaigns (id, name, status, leads_count) VALUES (?, ?, ?, ?)",
                  (str(uuid.uuid4()), "Office Automation Outreach", "Paused", 45))
    except sqlite3.IntegrityError:
        pass # Already exists

    # 3. Insert Recent "Leads"
    leads = [
        ("David Miller", "david.m@example.com", "New"),
        ("Sarah Connor", "sarah@skynet.net", "Qualified"),
        ("Mike Ross", "mike@pearson.com", "Closed-Won")
    ]
    
    for name, email, status in leads:
        try:
            c.execute("INSERT INTO leads (id, name, email, status, created_at) VALUES (?, ?, ?, ?, ?)",
                      (str(uuid.uuid4()), name, email, status, datetime.datetime.now()))
        except:
            pass

    conn.commit()
    conn.close()
    print("✅ Dashboard Seeded: 2 Campaigns, 3 Leads added.")

if __name__ == "__main__":
    seed_dashboard()
