-- ==========================================================
-- COMBINED P0 SQL MIGRATION
-- Run this SINGLE file in Supabase SQL Editor
-- Includes: all tables + Jan 18 kickoff + verification queries
-- ==========================================================
-- ============================================
-- 1. PROMPT VARIANTS (seed_prompt_variants.sql)
-- ============================================
CREATE TABLE IF NOT EXISTS prompt_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    vertical TEXT NOT NULL DEFAULT 'general',
    agent TEXT NOT NULL DEFAULT 'sarah',
    message_template TEXT,
    system_prompt TEXT,
    alpha INT DEFAULT 1,
    beta_param INT DEFAULT 1,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_prompt_variants_vertical_agent ON prompt_variants(vertical, agent, active);
CREATE INDEX IF NOT EXISTS idx_prompt_variants_active ON prompt_variants(active);
-- 5 SMS HVAC variants (agent: sarah)
INSERT INTO prompt_variants (
        name,
        vertical,
        agent,
        message_template,
        alpha,
        beta_param,
        active
    )
VALUES (
        'hvac_sms_direct',
        'hvac',
        'sarah',
        'Hi, this is Sarah from AI Service Co. I noticed {company} might be missing calls after hours. We handle that 24/7 - no missed leads. Got 2 min to chat about how it works?',
        1,
        1,
        TRUE
    ),
    (
        'hvac_sms_pain',
        'hvac',
        'sarah',
        'Hey! Quick question for {company} - how many service calls do you think go to voicemail each month? We help HVAC companies capture 100% of those. Can I show you how in 30 seconds?',
        1,
        1,
        TRUE
    ),
    (
        'hvac_sms_proof',
        'hvac',
        'sarah',
        'Hi from AI Service Co. We work with HVAC companies across Florida - one client went from 40% to 100% call answer rate. Would that kind of result matter for {company}?',
        1,
        1,
        TRUE
    ),
    (
        'hvac_sms_curious',
        'hvac',
        'sarah',
        'Quick q for {company}: If a customer calls at 9pm with an AC emergency, who answers? We make sure it''s never voicemail. Want me to explain how it works?',
        1,
        1,
        TRUE
    ),
    (
        'hvac_sms_value',
        'hvac',
        'sarah',
        'Hey! I put together a quick report on how {company} could capture more after-hours calls. Mind if I send it over? Takes 2 min to review.',
        1,
        1,
        TRUE
    ) ON CONFLICT DO NOTHING;
-- 3 Email HVAC variants (agent: christina)
INSERT INTO prompt_variants (
        name,
        vertical,
        agent,
        message_template,
        system_prompt,
        alpha,
        beta_param,
        active
    )
VALUES (
        'hvac_email_problem',
        'hvac',
        'christina',
        E'Subject: {company} - Missing Calls = Missing Revenue\n\nHi,\n\nQuick question: When a homeowner calls {company} after 5pm with an AC emergency, what happens?\n\nIf the answer is "voicemail" - you' 're leaving money on the table. We help HVAC companies answer every call, 24/7, with AI that sounds natural and books appointments directly into your calendar.\n\nNo missed calls. No lost revenue. No extra staff.\n\nWorth a 15-min call to see if it fits?\n\n- Christina\nAI Service Co',
        'You are Christina, outbound sales specialist for AI Service Co. Focus on business impact of missed calls.',
        1,
        1,
        TRUE
    ),
    (
        'hvac_email_numbers',
        'hvac',
        'christina',
        E'Subject: {company} - Here' 's What 24/7 Call Handling Could Mean\n\nHi,\n\nDid you know the average HVAC company misses 30-40% of inbound calls?\n\nAt $200+ per service call, that adds up fast.\n\nWe built an AI system that:\n✓ Answers every call (day, night, weekend)\n✓ Qualifies the lead in real-time\n✓ Books directly into your calendar\n\nCan I grab 15 min to show you how it works for {company}?\n\n- Christina',
        'You are Christina, use numbers and ROI focus.',
        1,
        1,
        TRUE
    ),
    (
        'hvac_email_story',
        'hvac',
        'christina',
        E'Subject: Thought of {company} when I saw this\n\nHi,\n\nA contractor told me last week: "I hired a receptionist for $3k/month and she still missed half the after-hours calls."\n\nWe built Sarah - an AI that handles calls 24/7, never takes a sick day, and costs a fraction of that.\n\nWould it make sense to see if she' 'd be a fit for {company}?\n\n- Christina',
        'You are Christina, use storytelling and relatable examples.',
        1,
        1,
        TRUE
    ) ON CONFLICT DO NOTHING;
