"""Create Sovereign Memory Tables in Supabase"""
from supabase import create_client
import json

url = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo'

sb = create_client(url, key)

# SQL to create tables (run via Supabase SQL editor or REST API)
CREATE_TABLES_SQL = """
-- 1. sovereign_config - Critical configuration storage
CREATE TABLE IF NOT EXISTS sovereign_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    category VARCHAR(100),
    description TEXT,
    version INTEGER DEFAULT 1,
    encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. sovereign_actions - All actions with success/failure
CREATE TABLE IF NOT EXISTS sovereign_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_type VARCHAR(255) NOT NULL,
    action_description TEXT,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    success BOOLEAN,
    error_message TEXT,
    duration_ms INTEGER,
    task_id UUID,
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. sovereign_errors - Error patterns with solutions
CREATE TABLE IF NOT EXISTS sovereign_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    error_pattern TEXT NOT NULL,
    error_message TEXT,
    solution TEXT NOT NULL,
    solution_code TEXT,
    frequency INTEGER DEFAULT 1,
    last_occurrence TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    success_rate FLOAT DEFAULT 0,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. sovereign_code - Working code snippets
CREATE TABLE IF NOT EXISTS sovereign_code (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    language VARCHAR(50) NOT NULL,
    code_snippet TEXT NOT NULL,
    description TEXT,
    use_case TEXT,
    file_context VARCHAR(500),
    tags TEXT[],
    version INTEGER DEFAULT 1,
    usefulness_score INTEGER DEFAULT 0,
    times_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. sovereign_preferences - Hard rules from user
CREATE TABLE IF NOT EXISTS sovereign_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    preference_key VARCHAR(255) UNIQUE NOT NULL,
    preference_value TEXT NOT NULL,
    rule_type VARCHAR(50) DEFAULT 'preference',
    priority INTEGER DEFAULT 5,
    is_hard_rule BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. sovereign_tasks - Task tracking
CREATE TABLE IF NOT EXISTS sovereign_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_name VARCHAR(255) NOT NULL,
    task_description TEXT,
    task_goal TEXT,
    parent_task_id UUID REFERENCES sovereign_tasks(id),
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    context JSONB,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    model_used VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. sovereign_embeddings - Vector search (requires pgvector extension)
CREATE TABLE IF NOT EXISTS sovereign_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_table VARCHAR(255) NOT NULL,
    source_id UUID NOT NULL,
    text_content TEXT,
    embedding_model VARCHAR(100) DEFAULT 'text-embedding-ada-002',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. sovereign_sessions - Conversation context
CREATE TABLE IF NOT EXISTS sovereign_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE NOT NULL,
    context JSONB,
    user_id TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE
);

-- 9. sovereign_logs - Detailed audit logs
CREATE TABLE IF NOT EXISTS sovereign_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    log_level VARCHAR(20) DEFAULT 'info',
    message TEXT NOT NULL,
    details JSONB,
    source VARCHAR(255),
    task_id UUID,
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. sovereign_alerts - Urgent notifications
CREATE TABLE IF NOT EXISTS sovereign_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    severity VARCHAR(20) DEFAULT 'info',
    title VARCHAR(255) NOT NULL,
    message TEXT,
    task_id UUID,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sovereign_config_key ON sovereign_config(config_key);
CREATE INDEX IF NOT EXISTS idx_sovereign_actions_type ON sovereign_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_sovereign_errors_pattern ON sovereign_errors(error_pattern);
CREATE INDEX IF NOT EXISTS idx_sovereign_code_language ON sovereign_code(language);
CREATE INDEX IF NOT EXISTS idx_sovereign_tasks_status ON sovereign_tasks(status);
CREATE INDEX IF NOT EXISTS idx_sovereign_logs_level ON sovereign_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_sovereign_alerts_severity ON sovereign_alerts(severity);
"""

print("="*60)
print("SOVEREIGN MEMORY SYSTEM - TABLE CREATION")
print("="*60)

# Since we can't run raw SQL via REST API, we'll create tables by inserting test data
# which will fail if table doesn't exist, giving us info

tables_to_check = [
    'sovereign_config',
    'sovereign_actions', 
    'sovereign_errors',
    'sovereign_code',
    'sovereign_preferences',
    'sovereign_tasks',
    'sovereign_embeddings',
    'sovereign_sessions',
    'sovereign_logs',
    'sovereign_alerts'
]

