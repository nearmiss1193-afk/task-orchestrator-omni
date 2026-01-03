-- The "Everything" Lead Table for Omni-Automation
CREATE TABLE IF NOT EXISTS public.contacts_master (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  ghl_contact_id TEXT UNIQUE NOT NULL,
  full_name TEXT,
  email TEXT,
  phone TEXT,
  website_url TEXT,
  
  -- AI Processing Data
  lead_score INT DEFAULT 0, -- 0-100 based on AI fit
  sentiment TEXT, -- 'positive', 'neutral', 'hostile'
  raw_research JSONB, -- Scraped website/social data
  ai_strategy TEXT, -- The "plan" the AI has for this lead
  
  -- Automation Tracking
  last_outreach_at TIMESTAMPTZ,
  appointment_booked BOOLEAN DEFAULT false,
  status TEXT DEFAULT 'new', -- 'nurturing', 'booked', 'closed', 'dq'
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Realtime for instant Agent reactions
ALTER PUBLICATION supabase_realtime ADD TABLE public.contacts_master;

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_contacts_ghl_id ON public.contacts_master(ghl_contact_id);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON public.contacts_master(email);
CREATE INDEX IF NOT EXISTS idx_contacts_status ON public.contacts_master(status);
