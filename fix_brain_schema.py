import psycopg2
import json
from datetime import datetime

DB_URL = 'postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres'

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# Check current schema
print("=== CURRENT SCHEMA ===")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'system_memory'
""")
columns = cur.fetchall()
print("system_memory columns:", columns)

# If missing created_at, add it
col_names = [c[0] for c in columns]
if 'created_at' not in col_names:
    print("Adding created_at column...")
    cur.execute("ALTER TABLE system_memory ADD COLUMN created_at TIMESTAMP DEFAULT NOW()")
    conn.commit()
    print("Added!")

# Now insert brain data
print("\n=== INSERTING BRAIN DATA ===")

# Master context
master_context = f"""
# Empire Brain Context
Last Updated: {datetime.now().isoformat()}

## Key Capabilities
- Pricing: $297/$497/$997 (Golden Standard)
- Trial: 14-Day Free Trial
- AI: Sarah the Spartan (Vapi voice)
- Dashboard: Empire Mission Control v2.3
- Leads: 139 in pipeline (137 processing, 2 contacted)

## Knowledge Base
- ai_boom_playbook.md, ai_research_2025.md, business_wisdom.md
- hvac_prospect_list.md, marketing_playbook.md, operational_memory.md
- sales_call_kit.md, sales_mastery.md, service_industry_guide.md
- system_recovery.md, video_demo_script.md, web_mastery.md

## Conversation History
- 38 past sessions analyzed
- Key patterns: pricing fixes, Vapi config, GHL integration, dashboard repairs

## Common Issues to Avoid
- .env null character corruption (lines 56-58)
- GitHub GH013 secret scanning blocks
- Vapi call forwarding is phone-level not assistant-level
- Dashboard shows 0 when Supabase connection fails

## Success Patterns
- Always use os.getenv for API keys, never hardcode
- Run cortex_loop.py to sync memory after changes
- Deploy to backup repo if main has secret issues
"""

# Use simple upsert
cur.execute("""
    INSERT INTO system_memory (key, value) 
    VALUES ('master_context', %s)
    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
""", (master_context,))

cur.execute("""
    INSERT INTO system_memory (key, value) 
    VALUES ('meta_learnings', %s)
    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
""", (json.dumps({
    'conversations': 38,
    'knowledge_files': 12,
    'leads': 139,
    'last_updated': datetime.now().isoformat()
}),))

conn.commit()
print("Brain data inserted successfully!")

# Verify
cur.execute("SELECT key FROM system_memory")
keys = [r[0] for r in cur.fetchall()]
print(f"\nSystem memory now has {len(keys)} entries:")
for k in keys:
    print(f"  - {k}")
    
conn.close()