-- ============================================
-- 2. OUTREACH ATTRIBUTION
-- ============================================
CREATE TABLE IF NOT EXISTS outreach_attribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ DEFAULT NOW(),
    contact_id TEXT,
    phone TEXT NOT NULL,
    channel TEXT NOT NULL CHECK (channel IN ('sms', 'email', 'call')),
    variant_id UUID,
    variant_name TEXT,
    correlation_id TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_outreach_attr_phone ON outreach_attribution(phone);
CREATE INDEX IF NOT EXISTS idx_outreach_attr_ts ON outreach_attribution(ts DESC);
CREATE INDEX IF NOT EXISTS idx_outreach_attr_variant ON outreach_attribution(variant_id);
-- ============================================
-- 3. KICKOFF RUNS + TOMORROW (JAN 18)
-- ============================================
CREATE TABLE IF NOT EXISTS kickoff_runs (
    date DATE PRIMARY KEY,
    executed BOOLEAN NOT NULL DEFAULT false,
    executed_at TIMESTAMPTZ,
    run_id TEXT,
    contacts_reached INT DEFAULT 0,
    details JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_kickoff_runs_executed ON kickoff_runs(date, executed);
-- INSERT JANUARY 18, 2026 as kickoff date
INSERT INTO kickoff_runs (date, executed)
VALUES ('2026-01-18', false) ON CONFLICT (date) DO NOTHING;
-- ============================================
-- 4. TRAINING DATA
-- ============================================
CREATE TABLE IF NOT EXISTS training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ DEFAULT NOW(),
    source TEXT NOT NULL DEFAULT 'internal',
    dataset TEXT,
    pattern_type TEXT,
    pattern_text TEXT,
    raw_text TEXT,
    scenario TEXT,
    outcome TEXT DEFAULT 'neutral',
    emotional_cues JSONB DEFAULT '{}',
    agent TEXT,
    learning_extracted BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_training_data_ts ON training_data(ts DESC);
CREATE INDEX IF NOT EXISTS idx_training_data_pattern_type ON training_data(pattern_type);
CREATE INDEX IF NOT EXISTS idx_training_data_source ON training_data(source);
-- ============================================
-- 5. CONTENT ENGINE TABLES
-- ============================================
CREATE TABLE IF NOT EXISTS content_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL CHECK (type IN ('video', 'image', 'text', 'audio')),
    source TEXT NOT NULL,
    title TEXT,
    description TEXT,
    file_url TEXT,
    thumbnail_url TEXT,
    duration_seconds INT,
    resolution TEXT,
    prompt TEXT,
    performance JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS content_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content_library(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (
        status IN (
            'pending',
            'approved',
            'rejected',
            'auto_approved'
        )
    ),
    approved_by TEXT,
    approved_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS posting_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform TEXT UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    cadence_per_day INT DEFAULT 1,
    window_start_hour INT DEFAULT 9,
    window_end_hour INT DEFAULT 17,
    weekdays_only BOOLEAN DEFAULT TRUE,
    require_approval BOOLEAN DEFAULT TRUE,
    last_posted_at TIMESTAMPTZ,
    posts_today INT DEFAULT 0,
    posts_today_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS content_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content_library(id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK (
        action IN (
            'publish',
            'schedule',
            'boost',
            'archive',
            'delete'
        )
    ),
    platform TEXT,
    scheduled_for TIMESTAMPTZ,
    status TEXT DEFAULT 'queued' CHECK (
        status IN (
            'queued',
            'processing',
            'completed',
            'failed',
            'cancelled'
        )
    ),
    attempts INT DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Default posting rules (all disabled)
INSERT INTO posting_rules (
        platform,
        enabled,
        cadence_per_day,
        window_start_hour,
        window_end_hour,
        weekdays_only,
        require_approval
    )
VALUES ('facebook', FALSE, 2, 9, 18, TRUE, TRUE),
    ('instagram', FALSE, 2, 10, 20, TRUE, TRUE),
    ('linkedin', FALSE, 1, 8, 17, TRUE, TRUE),
    (
        'google_business_profile',
        FALSE,
        1,
        9,
        17,
        TRUE,
        TRUE
    ),
    ('twitter', FALSE, 3, 8, 22, FALSE, TRUE),
    ('tiktok', FALSE, 1, 12, 21, FALSE, TRUE) ON CONFLICT (platform) DO NOTHING;
-- ============================================
-- 6. THOMPSON SAMPLING FUNCTIONS
-- ============================================
CREATE OR REPLACE FUNCTION get_best_variant(
        p_vertical TEXT DEFAULT 'general',
        p_agent TEXT DEFAULT 'sarah'
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        message_template TEXT,
        system_prompt TEXT,
        alpha INT,
        beta_param INT
    ) AS $$
DECLARE variant RECORD;
best_variant RECORD;
best_sample FLOAT := -1;
current_sample FLOAT;
BEGIN FOR variant IN
SELECT pv.id,
    pv.name,
    pv.message_template,
    pv.system_prompt,
    pv.alpha,
    pv.beta_param
FROM prompt_variants pv
WHERE pv.vertical = p_vertical
    AND pv.agent = p_agent
    AND pv.active = TRUE LOOP current_sample := random() * (
        variant.alpha::FLOAT / (variant.alpha + variant.beta_param)
    );
IF current_sample > best_sample THEN best_sample := current_sample;
best_variant := variant;
END IF;
END LOOP;
IF best_variant IS NOT NULL THEN RETURN QUERY
SELECT best_variant.id,
    best_variant.name,
    best_variant.message_template,
    best_variant.system_prompt,
    best_variant.alpha,
    best_variant.beta_param;
END IF;
RETURN;
END;
$$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION update_variant_outcome(p_variant_id UUID, p_success BOOLEAN) RETURNS VOID AS $$ BEGIN IF p_success THEN
UPDATE prompt_variants
SET alpha = alpha + 1,
    updated_at = NOW()
WHERE id = p_variant_id;
ELSE
UPDATE prompt_variants
SET beta_param = beta_param + 1,
    updated_at = NOW()
WHERE id = p_variant_id;
END IF;
END;
$$ LANGUAGE plpgsql;
-- ============================================
-- GRANTS
-- ============================================
GRANT ALL ON prompt_variants TO authenticated;
GRANT ALL ON outreach_attribution TO authenticated;
GRANT ALL ON kickoff_runs TO authenticated;
GRANT ALL ON training_data TO authenticated;
GRANT ALL ON content_library TO authenticated;
GRANT ALL ON content_approvals TO authenticated;
GRANT ALL ON posting_rules TO authenticated;
GRANT ALL ON content_queue TO authenticated;
GRANT EXECUTE ON FUNCTION get_best_variant TO authenticated;
GRANT EXECUTE ON FUNCTION update_variant_outcome TO authenticated;
-- ============================================
-- VERIFICATION QUERIES
-- ============================================
-- 1. Check prompt variants for HVAC
SELECT name,
    vertical,
    agent,
    alpha,
    beta_param,
    active
FROM prompt_variants
WHERE vertical = 'hvac'
ORDER BY name;
-- 2. Check kickoff for Jan 18
SELECT *
FROM kickoff_runs
WHERE date = '2026-01-18';
-- 3. Check posting rules
SELECT platform,
    enabled,
    cadence_per_day,
    window_start_hour,
    window_end_hour
FROM posting_rules
ORDER BY platform;