
import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"

def extract_json(text):
    # Search for JSON block
    match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return None

def apply_optimization():
    if not VAPI_KEY:
        print("❌ VAPI_PRIVATE_KEY missing.")
        return

    try:
        with open('voice_optimization_advice.md', 'rb') as f:
            advice_text = f.read().decode('latin-1')
        
        print(f"Advice Length: {len(advice_text)}")
        
        patch_data = extract_json(advice_text)
        if not patch_data:
            print("❌ No JSON optimization block found in advice.")
            return

        print("🚀 Applying Optimized Vapi Config...")
        # Clean up patch_data (Vapi is picky, remove ID/orgId if Grok included them)
        keys_to_remove = ["id", "orgId", "createdAt", "updatedAt"]
        for key in keys_to_remove:
            if key in patch_data: del patch_data[key]
        
        url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
        headers = {
            "Authorization": f"Bearer {VAPI_KEY}",
            "Content-Type": "application/json"
        }
        
        res = requests.patch(url, headers=headers, json=patch_data)
        if res.status_code == 200:
            print("✅ SUCCESS: Sarah's voice is now optimized!")
            print(json.dumps(res.json(), indent=2)[:500] + "...")
        else:
            print(f"❌ FAILED: {res.status_code} - {res.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    apply_optimization()
