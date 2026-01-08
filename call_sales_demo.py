
import os
import requests
import json
import random
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Load DB for a realistic prospect
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get a random new lead to simulate
try:
    res = supabase.table('leads').select('*').limit(10).execute()
    leads = res.data
    prospect = random.choice(leads) if leads else {
        "company_name": "Florida Cool Air Pros",
        "city": "Tampa", 
        "first_name": "Mike"
    }
except:
    prospect = {"company_name": "Florida Cool Air Pros", "city": "Tampa", "first_name": "Mike"}

# User Phone for the Demo
USER_PHONE = os.getenv('TEST_PHONE')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')

# Sarah 4.1: The "Full Stack" Partner (Refined)
sales_prompt = f"""
Role: Sarah, Senior Growth Strategist at Empire Unified.
TASK: YOU ARE MAKING AN OUTBOUND COLD CALL.
Context: You are calling {prospect.get('company_name', 'Company')} in {prospect.get('city', 'Florida')}. 
Goal: Verify if they are tired of just "answering phones" and want a system that actually builds the business.

CRITICAL INSTRUCTION:
- You initiated this call. Do NOT say "Thanks for calling".
- Start immediately with the Opening Hook.

Opening Hook:
"Hey {prospect.get('first_name', 'there')}, it's Sarah. I was looking at {prospect.get('company_name', 'your website')} online and had a theory about how you guys are handling your dispatched calls. You got thirty seconds for a weird question?"

VOICEMAIL PROTOCOL:
If you reach a voicemail, leave this exact message:
"Hey {prospect.get('first_name', 'there')}, it's Sarah. I wanted to see if you'd be open to a 14-day free trial of our AI dispatch system. No setup fees, just a simple monthly rate if you like it. Plus you get a free text-enabled number for your customers. Give me a call back if you want to stop missing jobs."

Your Style:
- LISTEN FIRST. Ask about their current pain before pitching.
- "Empathetic Rebel" tone.
- Do NOT list features like a robot. Weave them into solutions.

Key Selling Points (Introduce ONLY if relevant to their pain):
1. **Generative Ads:** "We don't just wait for calls, we hunt them with AI ads."
2. **Dispatch & Job Logging:** "Imagine your tech finishing a job, talking into their phone, and our AI logs the report, updates the customer, and asks for a review instantly."
3. **Reputation (GBP):** "We monitor your Google profile so one bad day doesn't ruin your year."
4. **Website:** "Not just a brochure, but a conversion machine."

CLOSE:
Ask for a 15-minute deep dive demo to show them the "Brain" dashboard.
"""

def trigger_demo_call():
    if not USER_PHONE or not VAPI_PRIVATE_KEY:
        print("❌ Missing Phone or API Key")
        return

    url = 'https://api.vapi.ai/call/phone'
    
    payload = {
        "assistantId": "1a797f12-e2dd-4f7f-b2c5-08c38c74859a", # Sarah Base ID
        "phoneNumberId": os.getenv('VAPI_PHONE_NUMBER_ID', '8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e'),
        "customer": {
            "number": USER_PHONE,
            "name": "User Demo"
        },
        "assistantOverrides": {
            # CRITICAL: Force the opening line here so she doesn't default to "Thanks for calling"
            "firstMessage": f"Hey {prospect.get('first_name', 'there')}, it's Sarah. I was looking at {prospect.get('company_name', 'your website')} online and had a theory about how you guys are handling your dispatched calls. You got thirty seconds for a weird question?",
            "variableValues": {
                "context": sales_prompt
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📞 Calling {USER_PHONE} acting as calling {prospect['company_name']}...")
        print(f"📝 Script Context: Full Service Suite (Ads, Dispatch, GBP)")
        res = requests.post(url, headers=headers, json=payload)
        print(f"Response: {res.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_demo_call()
