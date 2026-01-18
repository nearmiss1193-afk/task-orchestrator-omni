-- ==========================================================
-- CONTENT ENGINE DB HARDENING
-- Cloud-safe content lifecycle with gated publishing
-- Run this in Supabase SQL Editor
-- ==========================================================
-- ============================================
-- PART A: EXISTING SCHEMA (IF NOT EXISTS)
-- Safe re-run of content_library_schema.sql
-- ============================================
-- Content Library: Stores all generated/uploaded content
CREATE TABLE IF NOT EXISTS content_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL CHECK (type IN ('video', 'image', 'text', 'audio')),
    source TEXT NOT NULL,
    title TEXT,
    description TEXT,
    file_url TEXT,
    thumbnail_url TEXT,
    local_path TEXT,
    duration_seconds INT,
    resolution TEXT,
    aspect_ratio TEXT,
    file_size_bytes BIGINT,
    mime_type TEXT,
    prompt TEXT,
    style TEXT,
    generation_config JSONB,
    estimated_cost DECIMAL(10, 2),
    platforms_posted TEXT [] DEFAULT '{}',
    times_used INT DEFAULT 0,
    performance JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Social Posts: Tracks all posts across platforms
CREATE TABLE IF NOT EXISTS social_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content_library(id) ON DELETE
    SET NULL,
        platform TEXT NOT NULL,
        platform_post_id TEXT,
        platform_account_id TEXT,
        caption TEXT,
        hashtags TEXT [],
        mentions TEXT [],
        link TEXT,
        scheduled_at TIMESTAMPTZ,
        posted_at TIMESTAMPTZ,
        status TEXT DEFAULT 'draft' CHECK (
            status IN (
                'draft',
                'scheduled',
                'posting',
                'posted',
                'failed'
            )
        ),
        error_message TEXT,
        engagement JSONB DEFAULT '{}',
        last_engagement_sync TIMESTAMPTZ,
        api_provider TEXT,
        api_response JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Social Comments: Tracks comments/replies for engagement
CREATE TABLE IF NOT EXISTS social_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES social_posts(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    platform_comment_id TEXT,
    parent_comment_id TEXT,
    author_id TEXT,
    author_name TEXT,
    author_profile_url TEXT,
    content TEXT NOT NULL,
    sentiment TEXT CHECK (
        sentiment IN ('positive', 'negative', 'neutral', 'question')
    ),
    intent TEXT,
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    responded BOOLEAN DEFAULT FALSE,
    response TEXT,
    response_at TIMESTAMPTZ,
    responded_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Social DMs: Direct message tracking
CREATE TABLE IF NOT EXISTS social_dms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform TEXT NOT NULL,
    conversation_id TEXT,
    contact_id UUID,
    contact_name TEXT,
    contact_handle TEXT,
    direction TEXT CHECK (direction IN ('inbound', 'outbound')),
    content TEXT NOT NULL,
    sentiment TEXT,
    intent TEXT,
    requires_response BOOLEAN DEFAULT FALSE,
    responded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Content Performance: Aggregated metrics
CREATE TABLE IF NOT EXISTS content_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content_library(id) ON DELETE CASCADE,
    total_views INT DEFAULT 0,
    total_likes INT DEFAULT 0,
    total_comments INT DEFAULT 0,
    total_shares INT DEFAULT 0,
    total_saves INT DEFAULT 0,
    total_clicks INT DEFAULT 0,
    engagement_rate DECIMAL(5, 4),
    metrics_by_platform JSONB DEFAULT '{}',
    first_posted_at TIMESTAMPTZ,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);
-- ============================================
-- PART B: NEW GATING & QUEUE TABLES
-- ============================================
-- Content Approvals: Manual/auto approval gate before publishing
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
    -- 'human', 'auto', or user email
    approved_at TIMESTAMPTZ,
    rejected_reason TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Posting Rules: Platform-specific publishing gates
