"""
Sarah Memory System - Database Schema Setup
Creates contacts, interactions, memories, playbook_updates tables in Supabase
"""
import requests

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

# SQL to create the memory system tables
SCHEMA_SQL = """
-- CONTACTS: One row per phone/email (master contact record)
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Identity
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255),
    name VARCHAR(255),
    
    -- Classification
    pipeline_stage VARCHAR(50) DEFAULT 'new', -- new, qualified, booked, customer, churned
    tags TEXT[] DEFAULT '{}',
    timezone VARCHAR(50),
    
    -- Summary (updated after each interaction)
    last_interaction_at TIMESTAMPTZ,
    interaction_count INTEGER DEFAULT 0,
    summary_1_sentence TEXT,
    lead_fit VARCHAR(20), -- qualified, not_fit, unknown
    sentiment VARCHAR(20), -- calm, urgent, frustrated
    
    -- Booking
    last_booking_at TIMESTAMPTZ,
    booking_link_sent BOOLEAN DEFAULT FALSE,
    
    -- Opt out
    opt_out BOOLEAN DEFAULT FALSE,
    opt_out_at TIMESTAMPTZ
);

-- INTERACTIONS: Every inbound/outbound call/text
CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Link to contact
    contact_id UUID REFERENCES contacts(id),
    phone VARCHAR(20),
    
    -- Interaction details
    channel VARCHAR(10) NOT NULL, -- sms, call
    direction VARCHAR(10) NOT NULL, -- inbound, outbound
    
    -- Content
    user_message TEXT,
    ai_response TEXT,
    full_transcript TEXT,
    
    -- Classification
    intent VARCHAR(50), -- pricing, book, support, complaint, other
    sentiment VARCHAR(20),
    outcome VARCHAR(50), -- booked, send_link, follow_up, escalate, close
    
    -- Booking
    booking_requested TIMESTAMPTZ,
    booking_confirmed TIMESTAMPTZ,
    
    -- Escalation
    escalated BOOLEAN DEFAULT FALSE,
    escalation_reason TEXT,
    escalation_urgency VARCHAR(10) -- low, med, high
);

-- MEMORIES: Extracted facts/preferences/constraints/traits
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Link to contact
    contact_id UUID REFERENCES contacts(id),
    phone VARCHAR(20),
    
    -- Memory content
    memory_type VARCHAR(20) NOT NULL, -- fact, preference, constraint, trait, objection, open_loop
    key VARCHAR(100) NOT NULL,
    value TEXT NOT NULL,
    
    -- Confidence
    confidence FLOAT DEFAULT 1.0, -- 0.0 to 1.0
    
    -- Source
    source_interaction_id UUID REFERENCES interactions(id),
    
    -- Priority for injection
    priority INTEGER DEFAULT 5 -- 1=highest, 10=lowest
);

-- PLAYBOOK_UPDATES: Learned improvements (for approval)
CREATE TABLE IF NOT EXISTS playbook_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Update details
    update_type VARCHAR(50), -- script_change, kb_gap, experiment
    where_applies VARCHAR(50), -- sms_opening, pricing_answer, booking_cta, call_flow
    
    -- Content
    change_description TEXT NOT NULL,
    reason TEXT,
    risk_level VARCHAR(10), -- low, med, high
    
    -- For experiments
    variant_a TEXT,
    variant_b TEXT,
    success_metric VARCHAR(50),
    sample_size INTEGER,
    
    -- Status
    status VARCHAR(20) DEFAULT 'proposed', -- proposed, approved, rejected, tested
    approved_by VARCHAR(100),
    approved_at TIMESTAMPTZ,
    
    -- Results
    results JSONB
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_interactions_contact_id ON interactions(contact_id);
CREATE INDEX IF NOT EXISTS idx_interactions_phone ON interactions(phone);
CREATE INDEX IF NOT EXISTS idx_memories_contact_id ON memories(contact_id);
CREATE INDEX IF NOT EXISTS idx_memories_phone ON memories(phone);
"""

def create_tables_via_rest():
    """Create tables using Supabase REST API (sql function)"""
    print("=" * 60)
    print("SARAH MEMORY SYSTEM - DATABASE SETUP")
    print("=" * 60)
    
    # Note: Supabase REST API doesn't directly execute raw SQL
    # We need to use the SQL editor in dashboard or use psycopg2
    # For now, let's check if tables exist and create sample structure
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Check if contacts table exists
    print("\n[1] Checking contacts table...")
    r = requests.get(f"{SUPABASE_URL}/rest/v1/contacts?limit=1", headers=headers)
    if r.status_code == 200:
        print("  contacts table EXISTS")
    else:
        print(f"  contacts table NOT FOUND (status {r.status_code})")
        print("  -> Need to create via Supabase SQL Editor")
    
    # Check if interactions table exists
    print("\n[2] Checking interactions table...")
    r = requests.get(f"{SUPABASE_URL}/rest/v1/interactions?limit=1", headers=headers)
    if r.status_code == 200:
        print("  interactions table EXISTS")
    else:
        print(f"  interactions table NOT FOUND (status {r.status_code})")
    
    # Check if memories table exists
    print("\n[3] Checking memories table...")
    r = requests.get(f"{SUPABASE_URL}/rest/v1/memories?limit=1", headers=headers)
    if r.status_code == 200:
        print("  memories table EXISTS")
    else:
        print(f"  memories table NOT FOUND (status {r.status_code})")
    
    # Check if playbook_updates table exists
    print("\n[4] Checking playbook_updates table...")
    r = requests.get(f"{SUPABASE_URL}/rest/v1/playbook_updates?limit=1", headers=headers)
    if r.status_code == 200:
        print("  playbook_updates table EXISTS")
    else:
        print(f"  playbook_updates table NOT FOUND (status {r.status_code})")
    
    print("\n" + "=" * 60)
    print("SQL SCHEMA (run in Supabase SQL Editor if tables missing):")
    print("=" * 60)
    print(SCHEMA_SQL)

if __name__ == "__main__":
    create_tables_via_rest()
