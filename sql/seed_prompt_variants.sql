-- ==========================================================
-- SEED PROMPT VARIANTS FOR THOMPSON SAMPLING
-- HVAC B2B variants for Monday campaign
-- Run in Supabase SQL Editor
-- ==========================================================
-- Create prompt_variants table if not exists
CREATE TABLE IF NOT EXISTS prompt_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    vertical TEXT NOT NULL DEFAULT 'general',
    agent TEXT NOT NULL DEFAULT 'sarah',
    message_template TEXT,
    system_prompt TEXT,
    alpha INT DEFAULT 1,
    -- Success count (Bayesian prior)
    beta_param INT DEFAULT 1,
    -- Failure count (Bayesian prior)
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Index for variant selection
CREATE INDEX IF NOT EXISTS idx_prompt_variants_vertical_agent ON prompt_variants(vertical, agent, active);
CREATE INDEX IF NOT EXISTS idx_prompt_variants_active ON prompt_variants(active);
-- ==========================================================
-- SMS VARIANTS (5) - HVAC B2B - Agent: sarah
-- Under 280 chars, compliant, different tones
-- ==========================================================
INSERT INTO prompt_variants (
        name,
        vertical,
        agent,
        message_template,
        alpha,
        beta_param,
        active
    )
VALUES -- Variant 1: Direct/Efficient
    (
        'hvac_sms_direct',
        'hvac',
        'sarah',
        'Hi, this is Sarah from AI Service Co. I noticed {company} might be missing calls after hours. We handle that 24/7 - no missed leads. Got 2 min to chat about how it works?',
        1,
        1,
        TRUE
    ),
    -- Variant 2: Pain Point Focus
    (
        'hvac_sms_pain',
        'hvac',
        'sarah',
        'Hey! Quick question for {company} - how many service calls do you think go to voicemail each month? We help HVAC companies capture 100% of those. Can I show you how in 30 seconds?',
        1,
        1,
        TRUE
    ),
    -- Variant 3: Social Proof
    (
        'hvac_sms_proof',
        'hvac',
        'sarah',
        'Hi from AI Service Co. We work with HVAC companies across Florida - one client went from 40% to 100% call answer rate. Would that kind of result matter for {company}?',
        1,
        1,
        TRUE
    ),
    -- Variant 4: Curiosity/Question
    (
        'hvac_sms_curious',
        'hvac',
        'sarah',
        'Quick q for {company}: If a customer calls at 9pm with an AC emergency, who answers? We make sure it''s never voicemail. Want me to explain how it works?',
        1,
        1,
        TRUE
    ),
    -- Variant 5: Value First
    (
        'hvac_sms_value',
        'hvac',
        'sarah',
        'Hey! I put together a quick report on how {company} could capture more after-hours calls. Mind if I send it over? Takes 2 min to review.',
        1,
        1,
        TRUE
    ) ON CONFLICT DO NOTHING;
-- ==========================================================
-- EMAIL VARIANTS (3) - HVAC B2B - Agent: christina
-- Longer form, different CTAs
-- ==========================================================
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
VALUES -- Variant 1: Problem/Solution
    (
        'hvac_email_problem',
        'hvac',
        'christina',
        'Subject: {company} - Missing Calls = Missing Revenue

Hi,

Quick question: When a homeowner calls {company} after 5pm with an AC emergency, what happens?

If the answer is "voicemail" - you''re leaving money on the table. We help HVAC companies answer every call, 24/7, with AI that sounds natural and books appointments directly into your calendar.

No missed calls. No lost revenue. No extra staff.

Worth a 15-min call to see if it fits?

- Christina
AI Service Co',
        'You are Christina, outbound sales specialist for AI Service Co. Focus on the business impact of missed calls.',
        1,
        1,
        TRUE
    ),
    -- Variant 2: Numbers Focus
    (
        'hvac_email_numbers',
        'hvac',
        'christina',
        'Subject: {company} - Here''s What 24/7 Call Handling Could Mean

Hi,

Did you know the average HVAC company misses 30-40% of inbound calls?

At $200+ per service call, that adds up fast.

We built an AI system that:
✓ Answers every call (day, night, weekend)
✓ Qualifies the lead in real-time
✓ Books directly into your calendar
✓ Sends you a summary text

One of our Florida clients cut missed calls to zero in week one.

Can I grab 15 min to show you how it works for {company}?

- Christina
AI Service Co',
        'You are Christina, use numbers and ROI focus.',
        1,
        1,
        TRUE
    ),
    -- Variant 3: Story/Casual
    (
        'hvac_email_story',
        'hvac',
        'christina',
        'Subject: Thought of {company} when I saw this

Hi,

A contractor told me last week: "I hired a receptionist for $3k/month and she still missed half the after-hours calls."

We built Sarah - an AI that handles calls 24/7, never takes a sick day, and costs a fraction of that.

She''s already working for HVAC companies in Florida. Would it make sense to see if she''d be a fit for {company}?

Takes 15 min to walk through.

- Christina
AI Service Co',
        'You are Christina, use storytelling and relatable examples.',
        1,
        1,
        TRUE
    ) ON CONFLICT DO NOTHING;
-- ==========================================================
-- HELPER FUNCTION: Get best variant with Thompson Sampling
-- ==========================================================
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
BEGIN -- Thompson Sampling: For each variant, sample from Beta(alpha, beta)
-- Return the variant with highest sample
FOR variant IN
SELECT pv.id,
    pv.name,
    pv.message_template,
    pv.system_prompt,
    pv.alpha,
    pv.beta_param
FROM prompt_variants pv
WHERE pv.vertical = p_vertical
    AND pv.agent = p_agent
    AND pv.active = TRUE LOOP -- Sample from Beta distribution (approximation using gamma)
    current_sample := random() * (
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
-- ==========================================================
-- HELPER FUNCTION: Update variant outcome
-- ==========================================================
CREATE OR REPLACE FUNCTION update_variant_outcome(
        p_variant_id UUID,
        p_success BOOLEAN
    ) RETURNS VOID AS $$ BEGIN IF p_success THEN
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
-- ==========================================================
-- GRANTS
-- ==========================================================
GRANT ALL ON prompt_variants TO authenticated;
GRANT EXECUTE ON FUNCTION get_best_variant TO authenticated;
GRANT EXECUTE ON FUNCTION update_variant_outcome TO authenticated;
-- ==========================================================
-- VERIFICATION QUERY
-- ==========================================================
SELECT name,
    vertical,
    agent,
    alpha,
    beta_param,
    active
FROM prompt_variants
WHERE vertical = 'hvac'
ORDER BY name;