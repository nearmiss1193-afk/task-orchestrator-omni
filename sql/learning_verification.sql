-- ============================================================
-- SYSTEM LEARNING VERIFICATION - Jan 18, 2026
-- Run each block separately in Supabase SQL Editor
-- ============================================================
-- ============================================================
-- BLOCK 1: Event Summary (Last 50 types + 24h counts)
-- ============================================================
WITH event_summary AS (
    SELECT type,
        COUNT(*) as total_count,
        MAX(ts) as last_seen,
        COUNT(*) FILTER (
            WHERE ts > NOW() - INTERVAL '24 hours'
        ) as last_24h
    FROM event_log_v2
    GROUP BY type
    ORDER BY last_seen DESC
    LIMIT 50
), appointment_counts AS (
    SELECT 'appointment.created' as metric,
        COUNT(*) as count_24h
    FROM event_log_v2
    WHERE type = 'appointment.created'
        AND ts > NOW() - INTERVAL '24 hours'
    UNION ALL
    SELECT 'appointment.updated',
        COUNT(*)
    FROM event_log_v2
    WHERE type = 'appointment.updated'
        AND ts > NOW() - INTERVAL '24 hours'
),
sms_counts AS (
    SELECT 'sms.sent' as metric,
        COUNT(*) as count_24h
    FROM event_log_v2
    WHERE type = 'sms.sent'
        AND ts > NOW() - INTERVAL '24 hours'
    UNION ALL
    SELECT 'sms.failed',
        COUNT(*)
    FROM event_log_v2
    WHERE type = 'sms.failed'
        AND ts > NOW() - INTERVAL '24 hours'
),
call_counts AS (
    SELECT 'call.*' as metric,
        COUNT(*) as count_24h
    FROM event_log_v2
    WHERE type LIKE 'call.%'
        AND ts > NOW() - INTERVAL '24 hours'
)
SELECT '=== EVENT TYPES (Last 50) ===' as section,
    NULL::text as metric,
    NULL::bigint as count_24h,
    NULL::timestamp as last_seen
UNION ALL
SELECT type,
    type,
    total_count,
    last_seen
FROM event_summary
UNION ALL
SELECT '=== 24H COUNTS ===' as section,
    NULL,
    NULL,
    NULL
UNION ALL
SELECT metric,
    metric,
    count_24h,
    NULL
FROM appointment_counts
UNION ALL
SELECT metric,
    metric,
    count_24h,
    NULL
FROM sms_counts
UNION ALL
SELECT metric,
    metric,
    count_24h,
    NULL
FROM call_counts;
-- ============================================================
-- BLOCK 2: Variant Tracking Check
-- ============================================================
-- 2A: Check event_log_v2 for variant_id in payload
SELECT type,
    ts,
    payload->>'variant_id' as variant_id,
    payload->>'variant_name' as variant_name,
    payload->>'campaign_id' as campaign_id,
    payload->>'ab_variant' as ab_variant
FROM event_log_v2
WHERE payload->>'variant_id' IS NOT NULL
    OR payload->>'variant_name' IS NOT NULL
    OR payload->>'ab_variant' IS NOT NULL
ORDER BY ts DESC
LIMIT 20;
-- 2B: Check if interactions table exists and has variants
SELECT 'interactions' as table_name,
    COUNT(*) as row_count,
    COUNT(*) FILTER (
        WHERE variant_id IS NOT NULL
    ) as with_variant
FROM interactions
WHERE EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'interactions'
    );
-- 2C: Check if outreach_attribution table exists
SELECT table_name,
    column_name
FROM information_schema.columns
WHERE table_name IN (
        'interactions',
        'outreach_attribution',
        'ab_tests',
        'campaign_variants'
    )
ORDER BY table_name,
    ordinal_position;
-- ============================================================
-- BLOCK 3: Recent Events Detail (Debug)
-- ============================================================
SELECT id,
    type,
    source,
    severity,
    ts,
    entity_id,
    correlation_id,
    payload
FROM event_log_v2
ORDER BY ts DESC
LIMIT 30;
-- ============================================================
-- BLOCK 4: SMS Sent Today (Verify 21 messages)
-- ============================================================
SELECT type,
    ts,
    entity_id,
    payload->>'phone' as phone,
    payload->>'contact_name' as contact_name,
    payload->>'variant_id' as variant_id,
    payload->>'company_name' as company_name
FROM event_log_v2
WHERE type IN ('sms.sent', 'sms.queued', 'campaign.sms.sent')
    AND ts > NOW() - INTERVAL '24 hours'
ORDER BY ts DESC
LIMIT 30;