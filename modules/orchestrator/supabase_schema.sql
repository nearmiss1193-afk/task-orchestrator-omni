-- Create the leads table for AI Service Co
CREATE TABLE IF NOT EXISTS public.leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    website_url TEXT,
    personalized_copy TEXT,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Add a helpful index on email for quick lookups
CREATE INDEX IF NOT EXISTS idx_leads_email ON public.leads(email);

-- Enable Row Level Security (RLS) as a best practice
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows anyone to insert leads (for the website form)
-- Note: In production, you might want more restrictive policies.
CREATE POLICY "Allow public insert" ON public.leads
    FOR INSERT WITH CHECK (true);

-- Create a policy that allows service role to read/manage all
-- (This is default for service_role, but good to be explicit for authenticated admins if needed)
CREATE POLICY "Allow authenticated read" ON public.leads
    FOR SELECT USING (auth.role() = 'authenticated');
