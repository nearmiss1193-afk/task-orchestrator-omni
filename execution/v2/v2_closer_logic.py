import os
import requests
from typing import Dict, Any
from .ghl_bridge import ghl

class SarahCloserBridge:
    """
    v2 CLOSER LOGIC
    The bridge between Vapi call outcomes and Stripe payments.
    """

    def __init__(self):
        self.stripe_secret = os.environ.get("STRIPE_SECRET_KEY")

    async def handle_call_outcome(self, vapi_report: Dict[str, Any]):
        """Triggered by Vapi Webhook at end of call."""
        
        # 1. Extract Data
        prospect_id = vapi_report.get("customer", {}).get("id")
        prospect_phone = vapi_report.get("customer", {}).get("number")
        prospect_name = vapi_report.get("customer", {}).get("name")
        outcome = vapi_report.get("analysis", {}).get("structuredData", {})
        
        selected_package = outcome.get("package", "silver").lower()
        interest_level = outcome.get("interest_level", "low")

        if interest_level == "high" or "deposit" in str(vapi_report.get("transcript")).lower():
            # 2. Generate Stripe Link
            amount = 19700 if selected_package == "silver" else 39700
            stripe_link = await self._create_stripe_link(amount, prospect_name, selected_package)
            
            # 3. Send SMS via GHL
            message = f"Hey {prospect_name}, here is your secure link to lock in the {selected_package.upper()} spot: {stripe_link} -Sarah"
            await ghl.send_sms(prospect_phone, message)
            
            # 4. Update CRM
            await ghl.add_tag(prospect_id, f"v2-deposit-sent-{selected_package}")
            await ghl.update_pipeline_stage(prospect_id, "closing_stage_id_here")
            
            print(f"[CLOSER] ✅ Deposit link sent to {prospect_name} for {selected_package}")

    async def _create_stripe_link(self, amount: int, name: str, package: str) -> str:
        """Mocked Stripe Link Generation (Final build will use stripe-python)."""
        # In production: stripe.PaymentLink.create(...)
        return f"https://buy.stripe.com/mock_{package}_{amount}"

# Global instance
closer = SarahCloserBridge()