print("\nChecking existing tables...")
for table in tables_to_check:
    try:
        result = sb.table(table).select('id').limit(1).execute()
        print(f"  ✅ {table} - EXISTS ({len(result.data)} rows)")
    except Exception as e:
        print(f"  ❌ {table} - NEEDS CREATION")

print("\n" + "="*60)
print("SQL TO RUN IN SUPABASE SQL EDITOR:")
print("="*60)
print(CREATE_TABLES_SQL)

# Save SQL to file for manual execution
with open('create_sovereign_tables.sql', 'w') as f:
    f.write(CREATE_TABLES_SQL)

print("\n✅ SQL saved to: create_sovereign_tables.sql")
print("Run this in Supabase Dashboard > SQL Editor")

# Insert initial critical config
print("\n" + "="*60)
print("INSERTING CRITICAL CONFIG...")
print("="*60)

initial_config = [
    {'config_key': 'ghl_form_id', 'config_value': '7TTJ1CUAFjhON69ZsOZK', 'category': 'ghl', 'description': 'CORRECT form ID - links.aiserviceco.com'},
    {'config_key': 'ghl_calendar_id', 'config_value': 'YWQcHuXXznQEQa7LAWeB', 'category': 'ghl', 'description': 'CORRECT calendar ID - links.aiserviceco.com'},
    {'config_key': 'ghl_embed_domain', 'config_value': 'links.aiserviceco.com', 'category': 'ghl', 'description': 'NOT api.leadconnectorhq.com or link.msgsndr.com'},
    {'config_key': 'vapi_public_key', 'config_value': '3b065ff0-a721-4b66-8255-30b6b8d6daab', 'category': 'vapi', 'description': 'Vapi widget API key'},
    {'config_key': 'vapi_assistant_id', 'config_value': '1a797f12-e2dd-4f7f-b2c5-08c38c74859a', 'category': 'vapi', 'description': 'Sarah assistant ID'},
    {'config_key': 'vapi_widget_title', 'config_value': 'Talk to Sales', 'category': 'vapi', 'description': 'Widget button text'},
    {'config_key': 'vapi_widget_subtitle', 'config_value': 'Ask anything', 'category': 'vapi', 'description': 'Widget subtitle'},
    {'config_key': 'vapi_widget_color', 'config_value': '#f59e0b', 'category': 'vapi', 'description': 'Yellow/orange color'},
    {'config_key': 'vapi_widget_icon', 'config_value': 'mic', 'category': 'vapi', 'description': 'Microphone icon'},
]

# Try system_state table since sovereign_config may not exist yet
for cfg in initial_config:
    try:
        # Try sovereign_config first
        result = sb.table('sovereign_config').upsert(cfg, on_conflict='config_key').execute()
        print(f"  ✅ Saved: {cfg['config_key']}")
    except:
        # Fallback to system_state
        try:
            fallback = {'key': cfg['config_key'], 'status': cfg['config_value'], 'notes': cfg.get('description', '')}
            result = sb.table('system_state').upsert(fallback, on_conflict='key').execute()
            print(f"  ✅ Saved to system_state: {cfg['config_key']}")
        except Exception as e:
            print(f"  ❌ Failed: {cfg['config_key']} - {str(e)[:50]}")

# Add hard rules to preferences
print("\n" + "="*60)
print("INSERTING HARD RULES...")
print("="*60)

hard_rules = [
    {'key': 'RULE_query_config_before_edit', 'status': 'ALWAYS query sovereign_config before editing any embed, form, or widget code', 'notes': 'HARD RULE'},
    {'key': 'RULE_check_errors_on_failure', 'status': 'ALWAYS query sovereign_errors when encountering an error', 'notes': 'HARD RULE'},
    {'key': 'RULE_save_working_code', 'status': 'ALWAYS save working code to sovereign_code after successful fix', 'notes': 'HARD RULE'},
    {'key': 'RULE_push_before_deploy', 'status': 'NEVER deploy without git push first - FATAL', 'notes': 'HARD RULE'},
    {'key': 'RULE_verify_database_results', 'status': 'Exit code 0 means NOTHING - verify database results', 'notes': 'HARD RULE'},
]

for rule in hard_rules:
    try:
        result = sb.table('system_state').upsert(rule, on_conflict='key').execute()
        print(f"  ✅ Rule saved: {rule['key']}")
    except Exception as e:
        print(f"  ❌ Rule failed: {rule['key']} - {str(e)[:50]}")

print("\n" + "="*60)
print("SOVEREIGN MEMORY SYSTEM SETUP COMPLETE")
print("="*60)
