-- Ensure contacts_master exists
CREATE TABLE IF NOT EXISTS public.contacts_master (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamptz DEFAULT now(),
    full_name text,
    email_address text,
    phone_number text,
    company_name text,
    industry text,
    city text,
    state text,
    lead_score float,
    status text,
    tags text [],
    ghl_contact_id text UNIQUE,
    raw_research jsonb DEFAULT '{}'::jsonb
);
ALTER TABLE public.contacts_master ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM pg_policies
    WHERE tablename = 'contacts_master'
        AND policyname = 'Service Role Full Access Contacts'
) THEN CREATE POLICY "Service Role Full Access Contacts" ON public.contacts_master AS PERMISSIVE FOR ALL TO service_role USING (true) WITH CHECK (true);
END IF;
END $$;