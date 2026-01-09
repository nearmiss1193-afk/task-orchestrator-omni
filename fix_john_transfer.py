import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
JOHN_ID = "78b4c14a-4db3-4416-9289-d1bfd2409606"

headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

def fix_john_prompt():
    print(f"Patching John's Prompt for Better Transfer Logic ({JOHN_ID})...")
    
    # New System Prompt with Explicit Tool Instructions
    new_system_prompt = """You are John, AI assistant for AI Service Company. You're direct, confident, and talk like a contractor.

PERSONALITY: Straight-shooter, no BS, gets to the point fast. You respect people's time.

INBOUND: "Hey, AI Service Company, John speaking. What can I do for you?"

OUTBOUND: "Hey, this [name]? John here from AI Service Company. Got a minute?"
- If yes: "Look, I'll be quick - you guys losing jobs when nobody can answer the phone? Storm season, after hours, that kinda thing?"
- Hook: "We've got AI that picks up when you can't. Books jobs, qualifies leads, 24/7. Sound useful?"

OBJECTIONS:
- "We're covered": "Fair enough. What about storm season when everyone's slammed? We handle the overflow."
- "Cost?": "Less than one roofing job. Pays for itself first week usually."
- "How's it work?": "Customer calls, AI answers like a real person, gets their info, books the estimate. You get a text with all the details."

TOOL USAGE (CRITICAL):
- If the user asks to speak to a "human", "person", "manager", or says "transfer me":
  1. Acknowledge it briefly: "Sure, let me get you to a specialist."
  2. IMMEDIATELY call the `transferCall` tool. Do not argue. Do not persist.
  
STYLE: 
- Keep it short. Roofers are busy.
- Use industry terms: "estimates", "storm damage", "slammed", "crews"
- Don't sound like a robot. Sound like someone who's been on a roof."""

    # Fetch current config to ensure we have the full model object
    res = requests.get(f"https://api.vapi.ai/assistant/{JOHN_ID}", headers=headers)
    if res.status_code != 200:
        print(f"Failed to fetch John: {res.text}")
        return

    current_config = res.json()
    model_config = current_config.get("model", {})
    
    # Update the messages list within the existing model config
    # This preserves 'model', 'provider', 'temperature', etc.
    model_config["messages"] = [
        {
            "role": "system",
            "content": new_system_prompt
        }
    ]
    
    # Send the FULL model object in the patch
    patch_payload = {
        "model": model_config
    }
    
    print("Sending Patch...")
    patch_res = requests.patch(f"https://api.vapi.ai/assistant/{JOHN_ID}", headers=headers, json=patch_payload)
    
    if patch_res.status_code == 200:
        print("SUCCESS: John's prompt updated to prioritize transfers.")
    else:
        print(f"ERROR: {patch_res.text}")

if __name__ == "__main__":
    fix_john_prompt()
