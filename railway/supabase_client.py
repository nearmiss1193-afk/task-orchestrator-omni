"""
Supabase Client - Shared database connection for all Railway workers
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    """Get authenticated Supabase client using SERVICE_ROLE key"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")  # Must be service_role, not anon!
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    
    return create_client(url, key)


# Singleton client
_client = None

def get_client() -> Client:
    """Get or create Supabase client singleton"""
    global _client
    if _client is None:
        _client = get_supabase_client()
    return _client


# Helper functions for common operations
def get_new_leads(limit: int = 100) -> list:
    """Get leads with status='new' for prospecting"""
    client = get_client()
    result = client.table("contacts_master") \
        .select("*") \
        .eq("status", "new") \
        .limit(limit) \
        .execute()
    return result.data


def get_enrichable_leads(limit: int = 50) -> list:
    """Get leads that need enrichment (status='new' with no audit data)"""
    client = get_client()
    result = client.table("contacts_master") \
        .select("*") \
        .eq("status", "new") \
        .is_("pagespeed_score", "null") \
        .limit(limit) \
        .execute()
    return result.data


def get_outreachable_leads(limit: int = 50) -> list:
    """Get leads ready for outreach (status='enriched')"""
    client = get_client()
    result = client.table("contacts_master") \
        .select("*") \
        .eq("status", "enriched") \
        .limit(limit) \
        .execute()
    return result.data


def update_lead_status(lead_id: str, status: str, extra_data: dict = None):
    """Update lead status and optionally other fields"""
    client = get_client()
    data = {"status": status}
    if extra_data:
        data.update(extra_data)
    
    return client.table("contacts_master") \
        .update(data) \
        .eq("id", lead_id) \
        .execute()


def insert_lead(lead_data: dict):
    """Insert a new lead into contacts_master"""
    client = get_client()
    return client.table("contacts_master") \
        .insert(lead_data) \
        .execute()


def log_outbound_touch(contact_id: str, touch_type: str, touch_status: str = "sent", report_data: dict = None):
    """Log an outreach touch to outbound_touches"""
    client = get_client()
    data = {
        "contact_id": contact_id,
        "touch_type": touch_type,
        "touch_status": touch_status,
        "report_data": report_data or {}
    }
    return client.table("outbound_touches") \
        .insert(data) \
        .execute()


def check_recent_touch(contact_id: str, days: int = 7) -> bool:
    """Check if lead was already contacted recently (avoid duplicates)"""
    client = get_client()
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    result = client.table("outbound_touches") \
        .select("id") \
        .eq("contact_id", contact_id) \
        .gte("sent_at", cutoff) \
        .limit(1) \
        .execute()
    
    return len(result.data) > 0


if __name__ == "__main__":
    # Quick test
    client = get_client()
    print("✅ Supabase connection successful")
    
    # Test query
    result = client.table("contacts_master").select("id", count="exact").limit(1).execute()
    print(f"✅ contacts_master has {result.count} rows")
