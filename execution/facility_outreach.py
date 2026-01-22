"""
Facility Outreach - Partner Recruitment Automation
===================================================

Automated outreach to ALF facilities to build partner network.
Integrates with GHL for email/SMS sequences.

Part of the ALF Referral Agency system.
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

# Self-annealing integration
try:
    from annealing_engine import self_annealing, log_annealing_event
    ANNEALING_ENABLED = True
except ImportError:
    ANNEALING_ENABLED = False
    def self_annealing(func):
        return func

# Try Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Configuration
GHL_API_BASE = "https://services.leadconnectorhq.com"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Email templates
OUTREACH_TEMPLATES = {
    "initial_intro": {
        "subject": "Partnership Opportunity - Senior Referrals for {facility_name}",
        "body": """Hi {contact_name},

I'm reaching out because we work with families in the {city} area who are actively seeking assisted living options for their loved ones.

We've helped place families in quality facilities like yours, and I wanted to explore a potential partnership where we send qualified referrals your way.

**How it works:**
- Families come to us needing placement (often through hospital discharge planners and family referrals)
- We match them with facilities that fit their needs and budget
- We handle the initial intake and qualification
- You receive move-in ready prospects

Would you be open to a brief call this week to discuss how we might work together?

Best regards,
{sender_name}
{company_name}
{phone}"""
    },
    
    "follow_up_1": {
        "subject": "Following up on referral partnership - {facility_name}",
        "body": """Hi {contact_name},

I wanted to follow up on my previous message about sending qualified referrals to {facility_name}.

We currently work with about 5+ families per month seeking placement in the {city} area, and we're looking for quality partners to refer them to.

