
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")
GROK_KEY = os.environ.get("GROK_API_KEY")
ASSISTANT_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"

def get_assistant_config():
    if not VAPI_KEY: return None
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    headers = {"Authorization": f"Bearer {VAPI_KEY}"}
    res = requests.get(url, headers=headers)
    return res.json()

def ask_grok_about_voice(config):
    if not GROK_KEY: return "Grok Key Missing"
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROK_KEY}", "Content-Type": "application/json"}
    prompt = f"""
    You are an expert in Vapi.ai and AI voice optimization.
    The user wants to make "Sarah's Voice" the best possible, comparable to Grok AI's voice quality.
    
    Current Vapi Assistant Config:
    {json.dumps(config, indent=2)}
    
    TASK:
    1. Analyze the current voice, model, and transcription settings.
    2. Suggest the absolute BEST settings for:
       - Voice Provider (ElevenLabs, Play.ht, Rime, etc.) and specific Voice ID.
       - Model (GPT-4o, Grok, etc.) and temperature.
       - Background sound/latency settings.
       - Transcription provider.
       - Filler words or "human-like" markers.
    3. Provide a JSON object for the Vapi PATCH request to optimize the voice.
    4. Explain WHY these changes make it "the best".
    """
    
    data = {
        "model": "grok-3",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    res = requests.post(url, headers=headers, json=data)
    try:
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {e} - Response: {res.text}"

def update_assistant_config(patch_data):
    if not VAPI_KEY: return
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    headers = {"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"}
    res = requests.patch(url, headers=headers, json=patch_data)
    print(f"Update Status: {res.status_code}")
    print(res.text)

if __name__ == "__main__":
    print("Fetching Sarah's config...")
    config = get_assistant_config()
    if config:
        print("Asking Grok-3 for optimizations...")
        advice = ask_grok_about_voice(config)
        print("\n--- GROK ADVICE ---")
        print(advice)
        
        # Save advice to a file
        with open("voice_optimization_advice.md", "w") as f:
            f.write(advice)
        
        # NOTE: I will manually parse and apply the JSON from the 'advice' 
        # once I see it, or the user can review.
    else:
        print("Failed to fetch assistant config.")
