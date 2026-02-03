-- Sales Learning Loop Migration
-- Framework for evaluating calls, testing talk track variants, and routing to winners
-- ==========================================================
-- CONVERSATION OUTCOMES - Ingested from Vapi transcripts
-- ==========================================================
CREATE TABLE IF NOT EXISTS conversation_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id TEXT NOT NULL UNIQUE,
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Outcome classification
    outcome TEXT NOT NULL,
    -- 'booked', 'callback', 'rejection', 'voicemail', 'no_answer', 'hangup'
    outcome_confidence FLOAT,
    -- 0-1 confidence in outcome classification
    -- Call metadata
    agent TEXT,
    -- 'sarah', 'christina'
    vertical TEXT,
    -- 'hvac', 'plumbing', 'roofing', etc.
    phone TEXT,
    duration_seconds INTEGER,
    -- Variant tracking
    prompt_variant_id UUID,
    variant_name TEXT,
    -- Vapi data
    transcript TEXT,
    summary TEXT,
    vapi_payload JSONB,
    -- Scoring (populated by evaluator)
    scores JSONB,
    -- {rapport: 85, clarity: 90, objection_handling: 70, cta: 80, compliance: 100}
    total_score INTEGER,
    evaluation_notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_outcomes_ts ON conversation_outcomes(ts DESC);
CREATE INDEX IF NOT EXISTS idx_outcomes_outcome ON conversation_outcomes(outcome);
CREATE INDEX IF NOT EXISTS idx_outcomes_variant ON conversation_outcomes(prompt_variant_id);
CREATE INDEX IF NOT EXISTS idx_outcomes_vertical ON conversation_outcomes(vertical);
CREATE INDEX IF NOT EXISTS idx_outcomes_agent ON conversation_outcomes(agent);
-- ==========================================================
-- PROMPT VARIANTS - Talk tracks per vertical with A/B testing
-- ==========================================================
CREATE TABLE IF NOT EXISTS prompt_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Variant identification
    name TEXT NOT NULL,
    -- 'hvac_direct_v2', 'plumbing_empathy_v1'
    vertical TEXT NOT NULL,
    -- 'hvac', 'plumbing', 'roofing', 'general'
    agent TEXT NOT NULL,
    -- 'sarah', 'christina'
    -- Status
    active BOOLEAN DEFAULT true,
    is_control BOOLEAN DEFAULT false,
    -- Control variant for A/B tests
    -- Prompt content
    system_prompt TEXT NOT NULL,
    opener TEXT,
    -- First message template
    objection_handlers JSONB,
    -- {price: "...", timing: "...", competitor: "..."}
    closing_ctas TEXT [],
    -- Array of CTA options
    -- Performance tracking (updated by bandit)
    impressions INTEGER DEFAULT 0,
    successes INTEGER DEFAULT 0,
    -- Bookings
    callbacks INTEGER DEFAULT 0,
    rejections INTEGER DEFAULT 0,
    avg_score FLOAT DEFAULT 0,
    -- Bandit weights (Thompson Sampling)
    alpha FLOAT DEFAULT 1.0,
    -- Beta distribution alpha (successes + 1)
    beta_param FLOAT DEFAULT 1.0,
    -- Beta distribution beta (failures + 1)
    -- Metadata
    version INTEGER DEFAULT 1,
    notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_variants_vertical_agent ON prompt_variants(vertical, agent);
CREATE INDEX IF NOT EXISTS idx_variants_active ON prompt_variants(active)
WHERE active = true;
-- ==========================================================
-- SCORING RUBRIC - Weights for call evaluation
-- ==========================================================
CREATE TABLE IF NOT EXISTS scoring_rubric (
    id SERIAL PRIMARY KEY,
    version INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Dimension weights (must sum to 100)
    weight_rapport INTEGER DEFAULT 20,
    -- Opening, personalization, tone
    weight_clarity INTEGER DEFAULT 20,
    -- Clear value prop, no jargon
    weight_objection_handling INTEGER DEFAULT 25,
    -- Addressed concerns effectively
    weight_cta INTEGER DEFAULT 25,
    -- Strong call to action, booking push
    weight_compliance INTEGER DEFAULT 10,
    -- Proper disclosures, no pressure tactics
    -- Scoring criteria descriptions
    criteria_rapport TEXT DEFAULT 'Warm greeting, uses name, builds connection',
    criteria_clarity TEXT DEFAULT 'Clear explanation of value, no confusion',
    criteria_objection TEXT DEFAULT 'Handles price/timing objections with value reframe',
    criteria_cta TEXT DEFAULT 'Provides booking link, creates urgency, confirms action',
    criteria_compliance TEXT DEFAULT 'STOP honored, no misleading claims, proper opt-out'
);
-- Insert default rubric
INSERT INTO scoring_rubric (version, active, notes)
VALUES (1, true, 'Initial scoring rubric') ON CONFLICT DO NOTHING;
-- ==========================================================
-- BANDIT ROUTING FUNCTIONS
-- ==========================================================
-- Get best variant using Thompson Sampling
CREATE OR REPLACE FUNCTION get_best_variant(p_vertical TEXT, p_agent TEXT) RETURNS prompt_variants AS $$
DECLARE selected prompt_variants;
best_sample FLOAT := -1;
current_sample FLOAT;
v prompt_variants;
BEGIN FOR v IN
SELECT *
FROM prompt_variants
WHERE vertical = p_vertical
    AND agent = p_agent
    AND active = true LOOP -- Thompson Sampling: sample from Beta(alpha, beta)
    -- Using simple approximation: alpha / (alpha + beta) + random noise
    current_sample := v.alpha / (v.alpha + v.beta_param) + (random() - 0.5) * 0.2;
