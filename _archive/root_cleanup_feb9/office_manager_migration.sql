
-- Office Manager Inventory
CREATE TABLE IF NOT EXISTS office_inventory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    item_name TEXT NOT NULL UNIQUE,
    quantity INTEGER DEFAULT 0,
    unit TEXT DEFAULT 'units',
    min_threshold INTEGER DEFAULT 5,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Office Manager Tasks
CREATE TABLE IF NOT EXISTS office_tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, in_progress, done
    assigned_by TEXT DEFAULT 'system',
    due_date TIMESTAMPTZ
);

-- RLS Policies (Open for now/Authenticated)
ALTER TABLE office_inventory ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public Access" ON office_inventory FOR ALL USING (true);

ALTER TABLE office_tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public Access" ON office_tasks FOR ALL USING (true);
