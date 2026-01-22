-- AMOS (Autonomous Empire Builder) - Infrastructure Schema
-- 0. Cleanup (Optional but recommended for schema alignment)
DROP TABLE IF EXISTS system_state CASCADE;
-- 1. system_state
-- Tracks the current build status of every component.
CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN ('working', 'broken', 'not_built')),
    last_error TEXT,
    build_attempts INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- 2. system_health
-- Stores high-level system vitals.
CREATE TABLE IF NOT EXISTS system_health (
    id SERIAL PRIMARY KEY,
    metric TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    value TEXT,
    last_checked TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- 3. lessons_learned
-- Prevents repeating the same mistakes.
CREATE TABLE IF NOT EXISTS lessons_learned (
    id SERIAL PRIMARY KEY,
    component_name TEXT NOT NULL,
    failure_mode TEXT NOT NULL,
    solution TEXT NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- 4. buildable_components (View or Table)
-- Components whose dependencies are met and are ready for build.
CREATE TABLE IF NOT EXISTS buildable_components (
    id SERIAL PRIMARY KEY,
    component_name TEXT UNIQUE NOT NULL,
    dependencies TEXT [],
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'pending'
);
-- 5. get_lessons function
CREATE OR REPLACE FUNCTION get_lessons(comp_name TEXT) RETURNS SETOF lessons_learned AS $$ BEGIN RETURN QUERY
SELECT *
FROM lessons_learned
WHERE component_name = comp_name;
END;
$$ LANGUAGE plpgsql;
-- 📊 Initial Seeding
INSERT INTO system_state (key, status, build_attempts)
VALUES ('fusion_backend', 'working', 1),
    ('cloud_prospector', 'working', 1),
    ('scc_dashboard', 'working', 1),
    ('vapi_closer', 'working', 1) ON CONFLICT (key) DO NOTHING;
INSERT INTO system_health (metric, status, value)
VALUES ('Fusion Backend', 'healthy', 'deployed'),
    ('Cloud Prospector', 'healthy', 'cron_active'),
    ('SCC Visibility', 'healthy', 'live') ON CONFLICT (metric) DO NOTHING;
INSERT INTO buildable_components (component_name, dependencies, priority)
VALUES (
        'Automated Reporting',
        ARRAY ['fusion_backend'],
        2
    ),
    (
        'Advanced Neural Prospecting',
        ARRAY ['cloud_prospector'],
        3
    ) ON CONFLICT (component_name) DO NOTHING;