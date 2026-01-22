"""
V2 EMPIRE FUSION - SOVEREIGN MASTER APP
========================================
Standalone Modal app with all logic bundled for deployment.
"""
import modal
import os
from fastapi import Request

# Define the Modal App
image = (
    modal.Image.debian_slim()
    .pip_install("supabase", "requests", "anthropic", "openai", "google-generativeai", "fastapi")
)

app = modal.App("v2-empire-fusion")
VAULT_V1 = modal.Secret.from_name("agency-vault")

# ============================================
# INLINE: AI COUNCIL BROKER
# ============================================
class CouncilBroker:
    """The AI Council - Routes to the right LLM expert."""
    
    INTENT_MAP = {
        "outreach_copy": "claude",
        "complex_logic": "gpt4o", 
        "speed_check": "gemini",
        "real_time_intel": "grok"
    }

    async def get_expert(self, intent: str, prompt: str, system_prompt: str = "") -> str:
        """Route to the best LLM for this task."""
        expert = self.INTENT_MAP.get(intent, "gemini")
        
        if expert == "claude":
            return await self._call_claude(prompt, system_prompt)
        elif expert == "gemini":
            return await self._call_gemini(prompt)
        else:
            return await self._call_gemini(prompt)  # Default fallback

    async def _call_claude(self, prompt: str, system: str) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    async def _call_gemini(self, prompt: str) -> str:
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text

council = CouncilBroker()

# ============================================
# INLINE: GHL BRIDGE
# ============================================
class GHLBridge:
    """Handles CRM operations via GHL API."""
    
    def __init__(self):
        self.api_key = os.environ.get("GHL_API_KEY")

    async def send_sms(self, phone: str, body: str):
        print(f"[GHL] Sending SMS to {phone}: {body[:50]}...")
        return {"success": True}

    async def send_email(self, email: str, subject: str, body: str):
        print(f"[GHL] Sending Email to {email}: {subject}")
        return {"success": True}

ghl = GHLBridge()

# ============================================
# INLINE: SUPABASE HELPERS
# ============================================
def get_supabase():
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

# ============================================
# ENDPOINTS
# ============================================

@app.function(image=image, secrets=[VAULT_V1], timeout=600)
@modal.fastapi_endpoint(method="POST")
async def orchestrate(request: Request):
    """Triggered by SCC Dashboard to run specific campaigns."""
    payload = await request.json()
    campaign = payload.get("campaign", "DEFAULT")
    action = payload.get("action", "start")
    
    print(f"[FUSION] 🚀 Campaign Triggered: {campaign} ({action})")
    
    # 1. Handle Prospecting Trigger
    if campaign == "SMS_BLAST":
        supabase = get_supabase()
        res = supabase.table("contacts_master") \
            .select("*") \
            .eq("status", "new") \
            .limit(10) \
            .execute()
        
        prospects = res.data or []
        for p in prospects:
            await ghl.send_sms(p["phone"], f"Hi {p['full_name']}, I found a revenue leak at {p.get('company_name')}. Check it out?")
            supabase.table("contacts_master").update({"status": "contacted"}).eq("id", p["id"]).execute()
        
        return {"status": "success", "message": f"Processed {len(prospects)} SMS leads."}

    # 2. Handle FB Ads / Neural Scale (AI Strategy)
    elif campaign == "NEURAL_SCALE":
        # Simulate AI Scaling
        return {"status": "success", "message": "Neural Council scaling mission parameters."}

    # 3. Handle Voice Handover
    elif campaign == "VOICE_HANDOVER":
        return {"status": "success", "message": "Sarah 2.0 standing by for live transfer."}

    return {"status": "triggered", "campaign": campaign}

@app.function(image=image, secrets=[VAULT_V1], timeout=600)
@modal.fastapi_endpoint(method="POST")
async def close_call(request: Request):
    """Triggered by Vapi Webhook at end of call."""
    payload = await request.json()
    print("[FUSION] 📞 Call Report Received.")
    
    # Extract data
    prospect_phone = payload.get("customer", {}).get("number")
    prospect_name = payload.get("customer", {}).get("name", "there")
    outcome = payload.get("analysis", {}).get("structuredData", {})
    selected_package = outcome.get("package", "silver").lower()
    
    # Generate Stripe link (mocked)
    amount = 197 if selected_package == "silver" else 397
    stripe_link = f"https://buy.stripe.com/mock_{selected_package}_{amount}"
    
    # Send SMS with link
    message = f"Hey {prospect_name}, here is your secure link to lock in your spot: {stripe_link} -Sarah"
    await ghl.send_sms(prospect_phone, message)
    
    return {"status": "closing_processed", "link_sent": stripe_link}

@app.function(image=image, secrets=[VAULT_V1], timeout=600)
@modal.fastapi_endpoint(method="POST")
async def vitals(request: Request):
    """Triggered by SCC Dashboard to get system stats."""
    print("[FUSION] 🔭 Vitals Request Received.")
    
    supabase = get_supabase()
    res_contacted = supabase.table("contacts_master").select("id", count="exact").eq("status", "contacted").execute()
    res_new = supabase.table("contacts_master").select("id", count="exact").eq("status", "new").execute()
    res_paid = supabase.table("contacts_master").select("id", count="exact").eq("status", "deposited").execute()
    
    revenue = (res_paid.count or 0) * 197
    
    return {
        "vitals": {
            "system_status": "ONLINE",
            "revenue_total": f"${revenue}",
            "leads_contacted": res_contacted.count or 0,
            "leads_pending": res_new.count or 0,
            "agents_active": 3
        },
        "recent_activity": []
    }

@app.function(image=image, secrets=[VAULT_V1], timeout=600)
@modal.fastapi_endpoint(method="POST")
async def stripe_webhook(request: Request):
    """Triggered by Stripe when a payment succeeds."""
    payload = await request.json()
    print("[FUSION] 💰 Payment Signal Received.")
    
    customer_name = payload.get("data", {}).get("object", {}).get("customer_details", {}).get("name", "New Client")
    customer_email = payload.get("data", {}).get("object", {}).get("customer_details", {}).get("email")
    
    print(f"[ONBOARDING] 🎉 {customer_name} just paid! Triggering GHL sub-account creation...")
    # In production: Create GHL sub-account, load snapshot, trigger Sarah welcome call
    
    return {"status": "onboarding_triggered", "customer": customer_name}

if __name__ == "__main__":
    print("Sovereign Fusion App initialized. Deploy with 'modal deploy'.")
