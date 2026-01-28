-- ==========================================================
-- CUSTOMER MEMORY SYSTEM - Complete Schema
-- AI Service Co - Building rapport through remembered details
-- ==========================================================
-- 1. Customer Profile - Central customer information
CREATE TABLE IF NOT EXISTS customer_profile (
    contact_id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    email TEXT,
    -- Personal details (extracted from conversations)
    spouse_name TEXT,
    spouse_birthday DATE,
    children TEXT [],
    -- ['Tommy age 8', 'Sarah age 5']
    pets TEXT [],
    -- ['Dog named Max']
    hobbies TEXT [],
    -- ['biking', 'golf', 'fishing']
    favorite_sports_team TEXT,
    -- Business details
    business_name TEXT,
    business_type TEXT,
    employee_count INTEGER,
    pain_points TEXT [],
    -- Relationship tracking
    communication_style TEXT,
    -- 'formal', 'casual', 'joker', 'straight-to-point'
    best_time_to_call TEXT,
    topics_to_avoid TEXT [],
    topics_they_love TEXT [],
    -- AI notes
    rapport_score INTEGER DEFAULT 50,
    -- 0-100
    last_interaction TIMESTAMPTZ,
    total_interactions INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- 2. Customer Memories - Individual memorable facts
CREATE TABLE IF NOT EXISTS customer_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id TEXT NOT NULL REFERENCES customer_profile(contact_id) ON DELETE CASCADE,
    memory_type TEXT NOT NULL,
    -- 'personal', 'preference', 'event', 'complaint', 'family', 'health', 'hobby', 'business'
    memory_text TEXT NOT NULL,
    -- "Wife's birthday is January 15"
    source TEXT NOT NULL,
    -- 'call', 'sms', 'email', 'form'
    source_id TEXT,
    -- ID of the call/sms/email
    importance INTEGER DEFAULT 5 CHECK (
        importance >= 1
        AND importance <= 10
    ),
    reminder_date DATE,
    -- If this should trigger a reminder
    reminder_sent BOOLEAN DEFAULT FALSE,
    extracted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_memories_contact ON customer_memories(contact_id);
CREATE INDEX IF NOT EXISTS idx_memories_reminder ON customer_memories(reminder_date)
WHERE reminder_sent = FALSE;
CREATE INDEX IF NOT EXISTS idx_memories_type ON customer_memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON customer_memories(importance DESC);
-- 3. Customer Timeline - Complete interaction history
CREATE TABLE IF NOT EXISTS customer_timeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    -- 'call', 'sms_in', 'sms_out', 'email_in', 'email_out', 'form', 'appointment', 'purchase'
    event_summary TEXT,
    -- AI-generated summary
    full_content TEXT,
    -- Full transcript/message
    sentiment TEXT CHECK (
        sentiment IN (
            'positive',
            'neutral',
            'negative',
            'frustrated',
            'happy'
        )
    ),
    key_topics TEXT [],
    -- ['pricing', 'wife', 'bike accident']
    duration_seconds INTEGER,
    -- For calls
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for timeline queries
CREATE INDEX IF NOT EXISTS idx_timeline_contact ON customer_timeline(contact_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_timeline_type ON customer_timeline(event_type);
CREATE INDEX IF NOT EXISTS idx_timeline_sentiment ON customer_timeline(sentiment);
-- 4. Memory Reminders View - Easy access to pending reminders
CREATE OR REPLACE VIEW pending_reminders AS
SELECT m.id as memory_id,
    m.contact_id,
    m.memory_type,
    m.memory_text,
    m.reminder_date,
    p.first_name,
    p.last_name,
    p.phone,
    p.email
FROM customer_memories m
    JOIN customer_profile p ON m.contact_id = p.contact_id
WHERE m.reminder_date <= CURRENT_DATE
    AND m.reminder_sent = FALSE
ORDER BY m.reminder_date ASC;
-- 5. Customer Context View - For Sarah to load before calls
CREATE OR REPLACE VIEW customer_context AS
SELECT p.contact_id,
    p.first_name,
    p.last_name,
    p.phone,
    p.email,
    p.spouse_name,
    p.hobbies,
    p.communication_style,
    p.best_time_to_call,
    p.topics_to_avoid,
    p.topics_they_love,
    p.rapport_score,
    p.total_interactions,
    p.last_interaction,
    (
        SELECT json_agg(
                json_build_object(
                    'type',
                    m.memory_type,
                    'text',
                    m.memory_text,
                    'importance',
                    m.importance
                )
                ORDER BY m.importance DESC
            )
        FROM customer_memories m
        WHERE m.contact_id = p.contact_id
        LIMIT 10
    ) as top_memories,
    (
        SELECT json_agg(
                json_build_object(
                    'type',
                    t.event_type,
                    'summary',
                    t.event_summary,
                    'sentiment',
                    t.sentiment,
                    'date',
                    t.created_at
                )
                ORDER BY t.created_at DESC
            )
        FROM customer_timeline t
        WHERE t.contact_id = p.contact_id
        LIMIT 5
    ) as recent_timeline
FROM customer_profile p;
-- 6. Insert trigger to auto-update profile timestamp
CREATE OR REPLACE FUNCTION update_profile_timestamp() RETURNS TRIGGER AS $$ BEGIN
UPDATE customer_profile
SET updated_at = NOW(),
    total_interactions = total_interactions + 1,
    last_interaction = NOW()
WHERE contact_id = NEW.contact_id;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS timeline_update_profile ON customer_timeline;
CREATE TRIGGER timeline_update_profile
AFTER
INSERT ON customer_timeline FOR EACH ROW EXECUTE FUNCTION update_profile_timestamp();
-- 7. RLS Policies (for security)
ALTER TABLE customer_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_timeline ENABLE ROW LEVEL SECURITY;
-- Service role can do everything
CREATE POLICY "Service role full access profiles" ON customer_profile FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access memories" ON customer_memories FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access timeline" ON customer_timeline FOR ALL USING (auth.role() = 'service_role');
-- 8. Sample seed data for testing
INSERT INTO customer_profile (
        contact_id,
        first_name,
        last_name,
        phone,
        email,
        hobbies,
        communication_style,
        rapport_score
    )
VALUES (
        'test_mike_001',
        'Mike',
        'Johnson',
        '+13525551234',
        'mike@example.com',
        ARRAY ['biking', 'golf'],
        'casual',
        65
    ) ON CONFLICT (contact_id) DO NOTHING;
INSERT INTO customer_memories (
        contact_id,
        memory_type,
        memory_text,
        source,
        importance,
        reminder_date
    )
VALUES (
        'test_mike_001',
        'family',
        'Wife''s birthday is January 15',
        'call',
        8,
        '2026-01-15'
    ),
    (
        'test_mike_001',
        'health',
        'Fell off his bike last month, recovering from bruised ribs',
        'sms',
        7,
        NULL
    ),
    (
        'test_mike_001',
        'hobby',
        'Loves golf, plays every Sunday',
        'call',
        6,
        NULL
    ) ON CONFLICT DO NOTHING;
INSERT INTO customer_timeline (
        contact_id,
        event_type,
        event_summary,
        sentiment,
        key_topics
    )
VALUES (
        'test_mike_001',
        'call',
        'Inquired about AI receptionist pricing. Mentioned he''s tired of missing calls while on the golf course.',
        'positive',
        ARRAY ['pricing', 'golf', 'missed calls']
    ) ON CONFLICT DO NOTHING;
-- Grant permissions
GRANT ALL ON customer_profile TO service_role;
GRANT ALL ON customer_memories TO service_role;
GRANT ALL ON customer_timeline TO service_role;
GRANT SELECT ON pending_reminders TO service_role;
GRANT SELECT ON customer_context TO service_role;