IF current_sample > best_sample THEN best_sample := current_sample;
selected := v;
END IF;
END LOOP;
-- Update impressions
UPDATE prompt_variants
SET impressions = impressions + 1
WHERE id = selected.id;
RETURN selected;
END;
$$ LANGUAGE plpgsql;
-- Update variant performance after outcome
CREATE OR REPLACE FUNCTION update_variant_outcome(
        p_variant_id UUID,
        p_outcome TEXT,
        p_score INTEGER
    ) RETURNS VOID AS $$ BEGIN
UPDATE prompt_variants
SET successes = CASE
        WHEN p_outcome = 'booked' THEN successes + 1
        ELSE successes
    END,
    callbacks = CASE
        WHEN p_outcome = 'callback' THEN callbacks + 1
        ELSE callbacks
    END,
    rejections = CASE
        WHEN p_outcome = 'rejection' THEN rejections + 1
        ELSE rejections
    END,
    -- Update Beta distribution parameters
    alpha = CASE
        WHEN p_outcome = 'booked' THEN alpha + 1.0
        ELSE alpha
    END,
    beta_param = CASE
        WHEN p_outcome IN ('rejection', 'hangup') THEN beta_param + 1.0
        ELSE beta_param
    END,
    -- Update average score
    avg_score = (avg_score * impressions + p_score) / (impressions + 1),
    updated_at = now()
WHERE id = p_variant_id;
END;
$$ LANGUAGE plpgsql;
-- Get variant performance summary
CREATE OR REPLACE FUNCTION get_variant_performance(p_vertical TEXT DEFAULT NULL) RETURNS TABLE (
        id UUID,
        name TEXT,
        vertical TEXT,
        agent TEXT,
        impressions INTEGER,
        successes INTEGER,
        success_rate FLOAT,
        avg_score FLOAT,
        thompson_weight FLOAT
    ) AS $$ BEGIN RETURN QUERY
SELECT pv.id,
    pv.name,
    pv.vertical,
    pv.agent,
    pv.impressions,
    pv.successes,
    CASE
        WHEN pv.impressions > 0 THEN pv.successes::FLOAT / pv.impressions
        ELSE 0
    END,
    pv.avg_score,
    pv.alpha / (pv.alpha + pv.beta_param)
FROM prompt_variants pv
WHERE (
        p_vertical IS NULL
        OR pv.vertical = p_vertical
    )
    AND pv.active = true
ORDER BY pv.alpha / (pv.alpha + pv.beta_param) DESC;
END;
$$ LANGUAGE plpgsql;
-- Seed initial variants for common verticals
INSERT INTO prompt_variants (
        name,
        vertical,
        agent,
        system_prompt,
        opener,
        is_control
    )
VALUES (
        'hvac_direct_v1',
        'hvac',
        'christina',
        'You are Christina, selling AI automation to HVAC companies. Be direct, focus on ROI, mention seasonal demand peaks.',
        'Hi {name}! Quick question about {company} - are you capturing all the AC repair leads in your area this season?',
        true
    ),
    (
        'hvac_empathy_v1',
        'hvac',
        'christina',
        'You are Christina, helping HVAC owners reduce stress. Lead with understanding their pain points before pitching.',
        'Hi {name}, I know running an HVAC business means constant calls and scheduling headaches. What if that could be automatic?',
        false
    ),
    (
        'plumbing_urgent_v1',
        'plumbing',
        'christina',
        'You are Christina, selling to plumbers. Emphasize emergency calls and 24/7 availability.',
        'Hey {name}! Emergency plumbing calls at 2AM - are you answering all of them or losing them to competitors?',
        true
    ),
    (
        'general_value_v1',
        'general',
        'sarah',
        'You are Sarah, the inbound handler. Focus on value proposition and booking consultations.',
        'Thanks for reaching out! Let me show you how we help home service businesses like yours grow...',
        true
    ) ON CONFLICT DO NOTHING;
COMMENT ON TABLE conversation_outcomes IS 'Stores call outcomes and scores for learning loop';
COMMENT ON TABLE prompt_variants IS 'Talk track variants per vertical with Thompson Sampling routing';
COMMENT ON TABLE scoring_rubric IS 'Weights and criteria for evaluating calls';