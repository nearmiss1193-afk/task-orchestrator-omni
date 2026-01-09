# optimize_sarah_latency.py
# Upgrade Sarah to use Groq LLM + ElevenLabs Flash for <500ms latency
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

# Optimized configuration for <500ms latency
# Research source: Vapi latency docs, AssemblyAI recommendations
optimizations = {
    # Switch to Groq LLM - much faster than GPT-4
    "model": {
        "model": "llama-3.3-70b-versatile",  # Production-ready Groq Llama
        "provider": "groq",
        "messages": [
            {
                "role": "system",
                "content": """You are Sarah, AI phone assistant for AI Service Company. Be warm, genuine, casual.

INBOUND: "Hey, thanks for calling! This is Sarah. Who am I speaking with?"
- Get their name, then: "Nice to meet you, [name]! How can I help?"
- For demos: "Awesome! What's your best email for a calendar invite?"

OUTBOUND: "Hey, is this [name]?" 
- If yes: "Hey [name], Sarah from AI Service Company. Quick question - do you miss revenue from after-hours calls? Got 30 seconds?"

OBJECTIONS:
- "Have a receptionist": "We handle overflow and 2 AM calls - your team stays focused."
- "Cost?": "Less than one missed job per month. Want me to run numbers?"
- "Not interested": "All good! I'll check back when you're ready."

STYLE: Casual, concise, human. Use "totally", "honestly". No essays."""
            }
        ],
        "temperature": 0.7,
        "maxTokens": 150  # Keep responses short for speed
    },
    # ElevenLabs Flash v2.5 for fastest TTS
    "voice": {
        "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
        "provider": "11labs",
        "model": "eleven_flash_v2_5"  # Flash model for speed
    }
}

print("Upgrading Sarah for <500ms latency...")
print("  - LLM: GPT-4 -> Groq Llama 3.1 70B")
print("  - TTS: ElevenLabs -> ElevenLabs Flash v2.5")
print("  - Prompt: Shortened for faster processing")

res = requests.patch(url, headers=headers, json=optimizations)

if res.status_code == 200:
    print("\n[SUCCESS] Sarah optimized for low latency!")
    result = res.json()
    print(f"  Model: {result.get('model', {}).get('provider')} / {result.get('model', {}).get('model')}")
    print(f"  Voice: {result.get('voice', {}).get('provider')} / {result.get('voice', {}).get('model', 'default')}")
    
    # Save updated config
    with open("sarah_config_optimized.json", "w") as f:
        json.dump(result, f, indent=2)
    print("  Saved to: sarah_config_optimized.json")
else:
    print(f"\n[ERROR] {res.status_code}: {res.text}")
