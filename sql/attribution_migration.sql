-- Outreach Attribution + Appointment Outcomes Migration
-- For Thompson Sampling credit assignment: which variant produced the booking?
-- Table to track every outreach attempt with its variant
CREATE TABLE IF NOT EXISTS outreach_attribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    location_id TEXT,
    contact_id TEXT,
    phone TEXT,
    channel TEXT NOT NULL,
    -- 'sms', 'email', 'call'
    variant_id UUID,
    variant_name TEXT,
    touch INTEGER DEFAULT 1,
    correlation_id TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_outreach_attr_contact ON outreach_attribution(contact_id);
CREATE INDEX IF NOT EXISTS idx_outreach_attr_phone ON outreach_attribution(phone);
CREATE INDEX IF NOT EXISTS idx_outreach_attr_ts ON outreach_attribution(ts DESC);
CREATE INDEX IF NOT EXISTS idx_outreach_attr_variant ON outreach_attribution(variant_id);
-- Lightweight appointment outcomes table for quick learning
CREATE TABLE IF NOT EXISTS appointment_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    contact_id TEXT,
    phone TEXT,
    appointment_id TEXT NOT NULL,
    variant_id UUID,
    variant_name TEXT,
    outcome TEXT NOT NULL DEFAULT 'booked',
    -- 'booked', 'no_show', 'cancelled', 'completed'
    attribution_id UUID REFERENCES outreach_attribution(id),
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_appt_outcomes_variant ON appointment_outcomes(variant_id);
CREATE INDEX IF NOT EXISTS idx_appt_outcomes_ts ON appointment_outcomes(ts DESC);
CREATE INDEX IF NOT EXISTS idx_appt_outcomes_contact ON appointment_outcomes(contact_id);
-- Prompt variants table for Thompson Sampling (if not exists)
CREATE TABLE IF NOT EXISTS prompt_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    vertical TEXT DEFAULT 'general',
    agent TEXT DEFAULT 'christina',
    -- 'christina', 'sarah'
    opener TEXT,
    follow_up TEXT,
    closer TEXT,
    alpha INTEGER DEFAULT 1,
    -- Prior successes (Bayesian)
    beta INTEGER DEFAULT 1,
    -- Prior failures (Bayesian)
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT unique_variant_name UNIQUE (name, vertical, agent)
);
-- Insert some default variants for testing
INSERT INTO prompt_variants (name, vertical, agent, opener, alpha, beta)
VALUES (
        'direct_value',
        'general',
        'christina',
        'Hi! I just reviewed {company}''s marketing - there are quick wins you''re missing. Got 15 min? {booking_link}',
        1,
        1
    ),
    (
        'curiosity_hook',
        'general',
        'christina',
        'Hey! Noticed something interesting about {company}. Mind if I share? {booking_link}',
        1,
        1
    ),
    (
        'urgency_limited',
        'general',
        'christina',
        'Quick heads up - I''m reaching out to just 10 businesses this week. {company} is on my list. Interested? {booking_link}',
        1,
        1
    ),
    (
        'social_proof',
        'general',
        'christina',
        'We just helped a {vertical} company boost leads 40% in 30 days. {company} could be next. Free call? {booking_link}',
        1,
        1
    ) ON CONFLICT (name, vertical, agent) DO NOTHING;
-- Function to get best variant using Thompson Sampling
CREATE OR REPLACE FUNCTION get_best_variant(
        p_vertical TEXT DEFAULT 'general',
        p_agent TEXT DEFAULT 'christina'
    ) RETURNS TABLE (
        id UUID,
        name TEXT,
        opener TEXT,
        alpha INTEGER,
        beta INTEGER
    ) AS $$ BEGIN RETURN QUERY
SELECT pv.id,
    pv.name,
    pv.opener,
    pv.alpha,
    pv.beta
FROM prompt_variants pv
WHERE pv.vertical = COALESCE(p_vertical, 'general')
    AND pv.agent = COALESCE(p_agent, 'christina')
    AND pv.active = true
ORDER BY random() * (pv.alpha::float / (pv.alpha + pv.beta)) DESC
LIMIT 1;
END;
$$ LANGUAGE plpgsql;
-- Function to update variant based on outcome
CREATE OR REPLACE FUNCTION update_variant_outcome(
        p_variant_id UUID,
        p_success BOOLEAN DEFAULT true
    ) RETURNS VOID AS $$ BEGIN IF p_success THEN
UPDATE prompt_variants
SET alpha = alpha + 1
WHERE id = p_variant_id;
ELSE
UPDATE prompt_variants
SET beta = beta + 1
WHERE id = p_variant_id;
END IF;
END;
$$ LANGUAGE plpgsql;
COMMENT ON TABLE outreach_attribution IS 'Tracks outreach attempts with variant for credit assignment';
COMMENT ON TABLE appointment_outcomes IS 'Links appointments to variants for Thompson Sampling learning';
COMMENT ON TABLE prompt_variants IS 'Message variants for A/B testing with Bayesian scoring';