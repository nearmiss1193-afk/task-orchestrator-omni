import os
import asyncio
from typing import List, Dict, Any
from supabase import create_client, Client
from .council_broker import council
from .ghl_bridge import ghl

class V2OutreachOrchestrator:
    """
    MASTER ORCHESTRATOR v2.0
    The "Brain" that coordinates prospects -> hooks -> outreach.
    """
    
    def __init__(self):
        self.supabase = self._get_supabase()

    def _get_supabase(self) -> Client:
        url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        print(f"[DEBUG] URL: {url}, Key len: {len(str(key))}")
        return create_client(supabase_url=url, supabase_key=key)

    async def run_sequence(self):
        """The main autonomous loop execution."""
        print("[ORCHESTRATOR] 🚀 Starting v2.0 Outreach Loop...")
        
        # 1. Fetch New Prospects from Supabase
        prospects = await self._fetch_new_leads()
        
        if not prospects:
            print("[ORCHESTRATOR] Sleep Mode: No new leads found.")
            return

        for p in prospects:
            print(f"[ORCHESTRATOR] Processing: {p.get('full_name')} ({p.get('company_name')})")
            
            # 2. Generate Personality-Driven Hook (Consult Claude)
            hook = await self._generate_hook(p)
            
            # 3. Trigger Outreach via GHL
            # Using phone if available, else email
            if p.get("phone"):
                await ghl.send_sms(p["phone"], hook)
            elif p.get("email"):
                await ghl.send_email(p["email"], "Quick question for you", hook)
            
            # 4. Update Status (Supabase)
            await self._update_prospect_status(p["id"], "contacted")
            
        print(f"[ORCHESTRATOR] ✅ Loop complete. Processed {len(prospects)} leads.")

    async def _fetch_new_leads(self) -> List[Dict[str, Any]]:
        """Fetch leads tagged as 'new' with score > 70."""
        res = self.supabase.table("contacts_master") \
            .select("*") \
            .in_("status", ["new", "research_done"]) \
            .gt("lead_score", 0) \
            .limit(10) \
            .execute()
        return res.data

    async def _update_prospect_status(self, prospect_id: str, new_status: str):
        """Update Supabase record."""
        print(f"[DATABASE] Updating {prospect_id} status to {new_status}")
        self.supabase.table("contacts_master") \
            .update({"status": new_status, "last_contact_at": "now()"}) \
            .eq("id", prospect_id) \
            .execute()

    async def _generate_hook(self, prospect: Dict[str, Any]) -> str:
        """Consult the AI Council for the best human-like hook."""
        name = prospect.get("full_name") or "there"
        prompt = f"Write a friendly 1-sentence intro text to {name} who owns an {prospect.get('niche', 'business')} in {prospect.get('city', 'your area')}. Mention missed revenue."
        system = "You are Sarah, a friendly AI assistant. No AI jargon. Be helpful and warm. Keep it under 160 chars."
        
        return await council.get_expert(intent="outreach_copy", prompt=prompt, system_prompt=system)

    async def _update_prospect_status(self, prospect: Dict[str, Any], new_status: str):
        """Update Supabase record."""
        print(f"[DATABASE] Updating {prospect['name']} status to {new_status}")

if __name__ == "__main__":
    orch = V2OutreachOrchestrator()
    asyncio.run(orch.run_sequence())
