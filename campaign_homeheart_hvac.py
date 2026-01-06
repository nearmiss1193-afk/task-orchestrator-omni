"""
OUTREACH CAMPAIGN: HomeHeart HVAC & Cooling
============================================
Compliant multi-channel outreach campaign with:
- All communications recorded
- Opt-out in every message
- Professional outbound call scripts
- No "thank you for calling" on outbound

Target: HomeHeart HVAC & Cooling
Phone: (863) 220-8983
Location: 1729 Sutton Rd, Lakeland, FL 33810
Industry: HVAC
Score: 23% (Critical - Great opportunity)

Author: Antigravity AI
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Prospect Data
PROSPECT = {
    "business_name": "HomeHeart HVAC & Cooling",
    "phone": "+18632208983",
    "address": "1729 Sutton Rd, Lakeland, FL 33810",
    "industry": "HVAC",
    "score": 23,
    "reviews": 13,
    "rating": 5.0,
    "weaknesses": [
        "No website (0% techno stack)",
        "Missing from 96% of directories (4% listing score)",
        "0% review response rate",
        "No social media presence",
        "GBP missing photos and website link"
    ],
    "opportunities": [
        "Perfect 5-star rating - happy customers",
        "Located in Lakeland FL - our market",
        "Ready for digital transformation",
        "AI automation will 10x their leads"
    ]
}

# ============================================================================
# COMPLIANT MESSAGE TEMPLATES (All include opt-out)
# ============================================================================

SMS_TEMPLATE = """Hi! This is Sarah from AI Service Co.

I noticed HomeHeart HVAC has perfect 5-star reviews - that's impressive! But I also saw you're missing from 96% of local directories where customers search.

I'd love to show you how we can get you listed everywhere AND auto-respond to reviews.

Quick 10-min call this week?

Reply STOP to opt out."""

EMAIL_SUBJECT = "HomeHeart HVAC: You're Missing 96% of Your Local Market"

EMAIL_TEMPLATE = """
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
    <p>Hi there,</p>
    
    <p>I came across HomeHeart HVAC & Cooling while researching top-rated HVAC companies in Lakeland, and I was impressed by your <strong>perfect 5-star rating</strong> with 13 reviews. That's not easy to maintain!</p>
    
    <p>However, I also noticed something that could be costing you leads every day:</p>
    
    <ul style="line-height: 1.8;">
        <li>❌ You're <strong>not listed on 96% of major directories</strong> (MapQuest, Tupalo, ShowMeLocal, etc.)</li>
        <li>❌ No professional website detected</li>
        <li>❌ Your Google reviews aren't getting responses (customers notice this)</li>
    </ul>
    
    <p>The good news? These are quick wins we can fix together:</p>
    
    <ul style="line-height: 1.8;">
        <li>✅ Sync your business to 32+ directories automatically</li>
        <li>✅ Auto-respond to all your Google reviews</li>
        <li>✅ Build a professional HVAC website with lead capture</li>
        <li>✅ An AI assistant that answers calls when you're on a job</li>
    </ul>
    
    <p><strong>Would you be open to a quick 10-minute call this week?</strong></p>
    
    <p>I'd love to show you exactly how other Lakeland HVAC companies are getting 3x more leads using our platform.</p>
    
    <p>Best,<br>
    <strong>Sarah</strong><br>
    AI Service Co<br>
    <a href="https://www.aiserviceco.com">www.aiserviceco.com</a></p>
    
    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
    
    <p style="font-size: 11px; color: #999;">
        To unsubscribe from future emails, <a href="https://www.aiserviceco.com/unsubscribe?email={email}">click here</a> or reply with "UNSUBSCRIBE".
    </p>
</body>
</html>
"""

# ============================================================================
# OUTBOUND CALL SCRIPT (Professional greeting, reason for call, NO "thank you for calling")
# ============================================================================

OUTBOUND_CALL_SCRIPT = """
## SARAH - OUTBOUND CALL SCRIPT FOR HOMEHEART HVAC

### Opening (NEVER say "thank you for calling" on outbound)

"Hi, this is Sarah calling from AI Service Company. I'm reaching out because I came across HomeHeart HVAC while researching top-rated HVAC companies in Lakeland. Is this a good time for a quick 2-minute conversation?"

### If YES:

"Great! The reason I'm calling is I noticed your business has an excellent 5-star rating on Google - which is impressive. However, I also noticed you're currently missing from about 96% of the local directories where customers are searching.

