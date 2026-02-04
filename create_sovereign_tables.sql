
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
