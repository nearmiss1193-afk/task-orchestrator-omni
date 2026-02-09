-- Unified Lead Source of Truth Table
CREATE TABLE IF NOT EXISTS public.master_lead_dossier (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamptz DEFAULT now(),
    contact_id uuid REFERENCES public.contacts_master(id) ON DELETE CASCADE UNIQUE,
    resend_email_id text,
    email_open_count integer DEFAULT 0,
    email_click_count integer DEFAULT 0,
    last_email_status text,
    ghl_opportunity_id text,
    ghl_pipeline_stage text,
    ghl_status text,
    last_synced_at timestamptz DEFAULT now()
);
-- Enable RLS
ALTER TABLE public.master_lead_dossier ENABLE ROW LEVEL SECURITY;
-- Grant access to service role
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM pg_policies
    WHERE tablename = 'master_lead_dossier'
        AND policyname = 'Service Role Full Access Dossier'
) THEN CREATE POLICY "Service Role Full Access Dossier" ON public.master_lead_dossier AS PERMISSIVE FOR ALL TO service_role USING (true) WITH CHECK (true);
END IF;
END $$;