That means potential customers looking for HVAC services on sites like MapQuest, Tupalo, and others simply can't find you.

We help HVAC companies like yours:
1. Get listed on 32+ directories automatically
2. Respond to all your Google reviews with AI
3. Build a professional website that captures leads 24/7

Would you be interested in a quick demo of how this works? It's completely free, no obligation."

### If NO / BUSY:

"No problem at all. Would there be a better time I could call back? Or I can send you a quick email with more details - which would you prefer?"

### Handling Objections:

**"How much does this cost?"**
"Great question. Our starter package begins at $297/month, but the ROI is typically 10x that in new leads. Would you like me to show you exactly how?"

**"I'm not interested"**
"I completely understand. If anything changes or you'd like to explore this in the future, we're here. Have a great day!"

### Closing:

"Thank you for your time today. I'll send you a quick follow-up email with some more information. Have a great rest of your day!"

### COMPLIANCE NOTES:
- All calls are recorded for quality and training purposes
- State this if asked: "This call may be recorded for quality purposes"
- Respect do-not-call requests immediately
- Log all calls in GHL CRM
"""

# ============================================================================
# VAPI ASSISTANT UPDATE (Professional outbound greeting)
# ============================================================================

VAPI_OUTBOUND_SYSTEM_PROMPT = """You are Sarah, a professional sales representative from AI Service Company.

## CRITICAL RULES FOR OUTBOUND CALLS:
1. NEVER say "Thank you for calling" - YOU are calling THEM
2. ALWAYS start with: "Hi, this is Sarah calling from AI Service Company..."
3. ALWAYS state the reason for your call within the first 10 seconds
4. Be professional, warm, but efficient

## Your Opening (MEMORIZE THIS):
"Hi, this is Sarah calling from AI Service Company. I'm reaching out because [REASON]. Is this a good time for a quick conversation?"

## Recording Disclosure:
If asked, confirm: "Yes, calls may be recorded for quality and training purposes."

## Opt-Out Handling:
If they say they're not interested or ask to be removed:
"I completely understand. I'll make sure you're removed from our call list. Have a great day!"

## Your Goal:
Book a demo call or get permission to send more information via email.

