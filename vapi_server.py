from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import json
try:
    import resend
except ImportError:
    resend = None

app = FastAPI()

# Input Resend API Key securely environment variable
RESEND_API_KEY = os.environ.get("RESEND_API_KEY") 
if RESEND_API_KEY and resend:
    resend.api_key = RESEND_API_KEY

# Database Setup
def get_db_path():
    if os.environ.get("VERCEL"):
        return "/tmp/empire.db"
    return "empire.db"

def init_db():
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS leads
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      phone TEXT, 
                      email TEXT, 
                      name TEXT,
                      source TEXT, 
                      metadata TEXT, 
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS interactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      lead_phone TEXT, 
                      type TEXT, 
                      summary TEXT, 
                      transcript TEXT, 
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ DB Init Warning: {e}")

# Initialize on startup (best effort)
init_db()

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    try:
        data = await request.json()
        message = data.get('message', {})
        type = message.get('type', 'unknown')
        print(f"📡 Webhook: {type}")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/reserve")
async def reserve_plan(request: Request):
    try:
        data = await request.json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        plan = data.get('plan')
        
        # 1. Save to DB
    conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        meta = json.dumps({"plan": plan})
        c.execute("INSERT INTO leads (phone, email, name, source, metadata) VALUES (?, ?, ?, ?, ?)",
                  (phone, email, name, "web_reservation", meta))
        conn.commit()
        conn.close()
        
        # 2. Send Email via Resend
        if RESEND_API_KEY and resend:
            try:
                r = resend.Emails.send({
                  "from": "onboarding@resend.dev",
                  "to": email,
                  "subject": f"Empire HVAC: Your {plan} Plan is Reserved",
                  "html": f"<h1>Welcome to the Empire, {name}!</h1><p>We have reserved your <strong>{plan}</strong> plan.</p>"
                })
                print(f"📧 Email Sent: {r}")
            except Exception as email_error:
                print(f"❌ Email Error: {email_error}")
        else:
             print("⚠️ No RESEND_API_KEY found or resend module missing. Email skipped.")
        
        return {"status": "success", "message": "Reservation Confirmed"}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/stats")
def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM leads")
    leads = c.fetchone()[0]
    conn.close()
    return {"leads": leads, "revenue": leads * 99, "calls": 0, "reservations": leads}

@app.get("/api/leads")
def get_leads():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT 50")
    leads = [dict(row) for row in c.fetchall()]
    conn.close()
    return leads

@app.get("/")
def home():
    return {"status": "Sovereign Cloud Active 🟢"}
