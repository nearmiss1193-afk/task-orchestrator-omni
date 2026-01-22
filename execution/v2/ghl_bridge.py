import os
import requests
from typing import Optional, Dict, Any, List

class GHLBridge:
    """
    v2 GHL BRIDGE
    Handles CRM operations, SMS, and Email via the LeadConnector (GHL) API.
    """

    def __init__(self, api_key: Optional[str] = None, location_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("GHL_API_KEY")
        self.location_id = location_id or os.getenv("GHL_LOCATION_ID")
        self.base_url = "https://services.leadconnectorhq.com"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }

    async def send_sms(self, phone: str, body: str) -> Dict[str, Any]:
        """Send an SMS to a lead."""
        url = f"{self.base_url}/messages/send"
        payload = {
            "type": "SMS",
            "contactId": await self.get_or_create_contact(phone=phone),
            "message": body
        }
        # In a real GHL flow, we'd need to handle contactId correctly
        print(f"[GHL] Sending SMS to {phone}: {body[:50]}...")
        return {"success": True, "message_id": "mock_msg_123"}

    async def send_email(self, email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send an Email to a lead."""
        print(f"[GHL] Sending Email to {email}: {subject}")
        return {"success": True, "message_id": "mock_email_123"}

    async def get_or_create_contact(self, phone: str = None, email: str = None, name: str = None) -> str:
        """Find or create a contact in GHL and return the contactId."""
        # Simplified for v2 shadow dev
        return "mock_contact_id_456"

    async def add_tag(self, contact_id: str, tag: str):
        """Add a tag to a GHL contact."""
        print(f"[GHL] Adding tag '{tag}' to contact {contact_id}")

    async def update_pipeline_stage(self, contact_id: str, stage_id: str):
        """Move contact to a different pipeline stage."""
        print(f"[GHL] Updating pipeline stage for {contact_id} to {stage_id}")

# Global instance
ghl = GHLBridge()
