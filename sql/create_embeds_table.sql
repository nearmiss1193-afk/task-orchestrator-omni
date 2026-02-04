-- Create embeds table for Single Source of Truth
CREATE TABLE IF NOT EXISTS embeds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type TEXT NOT NULL UNIQUE,
    -- e.g. 'form', 'calendar', 'widget_emoji'
    code TEXT NOT NULL,
    -- The HTML embed code
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Insert real GHL Form Code
INSERT INTO embeds (type, code)
VALUES (
        'form',
        '<div class="ghl-form" data-id="RnK4OjX0oDcqtWw0VyLr"></div><script src="https://link.msgsndr.com/js/form_embed.js"></script>'
    ) ON CONFLICT (type) DO
UPDATE
SET code = EXCLUDED.code;
-- Insert real GHL Calendar Code
INSERT INTO embeds (type, code)
VALUES (
        'calendar',
        '<iframe src="https://calendar.gohighlevel.com/v2/preview/M7YwDClf34RsNhPQfhS7" width="100%" height="600" frameborder="0"></iframe>'
    ) ON CONFLICT (type) DO
UPDATE
SET code = EXCLUDED.code;
-- Insert Widget Emoji
INSERT INTO embeds (type, code)
VALUES ('widget_emoji', '⚡') ON CONFLICT (type) DO
UPDATE
SET code = EXCLUDED.code;
token: `sov-audit-2026-ghost`