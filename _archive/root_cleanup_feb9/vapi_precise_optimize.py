
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")
GROK_KEY = os.environ.get("GROK_API_KEY")
ASSISTANT_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"

def get_optimized_json():
    if not GROK_KEY: return None
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROK_KEY}", "Content-Type": "application/json"}
    prompt = """
    GIVE ME ONLY A JSON OBJECT for a Vapi.ai assistant PATCH request.
    Objective: Make Sarah's voice "the best" (natural, empathetic, low latency, Grok-level quality).
    
    REQUIRED KEYS in JSON:
    - name: "Sarah (Hardened)"
    - voice: { provider: "elevenlabs", voiceId: "sarah", stability: 0.5, similarityBoost: 0.75, style: 0, useSpeakerBoost: true }
    - model: { provider: "openai", model: "gpt-4o", temperature: 0.7 }
    - transcription: { provider: "deepgram", language: "en-US", model: "nova-2" }
    - fillerWordsEnabled: true
    - endOfCallReportEnabled: true
    
    OUTPUT ONLY THE RAW JSON. NO MARKDOWN. NO CODE BLOCKS.
    """
    
    data = {
        "model": "grok-3",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    res = requests.post(url, headers=headers, json=data)
    try:
        return res.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

def apply_update(json_str):
    if not VAPI_KEY or not json_str: return
    
    # Try to clean if Grok added backticks
    clean_json = json_str.replace("```json", "").replace("```", "").strip()
    
    try:
        patch_data = json.loads(clean_json)
        url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
        headers = {
            "Authorization": f"Bearer {VAPI_KEY}",
            "Content-Type": "application/json"
        }
        res = requests.patch(url, headers=headers, json=patch_data)
        if res.status_code == 200:
            print("✅ Sarah's voice optimized successfully!")
        else:
            print(f"❌ Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ JSON Parse Error: {e}")

if __name__ == "__main__":
    print("Requesting optimized JSON from Grok-3...")
    json_data = get_optimized_json()
    if json_data:
        print("Applying update to Vapi...")
        apply_update(json_data)
    else:
        print("Failed to get JSON from Grok.")
