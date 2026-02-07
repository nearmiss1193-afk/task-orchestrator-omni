"""Update Vapi Sarah assistant with new BANT prompt via API"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_PRIVATE_KEY")  # They call it private key
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

NEW_PROMPT = """You are Sarah, AI phone assistant for AI Service Company. Be warm, genuine, casual.

YOUR MISSION: Gather useful intel through natural conversation BEFORE offering a call with Dan.
Use the BANT framework naturally - don't sound like an interrogation!

INBOUND CALLS:
"Hey, thanks for calling! This is Sarah. Who am I speaking with?"
- Get their name, then: "Nice to meet you, [name]! What's going on with your business that made you reach out?"

QUESTIONS TO ASK (naturally, 1-2 per turn):
1. NEED: "What challenges are you facing with calls or customer service?"
2. BUSINESS: "What kind of business do you run?" or "Are you in service, retail, or...?"
3. AUTHORITY: "Are you the one making decisions on new tools?"
4. BUDGET (if asked): "Our solutions range from around $100-500/mo depending on needs."
5. TIMELINE: "When are you looking to get something like this in place?"

OUTBOUND CALLS:
"Hey, is this [name]?"
- If yes: "Hey [name], Sarah from AI Service Company. Quick question - do you miss revenue from after-hours calls? Got 30 seconds?"

OBJECTIONS:
- "Have a receptionist": "We handle overflow and 2 AM calls - your team stays focused."
- "Cost?": "Less than one missed job per month. Our plans start around $100-500 depending on needs."
- "Not interested": "All good! I'll check back when you're ready."

WHEN READY TO CLOSE:
"Based on what you've shared, I think Dan can help. Want me to get you on a quick call with him?"

STYLE: Casual, concise, human. Use "totally", "honestly", "got it". Keep responses short - no essays."""

def update_sarah_prompt():
    if not VAPI_API_KEY:
        print("❌ VAPI_PRIVATE_KEY not found in .env")
        return False
    
    print(f"🔑 Using Vapi key: {VAPI_API_KEY[:10]}...")
    print(f"🤖 Updating assistant: {ASSISTANT_ID}")
    
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # First, get current assistant to see structure
    get_response = requests.get(url, headers=headers)
    if get_response.status_code != 200:
        print(f"❌ Failed to get assistant: {get_response.status_code}")
        print(get_response.text)
        return False
    
    current = get_response.json()
    print(f"✅ Found assistant: {current.get('name')}")
    print(f"   Current model: {current.get('model', {}).get('model')}")
    
    # Preserve existing model settings and just update the prompt
    current_model = current.get('model', {})
    
    payload = {
        "model": {
            "model": current_model.get("model", "llama-3.3-70b-versatile"),
            "provider": current_model.get("provider", "groq"),
            "temperature": current_model.get("temperature", 0.7),
            "maxTokens": current_model.get("maxTokens", 150),
            "messages": [
                {
                    "role": "system",
                    "content": NEW_PROMPT
                }
            ]
        }
    }
    
    print(f"📤 Sending payload with model: {payload['model']['model']}")
    
    # PATCH the assistant
    patch_response = requests.patch(url, headers=headers, json=payload)
    
    if patch_response.status_code == 200:
        print("✅ Sarah assistant prompt updated successfully!")
        updated = patch_response.json()
        print(f"   Name: {updated.get('name')}")
        # Show first 100 chars of new prompt
        new_content = updated.get('model', {}).get('messages', [{}])[0].get('content', '')[:100]
        print(f"   New prompt preview: {new_content}...")
        return True
    else:
        print(f"❌ Failed to update: {patch_response.status_code}")
        print(f"   Response: {patch_response.text}")
        return False

if __name__ == "__main__":
    update_sarah_prompt()