-- CRITICAL: This controls when/if content can be published
CREATE TABLE IF NOT EXISTS posting_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform TEXT UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    -- Must explicitly enable to post
    cadence_per_day INT DEFAULT 1,
    -- Max posts per day
    window_start_hour INT DEFAULT 9,
    -- Start posting at 9am local
    window_end_hour INT DEFAULT 17,
    -- Stop posting at 5pm local
    weekdays_only BOOLEAN DEFAULT TRUE,
    -- No weekend posts by default
    min_hours_between_posts INT DEFAULT 4,
    -- Minimum gap between posts
    require_approval BOOLEAN DEFAULT TRUE,
    -- Require approval before posting
    last_posted_at TIMESTAMPTZ,
    -- Track last post time for cadence
    posts_today INT DEFAULT 0,
    -- Counter reset daily
    posts_today_date DATE,
    -- Date for counter reset
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Content Queue: Scheduled content actions
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
    -- Target platform
    scheduled_for TIMESTAMPTZ,
    -- When to execute
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
    max_attempts INT DEFAULT 3,
    last_error TEXT,
    result JSONB,
    -- Store action result
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);
-- ============================================
-- PART C: DEFAULT POSTING RULES (DISABLED)
-- All platforms start disabled for safety
-- ============================================
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
-- PART D: INDEXES
-- ============================================
-- Existing indexes (safe re-create)
CREATE INDEX IF NOT EXISTS idx_content_library_type ON content_library(type);
CREATE INDEX IF NOT EXISTS idx_content_library_source ON content_library(source);
CREATE INDEX IF NOT EXISTS idx_content_library_created ON content_library(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_posts_platform ON social_posts(platform);
CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_posts(status);
CREATE INDEX IF NOT EXISTS idx_social_posts_scheduled ON social_posts(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_social_posts_content ON social_posts(content_id);
CREATE INDEX IF NOT EXISTS idx_social_comments_post ON social_comments(post_id);
CREATE INDEX IF NOT EXISTS idx_social_comments_responded ON social_comments(responded);
CREATE INDEX IF NOT EXISTS idx_social_comments_priority ON social_comments(priority);
CREATE INDEX IF NOT EXISTS idx_social_dms_platform ON social_dms(platform);
CREATE INDEX IF NOT EXISTS idx_social_dms_requires_response ON social_dms(requires_response);
-- New indexes for approvals and queue
CREATE INDEX IF NOT EXISTS idx_content_approvals_status ON content_approvals(status);
CREATE INDEX IF NOT EXISTS idx_content_approvals_content ON content_approvals(content_id);
CREATE INDEX IF NOT EXISTS idx_content_queue_status ON content_queue(status);
CREATE INDEX IF NOT EXISTS idx_content_queue_scheduled ON content_queue(scheduled_for);
CREATE INDEX IF NOT EXISTS idx_content_queue_action ON content_queue(action);
CREATE INDEX IF NOT EXISTS idx_posting_rules_enabled ON posting_rules(enabled);
-- ============================================
-- PART E: HELPER FUNCTIONS
-- ============================================
-- Check if posting is allowed for a platform right now
CREATE OR REPLACE FUNCTION can_post_now(p_platform TEXT) RETURNS BOOLEAN AS $$
DECLARE rule posting_rules %ROWTYPE;
current_hour INT;
is_weekday BOOLEAN;
BEGIN
SELECT * INTO rule
FROM posting_rules
WHERE platform = p_platform;
IF NOT FOUND
OR NOT rule.enabled THEN RETURN FALSE;
END IF;
current_hour := EXTRACT(
    HOUR
    FROM NOW()
);
is_weekday := EXTRACT(
    DOW
    FROM NOW()
) BETWEEN 1 AND 5;
-- Check weekday restriction
IF rule.weekdays_only
AND NOT is_weekday THEN RETURN FALSE;
END IF;
-- Check time window
IF current_hour < rule.window_start_hour
OR current_hour >= rule.window_end_hour THEN RETURN FALSE;
END IF;
-- Check cadence (reset counter if new day)
IF rule.posts_today_date IS NULL
OR rule.posts_today_date < CURRENT_DATE THEN
UPDATE posting_rules
SET posts_today = 0,
    posts_today_date = CURRENT_DATE
WHERE platform = p_platform;
RETURN TRUE;
END IF;
-- Check if under daily limit
IF rule.posts_today >= rule.cadence_per_day THEN RETURN FALSE;
END IF;
-- Check minimum gap between posts
IF rule.last_posted_at IS NOT NULL
AND NOW() - rule.last_posted_at < (rule.min_hours_between_posts || ' hours')::INTERVAL THEN RETURN FALSE;
END IF;
RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
-- Record a post (updates counters and last_posted_at)
CREATE OR REPLACE FUNCTION record_post(p_platform TEXT) RETURNS VOID AS $$ BEGIN
UPDATE posting_rules
SET last_posted_at = NOW(),
    posts_today = CASE
        WHEN posts_today_date = CURRENT_DATE THEN posts_today + 1
        ELSE 1
    END,
    posts_today_date = CURRENT_DATE,
    updated_at = NOW()
WHERE platform = p_platform;
END;
$$ LANGUAGE plpgsql;
-- Get next queued item for processing
CREATE OR REPLACE FUNCTION get_next_queue_item() RETURNS content_queue AS $$
DECLARE item content_queue %ROWTYPE;
BEGIN
SELECT * INTO item
FROM content_queue
WHERE status = 'queued'
    AND (
        scheduled_for IS NULL
        OR scheduled_for <= NOW()
    )
    AND attempts < max_attempts
ORDER BY scheduled_for NULLS LAST,
    created_at
LIMIT 1 FOR
UPDATE SKIP LOCKED;
IF FOUND THEN
UPDATE content_queue
SET status = 'processing',
    attempts = attempts + 1
WHERE id = item.id;
END IF;
RETURN item;
END;
$$ LANGUAGE plpgsql;
-- ============================================
-- PART F: GRANTS
-- ============================================
GRANT ALL ON content_library TO authenticated;
GRANT ALL ON social_posts TO authenticated;
GRANT ALL ON social_comments TO authenticated;
GRANT ALL ON social_dms TO authenticated;
GRANT ALL ON content_performance TO authenticated;
GRANT ALL ON content_approvals TO authenticated;
GRANT ALL ON posting_rules TO authenticated;
GRANT ALL ON content_queue TO authenticated;
GRANT EXECUTE ON FUNCTION can_post_now TO authenticated;
GRANT EXECUTE ON FUNCTION record_post TO authenticated;
GRANT EXECUTE ON FUNCTION get_next_queue_item TO authenticated;
-- ============================================
-- VERIFICATION QUERIES (Run after migration)
-- ============================================
-- Query 1: Show new tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name IN (
        'content_library',
        'content_approvals',
        'posting_rules',
        'content_queue',
        'social_posts',
        'social_comments',
        'social_dms',
        'content_performance'
    )
ORDER BY table_name;
-- Query 2: List posting rules
SELECT platform,
    enabled,
    cadence_per_day,
    window_start_hour,
    window_end_hour,
    weekdays_only,
    require_approval
FROM posting_rules
ORDER BY platform;
-- Query 3: List queued jobs (should be empty initially)
SELECT id,
    content_id,
    action,
    platform,
    scheduled_for,
    status,
    attempts
FROM content_queue
WHERE status = 'queued'
ORDER BY scheduled_for NULLS LAST;