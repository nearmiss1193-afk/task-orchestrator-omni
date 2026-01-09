# create_john_roofing.py - Create John, male AI agent for roofing A/B test
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")

url = "https://api.vapi.ai/assistant"
headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

# John's configuration - optimized for roofing industry
john_config = {
    "name": "John 1.0 - Roofing",
    
    # Male voice - ElevenLabs "Adam" (deep, confident)
    "voice": {
        "voiceId": "pNInz6obpgDQGcFmaJgB",  # Adam - male voice
        "provider": "11labs",
        "model": "eleven_flash_v2_5"  # Fast TTS
    },
    
    # Groq LLM for speed (same as optimized Sarah)
    "model": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "messages": [
            {
                "role": "system",
                "content": """You are John, AI assistant for AI Service Company. You're direct, confident, and talk like a contractor.

PERSONALITY: Straight-shooter, no BS, gets to the point fast. You respect people's time.

INBOUND: "Hey, AI Service Company, John speaking. What can I do for you?"

OUTBOUND: "Hey, this [name]? John here from AI Service Company. Got a minute?"
- If yes: "Look, I'll be quick - you guys losing jobs when nobody can answer the phone? Storm season, after hours, that kinda thing?"
- Hook: "We've got AI that picks up when you can't. Books jobs, qualifies leads, 24/7. Sound useful?"

OBJECTIONS:
- "We're covered": "Fair enough. What about storm season when everyone's slammed? We handle the overflow."
- "Cost?": "Less than one roofing job. Pays for itself first week usually."
- "How's it work?": "Customer calls, AI answers like a real person, gets their info, books the estimate. You get a text with all the details."

STYLE: 
- Keep it short. Roofers are busy.
- Use industry terms: "estimates", "storm damage", "slammed", "crews"
- Don't sound like a robot. Sound like someone who's been on a roof."""
            }
        ],
        "temperature": 0.7,
        "maxTokens": 150
    },
    
    # Deepgram for STT
    "transcriber": {
        "model": "nova-2",
        "language": "en",
        "provider": "deepgram"
    },
    
    "firstMessage": "Hey, AI Service Company, John speaking. What can I do for you?",
    "endCallMessage": "Alright, appreciate your time. Take care.",
    
    "recordingEnabled": True,
    "silenceTimeoutSeconds": 10,
    "serverUrl": "https://nearmiss1193-afk--vapi-live.modal.run",
    "maxDurationSeconds": 600,
    "backchannelingEnabled": True,
    
    "analysisPlan": {
        "summaryPrompt": "Summarize this roofing sales call. Include: customer name, business name, pain points (storm season, missed calls, overflow), objections, and outcome (demo booked, follow up, not interested).",
        "successEvaluationPrompt": "Rate John's call performance 1-10. Did he build rapport quickly, handle objections, and get a clear next step?",
        "successEvaluationRubric": "NumericScale"
    }
}

print("Creating John (Male AI Agent for Roofing)...")
print("  Voice: ElevenLabs Adam (male)")
print("  LLM: Groq Llama 3.3 70B")
print("  Style: Direct, contractor-like")

res = requests.post(url, headers=headers, json=john_config)

if res.status_code == 201:
    result = res.json()
    print(f"\n[SUCCESS] John created!")
    print(f"  Assistant ID: {result.get('id')}")
    print(f"  Name: {result.get('name')}")
    
    # Save config
    with open("john_config.json", "w") as f:
        json.dump(result, f, indent=2)
    print("  Saved to: john_config.json")
    
    # Save ID for campaign use
    with open("john_assistant_id.txt", "w") as f:
        f.write(result.get('id'))
    print(f"\n  JOHN_ASSISTANT_ID={result.get('id')}")
    print("\n  Add this to your .env and use for roofing campaigns!")
else:
    print(f"\n[ERROR] {res.status_code}")
    print(res.text)