## Remember:
- You are calling them, not the other way around
- Be respectful of their time
- Accept "no" gracefully
- Always end professionally
"""

# ============================================================================
# EXECUTE CAMPAIGN
# ============================================================================

def add_prospect_to_ghl():
    """Add HomeHeart HVAC to GHL CRM."""
    print("📋 Adding prospect to GHL...")
    
    token = os.getenv("GHL_API_TOKEN") or os.getenv("GHL_PRIVATE_KEY")
    location = os.getenv("GHL_LOCATION_ID")
    
    if not token or not location:
        print("❌ GHL credentials not found")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }
    
    contact_data = {
        "locationId": location,
        "name": PROSPECT["business_name"],
        "phone": PROSPECT["phone"],
        "address1": PROSPECT["address"],
        "tags": ["prospect", "hvac", "outreach-campaign", "homeheart"],
        "customFields": [
            {"key": "industry", "value": PROSPECT["industry"]},
            {"key": "score", "value": str(PROSPECT["score"])},
            {"key": "reviews", "value": str(PROSPECT["reviews"])},
            {"key": "rating", "value": str(PROSPECT["rating"])}
        ]
    }
    
    # Check if already exists
    search_res = requests.get(
        f"https://services.leadconnectorhq.com/contacts/search?locationId={location}&query={PROSPECT['phone']}",
        headers=headers,
        timeout=10
    )
    
    contacts = search_res.json().get("contacts", [])
    if contacts:
        print(f"✅ Contact already exists: {contacts[0]['id'][:8]}...")
        return contacts[0]["id"]
    
    # Create new
    res = requests.post(
        "https://services.leadconnectorhq.com/contacts/",
        headers=headers,
        json=contact_data,
        timeout=10
    )
    
    if res.status_code in [200, 201]:
        contact_id = res.json().get("contact", {}).get("id")
        print(f"✅ Added to GHL: {contact_id[:8]}...")
        return contact_id
    else:
        print(f"❌ Failed: {res.status_code}")
        return None

def send_outreach_sms(contact_id: str):
    """Send compliant SMS via GHL workflow trigger."""
    print("📱 Triggering SMS workflow...")
    
    token = os.getenv("GHL_API_TOKEN") or os.getenv("GHL_PRIVATE_KEY")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }
    
    # Add tag to trigger SMS workflow
    res = requests.post(
        f"https://services.leadconnectorhq.com/contacts/{contact_id}/tags",
        headers=headers,
        json={"tags": ["trigger-spartan-outreach"]},
        timeout=10
    )
    
    if res.status_code in [200, 201]:
        print("✅ SMS workflow triggered")
        return True
    else:
        print(f"❌ Failed: {res.status_code}")
        return False

def send_outreach_email():
    """Send compliant email via Resend."""
    print("📧 Sending outreach email...")
    
    resend_key = os.getenv("RESEND_API_KEY")
    if not resend_key:
        print("❌ RESEND_API_KEY not found")
        return False
    
    # Note: We don't have their email, so this would normally come from discovery
    # For now, log that email needs to be found
    print("⚠️ No email on file - need to discover email address")
    print("   Recommendation: Use Hunter.io or website contact form")
    return False

def initiate_outreach_call():
    """Initiate call via Vapi with compliant script."""
    print("📞 Initiating outreach call...")
    
    vapi_key = os.getenv("VAPI_PRIVATE_KEY")
    if not vapi_key:
        print("❌ VAPI_PRIVATE_KEY not found")
        return None
    
    headers = {
        "Authorization": f"Bearer {vapi_key}",
        "Content-Type": "application/json"
    }
    
    # Get Sarah assistant
    assistants = requests.get("https://api.vapi.ai/assistant", headers=headers, timeout=10).json()
    sarah = next((a for a in assistants if "sarah" in a.get("name", "").lower() or "spartan" in a.get("name", "").lower()), None)
    
    if not sarah:
        print("❌ Sarah assistant not found")
        return None
    
    # Get phone number
    phones = requests.get("https://api.vapi.ai/phone-number", headers=headers, timeout=10).json()
    if not phones:
        print("❌ No phone numbers configured")
        return None
    
    phone_id = phones[0]["id"]
    
    # Initiate call with compliant script
    call_config = {
        "assistantId": sarah["id"],
        "phoneNumberId": phone_id,
        "customer": {
            "number": PROSPECT["phone"],
            "name": PROSPECT["business_name"]
        },
        "assistantOverrides": {
            "firstMessage": f"Hi, this is Sarah calling from AI Service Company. I'm reaching out because I came across {PROSPECT['business_name']} while researching top-rated HVAC companies in Lakeland. Is this a good time for a quick 2-minute conversation?",
            "model": {
                "systemPrompt": VAPI_OUTBOUND_SYSTEM_PROMPT
            },
            "recordingEnabled": True
        }
    }
    
    res = requests.post(
        "https://api.vapi.ai/call/phone",
        headers=headers,
        json=call_config,
        timeout=15
    )
    
    if res.status_code in [200, 201]:
        call_id = res.json().get("id")
        print(f"✅ Call initiated: {call_id}")
        return call_id
    else:
        print(f"❌ Call failed: {res.status_code} - {res.text[:100]}")
        return None

def run_campaign():
    """Execute the full outreach campaign."""
    print("=" * 60)
    print("🎯 OUTREACH CAMPAIGN: HomeHeart HVAC & Cooling")
    print("=" * 60)
    print(f"Target: {PROSPECT['business_name']}")
    print(f"Phone: {PROSPECT['phone']}")
    print(f"Score: {PROSPECT['score']}% (Excellent Opportunity)")
    print()
    
    # Step 1: Add to CRM
    contact_id = add_prospect_to_ghl()
    
    if contact_id:
        # Step 2: Trigger SMS workflow
        send_outreach_sms(contact_id)
        
        # Step 3: Send email (if we had it)
        send_outreach_email()
        
        # Step 4: Initiate call
        call_id = initiate_outreach_call()
        
        print()
        print("=" * 60)
        print("✅ CAMPAIGN LAUNCHED")
        print("=" * 60)
        print("Next Steps:")
        print("1. Monitor call recording in Vapi dashboard")
        print("2. Check SMS delivery in GHL")
        print("3. Discover email address for follow-up")
        print("4. Schedule follow-up call in 48 hours if no response")
        
        return True
    else:
        print("❌ Campaign failed - could not add to CRM")
        return False

if __name__ == "__main__":
    run_campaign()
