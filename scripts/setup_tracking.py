"""Create email_tracking table in Supabase for comprehensive tracking"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
s = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# Check if email_tracking table exists
try:
    test = s.table("email_tracking").select("id").limit(1).execute()
    print("email_tracking table already exists")
except Exception as e:
    if "does not exist" in str(e) or "42P01" in str(e):
        print("email_tracking table does not exist. Creating via SQL...")
        # We'll need to create it via dashboard or raw SQL
        print("""
Please run this SQL in Supabase dashboard (SQL Editor):

CREATE TABLE IF NOT EXISTS email_tracking (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    contact_id UUID REFERENCES contacts_master(id),
    resend_email_id TEXT,
    event_type TEXT NOT NULL,  -- sent, delivered, opened, clicked, bounced, complained
    subject_variant TEXT,      -- A/B test variant tracking
    subject_text TEXT,         -- actual subject used
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_email_tracking_contact ON email_tracking(contact_id);
CREATE INDEX idx_email_tracking_event ON email_tracking(event_type);
CREATE INDEX idx_email_tracking_created ON email_tracking(created_at);

-- Also ensure email_opens table has the right structure
CREATE TABLE IF NOT EXISTS email_opens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email_id TEXT,
    recipient_email TEXT,
    business_name TEXT,
    opened_at TIMESTAMPTZ DEFAULT NOW()
);
        """)
    else:
        print(f"Error: {e}")

# Check email_opens too
try:
    test = s.table("email_opens").select("id").limit(1).execute()
    print(f"email_opens table exists, has {len(test.data)} rows")
except Exception as e:
    print(f"email_opens: {e}")

# Check outbound_touches columns
sample = s.table("outbound_touches").select("*").limit(1).execute()
if sample.data:
    print(f"\noutbound_touches columns: {sorted(sample.data[0].keys())}")
