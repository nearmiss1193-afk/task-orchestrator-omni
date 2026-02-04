-- Supabase Migration: Create sovereign_memory table
-- Board approved: Grok, Gemini, ChatGPT unanimous
-- Date: Feb 4, 2026
-- Create the table
CREATE TABLE IF NOT EXISTS sovereign_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    section TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    source TEXT DEFAULT 'system',
    CONSTRAINT unique_section_key UNIQUE (section, key)
);
-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_sovereign_memory_section ON sovereign_memory(section);
CREATE INDEX IF NOT EXISTS idx_sovereign_memory_key ON sovereign_memory(key);
CREATE INDEX IF NOT EXISTS idx_sovereign_memory_updated ON sovereign_memory(last_updated DESC);
-- Enable Row Level Security (but allow service role full access)
ALTER TABLE sovereign_memory ENABLE ROW LEVEL SECURITY;
-- Policy: Service role can do everything
CREATE POLICY "Service role full access" ON sovereign_memory FOR ALL USING (true) WITH CHECK (true);
-- Insert initial system context
INSERT INTO sovereign_memory (section, key, value, source)
VALUES ('system', 'version', '5.5', 'init'),
    (
        'system',
        'brand',
        'AI Service Co (A Division of WORLD UNITIES)',
        'init'
    ),
    ('system', 'location', 'Lakeland, FL', 'init'),
    ('system', 'phone', '+1-352-936-8152', 'init'),
    (
        'contacts',
        'email',
        'dan@aiserviceco.com',
        'init'
    ),
    (
        'ai',
        'voice_sarah',
        '1a797f12-e2dd-4f7f-b2c5-08c38c74859a',
        'init'
    ),
    (
        'ai',
        'voice_rachel',
        'b51b43d3-5645-4e49-be96-5a8c3b32e0ea',
        'init'
    ),
    (
        'crm',
        'ghl_location',
        'uFYcZA7Zk6EcBze5B4oH',
        'init'
    ),
    (
        'crm',
        'ghl_pipeline',
        'M7YwDClf34RsNhPQfhS7',
        'init'
    ) ON CONFLICT (section, key) DO
UPDATE
SET value = EXCLUDED.value,
    last_updated = NOW(),
    source = EXCLUDED.source;
-- Comment for documentation
COMMENT ON TABLE sovereign_memory IS 'Operational memory for AI Service Co - synced from operational_memory.md';