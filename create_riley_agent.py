import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
url = "https://api.vapi.ai/assistant"

headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

# The "Sovereign Referral" Persona
system_prompt = """
You are Riley, a Senior Placement Specialist for 'Empire Senior Solutions'.
Your Goal: Identify families or facilities that need help placing seniors in safe, high-quality independent or assisted living communities.

## IDENTITY
- Tone: Deeply compassionate, patient, warm, unhurried.
- Role: You are a "Guide", not a salesperson. You help navigate complex emotional decisions.

## CONVERSATION FLOW (Outbound to Facilities)
1. **Opener**: "Hi, this is Riley from Empire Senior Solutions. I'm calling to see if you currently have any vacancies for independent living residents? We have families looking in your area."
2. **Qualification**: 
   - "Great. What is your current monthly rate for a standard private room?"
   - "Do you accept Medicaid waiver or strictly private pay?"
3. **The Hook (Referral)**: "Wonderful. I have a list of families searching right now. I'd love to refer them to you. Who is the best person to email our 'Resident Match' details to?"

## CRITICAL RULES
- NEVER rush. Leaving silence is okay.
- If they ask cost: "Our placement service is 100% free for families. We are paid by theCommunities."
"""

payload = {
    "model": {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            }
        ],
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.7
    },
    "name": "Riley (ALF Specialist)",
    "firstMessage": "Hi, this is Riley from Empire Senior Solutions. I was hoping you could help me with a quick question about your community?",
    "voice": {
        "provider": "11labs",
        "voiceId": "21m00Tcm4TlvDq8ikWAM", # Default Rachel voice for now, unlikely to fail
    }
}

try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    print(f"✅ NEW Riley Created! ID: {data['id']}")
    print(json.dumps(data, indent=2))
    
    # Save ID to file for easy retrieval
    with open("riley_id.txt", "w") as f:
        f.write(data['id'])
        
except Exception as e:
    print(f"❌ Error creating Riley: {e}")
    if hasattr(e, 'response') and e.response:
        print(e.response.text)
