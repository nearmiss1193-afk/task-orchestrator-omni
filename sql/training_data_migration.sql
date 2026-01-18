-- ==========================================================
-- TRAINING DATA TABLE
-- For continuous learning from HuggingFace + internal sources
-- Run in Supabase SQL Editor
-- ==========================================================
CREATE TABLE IF NOT EXISTS training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ DEFAULT NOW(),
    source TEXT NOT NULL DEFAULT 'internal',
    -- 'huggingface', 'internal', 'outcome'
    dataset TEXT,
    -- Dataset name or source identifier
    pattern_type TEXT,
    -- 'objection', 'closing', 'rapport', 'price', 'timing'
    pattern_text TEXT,
    -- Extracted pattern or example
    raw_text TEXT,
    -- Full conversation/context
    scenario TEXT,
    -- 'call_center', 'sales', 'support'
    outcome TEXT DEFAULT 'neutral',
    -- 'converted', 'lost', 'neutral'
    emotional_cues JSONB DEFAULT '{}',
    -- Detected patterns as JSON
    agent TEXT,
    -- 'sarah', 'christina', 'continuous_learning'
    learning_extracted BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb
);
-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_training_data_ts ON training_data(ts DESC);
CREATE INDEX IF NOT EXISTS idx_training_data_pattern_type ON training_data(pattern_type);
CREATE INDEX IF NOT EXISTS idx_training_data_source ON training_data(source);
CREATE INDEX IF NOT EXISTS idx_training_data_outcome ON training_data(outcome);
CREATE INDEX IF NOT EXISTS idx_training_data_agent ON training_data(agent);
-- Grants
GRANT ALL ON training_data TO authenticated;
-- ==========================================================
-- VERIFICATION
-- ==========================================================
SELECT column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'training_data'
ORDER BY ordinal_position;