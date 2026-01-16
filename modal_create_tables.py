"""
Modal Cloud Job - Create Supabase Memory Tables
One-time run to create contacts, memories, playbook_updates tables
"""
import modal

app = modal.App("create-supabase-tables")

image = modal.Image.debian_slim(python_version="3.11").pip_install("psycopg2-binary")

# Supabase PostgreSQL - Direct connection string
# Format: postgresql://user:password@host:port/database
DATABASE_URL = "postgresql://postgres.rzcpfwkygdvoshtwxncs:AISarah2024Omni!@aws-0-us-east-1.pooler.supabase.com:5432/postgres"


SCHEMA_SQL = """
-- CONTACTS: One row per phone/email (master contact record)
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255),
    name VARCHAR(255),
    pipeline_stage VARCHAR(50) DEFAULT 'new',
    tags TEXT[] DEFAULT '{}',
    timezone VARCHAR(50),
    last_interaction_at TIMESTAMPTZ,
    interaction_count INTEGER DEFAULT 0,
    summary_1_sentence TEXT,
    lead_fit VARCHAR(20),
    sentiment VARCHAR(20),
    last_booking_at TIMESTAMPTZ,
    booking_link_sent BOOLEAN DEFAULT FALSE,
    opt_out BOOLEAN DEFAULT FALSE,
    opt_out_at TIMESTAMPTZ
);

-- MEMORIES: Extracted facts/preferences/constraints/traits
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    contact_id UUID,
    phone VARCHAR(20),
    memory_type VARCHAR(20) NOT NULL,
    key VARCHAR(100) NOT NULL,
    value TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    source_interaction_id UUID,
    priority INTEGER DEFAULT 5
);

-- PLAYBOOK_UPDATES: Learned improvements (for approval)
CREATE TABLE IF NOT EXISTS playbook_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    update_type VARCHAR(50),
    where_applies VARCHAR(50),
    change_description TEXT NOT NULL,
    reason TEXT,
    risk_level VARCHAR(10),
    variant_a TEXT,
    variant_b TEXT,
    success_metric VARCHAR(50),
    sample_size INTEGER,
    status VARCHAR(20) DEFAULT 'proposed',
    approved_by VARCHAR(100),
    approved_at TIMESTAMPTZ,
    results JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_memories_contact_id ON memories(contact_id);
CREATE INDEX IF NOT EXISTS idx_memories_phone ON memories(phone);
"""


@app.function(image=image, timeout=120)
def create_tables():
    """Create all memory system tables in Supabase"""
    import psycopg2
    
    print("=" * 60)
    print("CREATING SUPABASE MEMORY TABLES")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Execute schema
        cur.execute(SCHEMA_SQL)
        
        print("[OK] Tables created successfully!")
        
        # Verify tables exist
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('contacts', 'memories', 'playbook_updates')
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"[VERIFIED] Tables: {tables}")
        
        cur.close()
        conn.close()
        
        return {"status": "success", "tables": tables}
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return {"status": "error", "error": str(e)}


@app.local_entrypoint()
def main():
    result = create_tables.remote()
    print(f"\nResult: {result}")


if __name__ == "__main__":
    print("Deploy and run with:")
    print("  modal run modal_create_tables.py")
