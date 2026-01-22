import os
import asyncio
from typing import Dict, Any
from supabase import create_client, Client

class V2MetricsAPI:
    """
    v2 METRICS API
    Provides real-time system vitals for the Sovereign Command Center.
    """

    def __init__(self):
        self.supabase = self._get_supabase()

    def _get_supabase(self) -> Client:
        url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        return create_client(url, key)

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Aggregate stats from Supabase."""
        
        # 1. Pipeline Stats
        res_contacted = self.supabase.table("contacts_master").select("id", count="exact").eq("status", "contacted").execute()
        res_new = self.supabase.table("contacts_master").select("id", count="exact").eq("status", "new").execute()
        
        # 2. Revenue Calculation (Mocked: 197 * number of 'deposited' leads)
        # In production: sum from a 'payments' table
        res_paid = self.supabase.table("contacts_master").select("id", count="exact").eq("status", "deposited").execute()
        revenue = (res_paid.count or 0) * 197

        # 3. Recent Activity (Last 5 leads)
        res_recent = self.supabase.table("contacts_master") \
            .select("full_name, company_name, status, last_contact_at") \
            .order("last_contact_at", desc=True) \
            .limit(5) \
            .execute()

        return {
            "vitals": {
                "system_status": "ONLINE",
                "revenue_total": f"${revenue}",
                "leads_contacted": res_contacted.count or 0,
                "leads_pending": res_new.count or 0,
                "agents_active": 3  # Predator, Sarah, Architect
            },
            "recent_activity": res_recent.data or []
        }

# Global instance
metrics = V2MetricsAPI()
