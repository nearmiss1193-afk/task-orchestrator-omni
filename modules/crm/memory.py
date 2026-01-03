import sqlite3
import json
import os
from datetime import datetime

# DB Path
DB_PATH = "empire.db"

def init_db():
    """Initialize the Memory Core database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Leads Table (The Core CRM)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE,
        email TEXT,
        name TEXT,
        status TEXT DEFAULT 'captured',
        source TEXT DEFAULT 'vapi',
        metadata TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Interaction Log (The Memory)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        type TEXT, -- 'call', 'sms', 'web', 'funnel'
        content TEXT,
        transcript TEXT,
        sentiment TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(lead_id) REFERENCES leads(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"🧠 Memory Core Initialized at {DB_PATH}")

def save_lead(phone, email=None, name=None, source='vapi', meta=None):
    """Save or Update a Lead in the Memory Core."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT id FROM leads WHERE phone = ?", (phone,))
    existing = cursor.fetchone()
    
    if existing:
        # Update
        lead_id = existing[0]
        cursor.execute('''
        UPDATE leads SET 
            email = COALESCE(?, email), 
            name = COALESCE(?, name),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (email, name, lead_id))
    else:
        # Insert
        cursor.execute('''
        INSERT INTO leads (phone, email, name, source, metadata)
        VALUES (?, ?, ?, ?, ?)
        ''', (phone, email, name, source, json.dumps(meta or {})))
        lead_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    print(f"🧠 Memory Saved Lead: {phone} (ID: {lead_id})")
    return lead_id

def log_interaction(phone, type, content, transcript=None):
    """Log an interaction for a phone number."""
    lead_id = save_lead(phone) # Ensure lead exists
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO interactions (lead_id, type, content, transcript)
    VALUES (?, ?, ?, ?)
    ''', (lead_id, type, content, transcript))
    conn.commit()
    conn.close()
    print(f"🧠 Memory Logged Interaction: {type} for {phone}")

if __name__ == "__main__":
    init_db()
