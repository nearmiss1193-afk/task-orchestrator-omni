-- SOCIAL MEDIA AUTOMATION TABLES
-- Run this in Supabase SQL Editor
-- Social Posts: Track all social media posts
CREATE TABLE IF NOT EXISTS social_posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    platform TEXT NOT NULL CHECK (
        platform IN (
            'facebook',
            'instagram',
            'youtube',
            'tiktok',
            'google_business'
        )
    ),
    post_type TEXT NOT NULL,
    content TEXT NOT NULL,
    media_url TEXT,
    hashtags TEXT [] DEFAULT '{}',
    scheduled_at TIMESTAMPTZ,
    posted_at TIMESTAMPTZ,
    status TEXT DEFAULT 'pending' CHECK (
        status IN ('pending', 'scheduled', 'posted', 'failed')
    ),
    post_id TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    engagement_likes INTEGER DEFAULT 0,
    engagement_comments INTEGER DEFAULT 0,
    engagement_shares INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);
-- Content Calendar: Plan content in advance
CREATE TABLE IF NOT EXISTS content_calendar (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    date DATE NOT NULL,
    platform TEXT NOT NULL,
    post_type TEXT NOT NULL,
    content_id UUID REFERENCES social_posts(id),
    status TEXT DEFAULT 'planned' CHECK (
        status IN (
            'planned',
            'generated',
            'scheduled',
            'posted',
            'failed'
        )
    ),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Social Accounts: Track connected accounts
CREATE TABLE IF NOT EXISTS social_accounts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    platform TEXT NOT NULL UNIQUE,
    account_id TEXT,
    account_name TEXT,
    access_token_expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    last_post_at TIMESTAMPTZ,
    follower_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Content Templates: Reusable templates for each post type
CREATE TABLE IF NOT EXISTS content_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    post_type TEXT NOT NULL,
    platform TEXT,
    template TEXT NOT NULL,
    variables TEXT [] DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    times_used INTEGER DEFAULT 0,
    avg_engagement FLOAT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Create indexes
CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_posts(status);
CREATE INDEX IF NOT EXISTS idx_social_posts_platform ON social_posts(platform);
CREATE INDEX IF NOT EXISTS idx_social_posts_posted_at ON social_posts(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_calendar_date ON content_calendar(date);
-- Enable RLS
ALTER TABLE social_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_calendar ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_templates ENABLE ROW LEVEL SECURITY;
-- Service role access
CREATE POLICY "Service role full access" ON social_posts FOR ALL USING (true);
CREATE POLICY "Service role full access" ON content_calendar FOR ALL USING (true);
CREATE POLICY "Service role full access" ON social_accounts FOR ALL USING (true);
CREATE POLICY "Service role full access" ON content_templates FOR ALL USING (true);
-- Insert default content templates
INSERT INTO content_templates (post_type, platform, template, variables)
VALUES (
        'market_monday',
        'all',
        '📊 Market Monday: {headline}\n\n{insight_1}\n{insight_2}\n\n💡 Use AI to automate your {industry} business!\n\n{hashtags}',
        ARRAY ['headline', 'insight_1', 'insight_2', 'industry', 'hashtags']
    ),
    (
        'tips_tuesday',
        'all',
        '💡 Tips Tuesday: {tip_title}\n\n{tip_explanation}\n\n{call_to_action}\n\n{hashtags}',
        ARRAY ['tip_title', 'tip_explanation', 'call_to_action', 'hashtags']
    ),
    (
        'listing_wednesday',
        'all',
        '🚀 Feature Spotlight: {package_name}\n\n{benefit_1}\n{benefit_2}\n{benefit_3}\n\n📞 Book your demo: {booking_link}\n\n{hashtags}',
        ARRAY ['package_name', 'benefit_1', 'benefit_2', 'benefit_3', 'booking_link', 'hashtags']
    ),
    (
        'faq_friday',
        'all',
        '❓ FAQ Friday: "{question}"\n\n{answer}\n\n{hashtags}',
        ARRAY ['question', 'answer', 'hashtags']
    ),
    (
        'showcase_saturday',
        'all',
        '✨ Saturday Showcase: {case_study_title}\n\n📈 Results:\n{result_1}\n{result_2}\n\n{call_to_action}\n\n{hashtags}',
        ARRAY ['case_study_title', 'result_1', 'result_2', 'call_to_action', 'hashtags']
    ),
    (
        'community_sunday',
        'all',
        '🌟 Happy Sunday, {community}!\n\n{message}\n\n{hashtags}',
        ARRAY ['community', 'message', 'hashtags']
    ) ON CONFLICT DO NOTHING;