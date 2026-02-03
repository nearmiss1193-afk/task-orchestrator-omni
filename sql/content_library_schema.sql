-- Content Library Schema for Social Command Center
-- Run this in Supabase SQL Editor
-- Content Library: Stores all generated/uploaded content
CREATE TABLE IF NOT EXISTS content_library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL CHECK (type IN ('video', 'image', 'text', 'audio')),
    source TEXT NOT NULL,
    -- 'veo', 'descript', 'inspix', 'manual'
    title TEXT,
    description TEXT,
    -- File storage
    file_url TEXT,
    thumbnail_url TEXT,
    local_path TEXT,
    -- Media metadata
    duration_seconds INT,
    resolution TEXT,
    aspect_ratio TEXT,
    file_size_bytes BIGINT,
    mime_type TEXT,
    -- Generation metadata
    prompt TEXT,
    style TEXT,
    generation_config JSONB,
    estimated_cost DECIMAL(10, 2),
    -- Usage tracking
    platforms_posted TEXT [] DEFAULT '{}',
    times_used INT DEFAULT 0,
    -- Performance
    performance JSONB DEFAULT '{}',
    -- aggregated metrics
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Social Posts: Tracks all posts across platforms
CREATE TABLE IF NOT EXISTS social_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content_library(id) ON DELETE
    SET NULL,
        -- Platform info
        platform TEXT NOT NULL,
        -- 'facebook', 'instagram', 'twitter', etc.
        platform_post_id TEXT,
        -- ID from the platform
        platform_account_id TEXT,
        -- Content
        caption TEXT,
        hashtags TEXT [],
        mentions TEXT [],
        link TEXT,
        -- Scheduling
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
        -- Engagement metrics
        engagement JSONB DEFAULT '{}',
        -- likes, comments, shares, views
        last_engagement_sync TIMESTAMPTZ,
        -- API tracking
        api_provider TEXT,
        -- 'ayrshare', 'ghl'
        api_response JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Social Comments: Tracks comments/replies for engagement
CREATE TABLE IF NOT EXISTS social_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES social_posts(id) ON DELETE CASCADE,
    -- Platform info
    platform TEXT NOT NULL,
    platform_comment_id TEXT,
    parent_comment_id TEXT,
    -- For nested replies
    -- Author
    author_id TEXT,
    author_name TEXT,
    author_profile_url TEXT,
    -- Content
    content TEXT NOT NULL,
    -- Analysis
    sentiment TEXT CHECK (
        sentiment IN ('positive', 'negative', 'neutral', 'question')
    ),
    intent TEXT,
    -- 'praise', 'complaint', 'question', 'interest', 'spam'
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    -- Response tracking
    responded BOOLEAN DEFAULT FALSE,
    response TEXT,
    response_at TIMESTAMPTZ,
    responded_by TEXT,
    -- 'ghost_responder', 'human', 'auto'
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Social DMs: Direct message tracking
CREATE TABLE IF NOT EXISTS social_dms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Platform info
    platform TEXT NOT NULL,
    conversation_id TEXT,
    -- Contact
    contact_id UUID,
    -- Link to contacts_master if exists
    contact_name TEXT,
    contact_handle TEXT,
    -- Message
    direction TEXT CHECK (direction IN ('inbound', 'outbound')),
    content TEXT NOT NULL,
    -- Analysis (for inbound)
    sentiment TEXT,
    intent TEXT,
    -- Response tracking
    requires_response BOOLEAN DEFAULT FALSE,
    responded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Content Performance: Aggregated metrics
CREATE TABLE IF NOT EXISTS content_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content_library(id) ON DELETE CASCADE,
    -- Aggregated metrics
    total_views INT DEFAULT 0,
    total_likes INT DEFAULT 0,
    total_comments INT DEFAULT 0,
    total_shares INT DEFAULT 0,
    total_saves INT DEFAULT 0,
    total_clicks INT DEFAULT 0,
    -- Engagement rate
    engagement_rate DECIMAL(5, 4),
    -- percentage
    -- Platform breakdown
    metrics_by_platform JSONB DEFAULT '{}',
    -- Time tracking
    first_posted_at TIMESTAMPTZ,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for common queries
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
-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER update_content_library_updated_at BEFORE
UPDATE ON content_library FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER update_social_posts_updated_at BEFORE
UPDATE ON social_posts FOR EACH ROW EXECUTE FUNCTION update_updated_at();
-- Grant permissions
GRANT ALL ON content_library TO authenticated;
GRANT ALL ON social_posts TO authenticated;
GRANT ALL ON social_comments TO authenticated;
GRANT ALL ON social_dms TO authenticated;
GRANT ALL ON content_performance TO authenticated;