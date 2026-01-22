import os
import requests
from typing import Dict, Any
from .ghl_bridge import ghl

class OnboardingEngine:
    """
    v2 ONBOARDING ENGINE
    Handles the Stripe -> GHL automation flow.
    """

    def __init__(self):
        self.ghl_api_key = os.environ.get("GHL_API_KEY")

    async def handle_payment_success(self, stripe_payload: Dict[str, Any]):
        """Triggered by Stripe Webhook when a deposit is paid."""
        
        # 1. Extract Customer Data
        customer_email = stripe_payload.get("data", {}).get("object", {}).get("customer_details", {}).get("email")
        customer_name = stripe_payload.get("data", {}).get("object", {}).get("customer_details", {}).get("name")
        package = stripe_payload.get("data", {}).get("object", {}).get("metadata", {}).get("package", "silver")
        
        print(f"[ONBOARDING] 💰 Payment Received from {customer_name} for {package}!")

        # 2. Create GHL Sub-Account (Simplified API call)
        sub_account_id = await self._create_ghl_sub_account(customer_name, customer_email)
        
        # 3. Load Snapshot (The "Brain" of the business)
        await self._load_ghl_snapshot(sub_account_id)
        
        # 4. Notify Dan & Sarah Onboarding Call
        await self._notify_and_celebrate(customer_name, customer_email, package)

    async def _create_ghl_sub_account(self, name: str, email: str) -> str:
        """Create a new GHL sub-account via API."""
        print(f"[GHL] Creating sub-account for {name}...")
        # In production: POST https://services.leadconnectorhq.com/locations
        return "new_sub_account_id_789"

    async def _load_ghl_snapshot(self, sub_account_id: str):
        """Push the 'Master Agency Snapshot' to the new account."""
        print(f"[GHL] Loading Master Snapshot to {sub_account_id}...")
        # In production: POST https://services.leadconnectorhq.com/locations/{id}/snapshots

    async def _notify_and_celebrate(self, name: str, email: str, package: str):
        """Send notification and trigger Sarah's welcome call."""
        print(f"[NOTIFY] SMS to Dan: 🎉 {name} just joined on the {package} package!")
        # Trigger Vapi Welcome Call
        print(f"[VAPI] Triggering Welcome Call to {name}...")

# Global instance
onboarding = OnboardingEngine()
