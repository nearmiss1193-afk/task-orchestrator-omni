-- =====================================================
-- JAN 18 KICKOFF - SQL VERIFICATION & SETUP
-- Run these blocks in Supabase SQL Editor TONIGHT
-- =====================================================
-- =====================================================
-- BLOCK A1: VERIFY KICKOFF_RUNS HAS 2026-01-18 ROW
-- =====================================================
SELECT date,
    executed,
    created_at
FROM kickoff_runs
WHERE date = '2026-01-18';
-- Expected: 1 row with executed=false
-- =====================================================
-- BLOCK A2: INSERT KICKOFF ROW IF MISSING
-- =====================================================
INSERT INTO kickoff_runs (date, executed)
VALUES ('2026-01-18', false) ON CONFLICT (date) DO NOTHING;
-- Verify:
SELECT *
FROM kickoff_runs
WHERE date = '2026-01-18';
-- =====================================================
-- BLOCK A3: TOMORROW READINESS VIEW
-- =====================================================
-- Run this to get a comprehensive readiness check
SELECT '2026-01-18' as kickoff_date,
    (
        SELECT COUNT(*)
        FROM kickoff_runs
        WHERE date = '2026-01-18'
    ) as kickoff_row_exists,
    (
        SELECT executed
        FROM kickoff_runs
        WHERE date = '2026-01-18'
    ) as kickoff_executed,
    (
        SELECT COUNT(*)
        FROM prompt_variants
        WHERE active = true
    ) as active_variants,
    (
        SELECT COUNT(*)
        FROM prompt_variants
        WHERE active = true
            AND vertical = 'hvac'
    ) as hvac_variants,
    (
        SELECT COUNT(*)
        FROM posting_rules
        WHERE enabled = true
    ) as posting_rules_enabled,
    (
        SELECT COUNT(*)
        FROM posting_rules
        WHERE enabled = false
    ) as posting_rules_disabled;
-- =====================================================
-- BLOCK A4: LAST 10 EVENTS IN EVENT_LOG_V2
-- =====================================================
SELECT id,
    type,
    source,
    severity,
    correlation_id,
    ts,
    payload->>'sent' as sent,
    payload->>'reason' as reason
FROM event_log_v2
ORDER BY ts DESC
LIMIT 10;
-- =====================================================
-- BLOCK A5: VERIFY HVAC VARIANTS ARE SEEDED
-- =====================================================
SELECT id,
    name,
    vertical,
    agent,
    channel,
    alpha,
    beta,
    active,
    LEFT(message_template, 80) as template_preview
FROM prompt_variants
WHERE vertical = 'hvac'
ORDER BY name;
-- Expected: 8 rows (5 SMS, 3 email)
-- =====================================================
-- BLOCK A6: ADD NEW HIGH-CONVERSION VARIANTS (Jan 18)
-- =====================================================
-- These use the diagnostic outreach playbook patterns
INSERT INTO prompt_variants (
        name,
        vertical,
        channel,
        agent,
        message_template,
        alpha,
        beta,
        active
    )
VALUES -- Diagnostic report variants
    (
        'hvac_sms_diagnostic_v1',
        'hvac',
        'sms',
        'sarah',
        'Hi {name}, noticed {company} might be losing calls to slow follow-up. We built a free report with 3 fixes. Want me to send it? -Sarah',
        1,
        1,
        true
    ),
    (
        'hvac_sms_review_v1',
        'hvac',
        'sms',
        'sarah',
        'Hi {name}, your HVAC reviews are at 3.8★ (industry avg 4.5). Quick report shows how to fix that – interested? https://link.aiserviceco.com/discovery -Sarah',
        1,
        1,
        true
    ),
    (
        'hvac_sms_competitor_v1',
        'hvac',
        'sms',
        'sarah',
        'Hi {name}, ran a quick analysis of {company} vs your top competitor. Found 2 easy wins. Free report: https://link.aiserviceco.com/discovery -Sarah',
        1,
        1,
        true
    ),
    (
        'hvac_sms_response_v1',
        'hvac',
        'sms',
        'sarah',
        'Hi {name}, businesses responding within 5 min convert 5x more. How fast is {company}? Free audit: https://link.aiserviceco.com/discovery -Sarah',
        1,
        1,
        true
    ),
    (
        'hvac_sms_curiosity_v1',
        'hvac',
        'sms',
        'sarah',
        'Hi {name} – noticed something interesting about {company}''s HVAC marketing. 2 min to share? -Sarah from AI Service Co',
        1,
        1,
        true
    ) ON CONFLICT (name) DO
UPDATE
SET message_template = EXCLUDED.message_template,
    active = true;
-- Verify new variants:
SELECT name,
    LEFT(message_template, 60) as preview,
    active
FROM prompt_variants
WHERE name LIKE 'hvac_sms_%_v1'
ORDER BY name;
-- =====================================================
-- BLOCK A7: VERIFY OUTREACH_ATTRIBUTION TABLE EXISTS
-- =====================================================
SELECT column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'outreach_attribution'
ORDER BY ordinal_position;
-- =====================================================
-- BLOCK A8: VERIFY POSTING RULES ALL DISABLED
-- =====================================================
SELECT platform,
    enabled,
    cadence_per_day,
    posts_today,
    last_posted_at
FROM posting_rules
ORDER BY platform;
-- All should show enabled=false