-- MISSION: LAKELAND LOCAL OS - BULKHEAD ISOLATION SCHEMA
-- Date: Feb 2, 2026
-- Goal: Decouple community directory from Sovereign Empire core.
-- 1. Business Directory Table
CREATE TABLE IF NOT EXISTS lakeland_directory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    place_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category TEXT,
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    phone TEXT,
    website TEXT,
    rating DECIMAL,
    user_ratings_total INTEGER,
    price_level INTEGER,
    is_open_now BOOLEAN DEFAULT false,
    -- ENRICHMENT (STRUCTURED SIGNALS)
    wifi_quality TEXT,
    -- unknown/ok/great
    work_friendly BOOLEAN,
    quiet_level TEXT,
    -- low/med/high
    atmosphere_tags TEXT [],
    best_for TEXT [],
    -- ['remote_work', 'families', etc]
    short_summary TEXT,
    -- METADATA
    raw_data JSONB,
    last_ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_enriched_at TIMESTAMP WITH TIME ZONE
);
-- 2. Reviews Table (Isolated)
CREATE TABLE IF NOT EXISTS lakeland_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    place_id TEXT REFERENCES lakeland_directory(place_id),
    rating DECIMAL,
    text TEXT,
    author_name TEXT,
    timestamp TIMESTAMP WITH TIME ZONE,
    raw_provider_payload JSONB
);
-- 3. Ingestion Ledger (Prevents redundant API calls)
CREATE TABLE IF NOT EXISTS lakeland_ingestion_ledger (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    grid_point TEXT,
    -- "lat,lng"
    category TEXT,
    last_run_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    yield_count INTEGER
);
-- 4. Enable RLS (Security First)
ALTER TABLE lakeland_directory ENABLE ROW LEVEL SECURITY;
ALTER TABLE lakeland_reviews ENABLE ROW LEVEL SECURITY;
-- Allow public read Access (Consumer Directory)
CREATE POLICY "Allow public read for directory" ON lakeland_directory FOR
SELECT USING (true);
CREATE POLICY "Allow public read for reviews" ON lakeland_reviews FOR
SELECT USING (true);
COMMENT ON TABLE lakeland_directory IS 'Isolated community directory for Lakeland, FL - Part of Lakeland Local OS';