**What we look for in partners:**
- Good AHCA standing
- Responsive to family tours
- Fair commission structure (typically first month's rent)

Would a 10-minute call work this week to see if there's a fit?

Best,
{sender_name}"""
    },
    
    "value_add": {
        "subject": "Exclusive referral opportunity for {facility_name}",
        "body": """Hi {contact_name},

I have a family actively looking for placement in the next 2 weeks - their requirements match {facility_name}:

- **Care Level:** {care_level}
- **Budget:** ${budget_min}-${budget_max}/month
- **Timeline:** Urgent - within 2 weeks
- **Payment:** Private pay (not Medicaid)

Would you like me to send them your way for a tour?

If you're interested, just reply to this email or call me at {phone}.

Best,
{sender_name}"""
    }
}


class FacilityOutreach:
    """
    Automated facility outreach and partner recruitment.
    """
    
    def __init__(
        self,
        ghl_api_key: Optional[str] = None,
        ghl_location_id: Optional[str] = None
    ):
        """Initialize outreach engine."""
        self.ghl_api_key = ghl_api_key or os.getenv("GHL_API_KEY")
        self.ghl_location_id = ghl_location_id or os.getenv("GHL_LOCATION_ID")
        
        if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_KEY:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.db_connected = True
        else:
            self.supabase = None
            self.db_connected = False
        
        self.company_info = {
            "company_name": os.getenv("COMPANY_NAME", "Sovereign Senior Placement"),
            "sender_name": os.getenv("SENDER_NAME", "Your Name"),
            "phone": os.getenv("COMPANY_PHONE", "(555) 123-4567")
        }
    
    def _ghl_headers(self) -> Dict[str, str]:
        """Get GHL API headers."""
        return {
            "Authorization": f"Bearer {self.ghl_api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }
    
    @self_annealing
    def send_outreach_email(
        self,
        facility_id: str,
        template: str = "initial_intro",
        custom_fields: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send outreach email to a facility.
        
        Args:
            facility_id: Facility ID from database
            template: Email template name
            custom_fields: Additional merge fields
        
        Returns:
            Send status
        """
        if not self.db_connected:
            return {"success": False, "error": "Database not connected"}
        
        # Get facility info
        result = self.supabase.table("alf_facilities").select("*").eq("id", facility_id).execute()
        if not result.data:
            return {"success": False, "error": "Facility not found"}
        
        facility = result.data[0]
        
        if not facility.get("contact_email"):
            return {"success": False, "error": "No contact email for facility"}
        
        # Get template
        email_template = OUTREACH_TEMPLATES.get(template)
        if not email_template:
            return {"success": False, "error": f"Unknown template: {template}"}
        
        # Build merge fields
        merge_fields = {
            "facility_name": facility.get("name", ""),
            "contact_name": facility.get("contact_name", "there"),
            "city": facility.get("city", "your area"),
            **self.company_info,
            **(custom_fields or {})
        }
        
        # Render email
        subject = email_template["subject"].format(**merge_fields)
        body = email_template["body"].format(**merge_fields)
        
        # Send via GHL
        if self.ghl_api_key:
            send_result = self._send_via_ghl(
                to_email=facility["contact_email"],
                subject=subject,
                body=body
            )
        else:
            send_result = {"success": False, "error": "GHL not configured", "would_send": True}
        
        # Log outreach
        if self.db_connected:
            self.supabase.table("facility_outreach").insert({
                "facility_id": facility_id,
                "outreach_type": "email",
                "contact_name": facility.get("contact_name"),
                "outcome": "sent" if send_result.get("success") else "failed",
                "notes": f"Template: {template}",
                "next_followup": (datetime.now() + timedelta(days=3)).isoformat()
            }).execute()
        
        print(f"[OUTREACH] Email to {facility['name']}: {send_result.get('success', False)}")
        
        return send_result
    
    def _send_via_ghl(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> Dict[str, Any]:
        """Send email via GHL API."""
        try:
            # Convert plain text to HTML
            html_body = body.replace("\n", "<br>").replace("**", "<strong>").replace("**", "</strong>")
            
            response = requests.post(
                f"{GHL_API_BASE}/emails",
                headers=self._ghl_headers(),
                json={
                    "locationId": self.ghl_location_id,
                    "to": to_email,
                    "subject": subject,
                    "htmlBody": html_body
                }
            )
            
            if response.status_code in [200, 201]:
                return {"success": True, "message_id": response.json().get("id")}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @self_annealing
    def run_outreach_campaign(
        self,
        city: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Run outreach campaign to prospect facilities.
        
        Args:
            city: Target city (optional)
            limit: Max facilities to contact
        
        Returns:
            Campaign results
        """
        if not self.db_connected:
            return {"success": False, "error": "Database not connected"}
        
        # Get prospect facilities
        query = self.supabase.table("alf_facilities").select("id, name, contact_email")
        query = query.eq("relationship_status", "prospect")
        
        if city:
            query = query.eq("city", city)
        
        query = query.limit(limit)
        result = query.execute()
        
        facilities = result.data or []
        
        results = {
            "total": len(facilities),
            "sent": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        for facility in facilities:
            if not facility.get("contact_email"):
                results["skipped"] += 1
                continue
            
            send_result = self.send_outreach_email(
                facility_id=facility["id"],
                template="initial_intro"
            )
            
            if send_result.get("success"):
                results["sent"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "facility": facility["name"],
                "result": send_result.get("success", False)
            })
        
        print(f"[OUTREACH] Campaign complete: {results['sent']} sent, {results['failed']} failed")
        
        return results
    
    def update_facility_status(
        self,
        facility_id: str,
        new_status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update facility relationship status.
        
        Args:
            facility_id: Facility ID
            new_status: New status (prospect, contacted, partner, contracted)
            notes: Optional notes
        
        Returns:
            Update result
        """
        if not self.db_connected:
            return {"success": False, "error": "Database not connected"}
        
        update_data = {
            "relationship_status": new_status,
            "updated_at": datetime.now().isoformat()
        }
        
        if new_status == "contracted":
            update_data["contract_signed"] = True
            update_data["contract_date"] = datetime.now().date().isoformat()
        
        result = self.supabase.table("alf_facilities").update(update_data).eq("id", facility_id).execute()
        
        # Log the status change
        self.supabase.table("facility_outreach").insert({
            "facility_id": facility_id,
            "outreach_type": "status_change",
            "outcome": new_status,
            "notes": notes
        }).execute()
        
        return {"success": True, "new_status": new_status}
    
    def get_followup_needed(self) -> List[Dict]:
        """Get facilities needing follow-up."""
        if not self.db_connected:
            return []
        
        today = datetime.now().date().isoformat()
        
        result = self.supabase.table("facility_outreach").select(
            "*, alf_facilities(name, contact_name, contact_email)"
        ).lte("next_followup", today).execute()
        
        return result.data or []
    
    def get_pipeline_summary(self) -> Dict[str, int]:
        """Get facility pipeline summary."""
        if not self.db_connected:
            return {}
        
        result = self.supabase.table("alf_facilities").select("relationship_status").execute()
        
        summary = {
            "prospect": 0,
            "contacted": 0,
            "partner": 0,
            "contracted": 0
        }
        
        for facility in result.data or []:
            status = facility.get("relationship_status", "prospect")
            if status in summary:
                summary[status] += 1
        
        return summary


if __name__ == "__main__":
    print("[OUTREACH] Facility Outreach - Partner Recruitment")
    print("=" * 55)
    
    # Check configuration
    ghl_key = os.getenv("GHL_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    
    print()
    print("Configuration Status:")
    print(f"  GHL: {'✅' if ghl_key else '⚠️ Not set'}")
    print(f"  Supabase: {'✅' if supabase_url else '⚠️ Not set'}")
    
    print()
    print("[OUTREACH] Available templates:")
    for name in OUTREACH_TEMPLATES.keys():
        print(f"  - {name}")
    
    # Initialize
    outreach = FacilityOutreach()
    
    if outreach.db_connected:
        summary = outreach.get_pipeline_summary()
        print()
        print("Partner Pipeline:")
        for status, count in summary.items():
            print(f"  {status}: {count}")
