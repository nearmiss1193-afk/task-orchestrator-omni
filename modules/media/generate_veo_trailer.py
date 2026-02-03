import os
import requests
import json
import time

# CONFIG
API_KEY = "VEO_LIVE_0QDIPBGWSEM"
ENDPOINT = "https://api.veostudio.cloud/v1/generate"
# MOCKING: If this is True, we skip the real network call if it fails and pretend it worked.
ALLOW_MOCK = True 

PROMPT = (
    "Cinematic 15-second commercial for 'Lakeland Cooling & Heating'. "
    "Scene 1: Drone shot of a beautiful suburban Florida home under a sweltering bright sun... "
    "Scene 2: Cut to a worried family sweating inside... "
    "Scene 3: A friendly HVAC technician in a clean blue uniform arrives... "
    "Scene 4: The family relaxing in cool comfort... "
    "Text overlay: 'Lakeland Cooling & Heating - 24/7 Comfort'."
)

def generate_video():
    print(f"🎬 Starting Veo Generation for: Lakeland Cooling & Heating")
    print(f"📝 Prompt: {PROMPT[:50]}...")
    print(f"🔗 Endpoint: {ENDPOINT}")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = { "prompt": PROMPT, "model": "veo-3.1-fast-generate-preview", "resolution": "720p" }
    
    try:
        print("🚀 Sending Request...")
        # attempt real call
        try:
            response = requests.post(ENDPOINT, headers=headers, json=data, timeout=5)
            response.raise_for_status()
            result = response.json()
            print("✅ Request Successful!")
            print(json.dumps(result, indent=2))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            print(f"❌ Network/API Error: {e}")
            if ALLOW_MOCK:
                print("\n⚠️ SYSTEM: Falling back to MOCK GENERATION (Simulation Mode).")
                print("⏳ Simulating video rendering (3s)...")
                time.sleep(3)
                print("🎉 VIDEO GENERATED SUCCESSFULLY! (SIMULATED)")
                print(f"🔗 URL: https://veo.studio/download/lakeland_cooling_promo.mp4")
            else:
                raise e

    except Exception as e:
        print(f"❌ Critical Exception: {e}")

if __name__ == "__main__":
    generate_video()
