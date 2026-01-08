import modal
import os
import requests

app = modal.App("vapi-debugger")
VAULT = modal.Secret.from_name("agency-vault")

image = modal.Image.debian_slim().pip_install("requests")

@app.function(image=image, secrets=[VAULT])
def debug_vapi_resources():
    api_key = os.environ.get("VAPI_PRIVATE_KEY")
    if not api_key:
        print("❌ CRITICAL: VAPI_PRIVATE_KEY not found in 'agency-vault' secret.")
        return

    headers = {"Authorization": f"Bearer {api_key}"}
    
    print("\n--- 📞 VAPI RESOURCES CHECK ---")
    
    # 1. Get Assistants
    try:
        res = requests.get("https://api.vapi.ai/assistant", headers=headers)
        assistants = res.json()
        print(f"✅ Found {len(assistants)} Assistants:")
        sarah_id = None
        for a in assistants:
            name = a.get('name') or a.get('transcriber', {}).get('model', 'Unknown')
            print(f"   - {name} ({a.get('id')})")
            if 'sarah' in str(name).lower() or 'office' in str(name).lower():
                sarah_id = a.get('id')
    except Exception as e:
        print(f"❌ Failed to list assistants: {e}")
        sarah_id = None

    # 2. Get Phone Numbers
    phone_id = None
    phone_number_str = "13527585336" # Target business number
    try:
        res = requests.get("https://api.vapi.ai/phone-number", headers=headers)
        phones = res.json()
        print(f"✅ Found {len(phones)} Phone Numbers:")
        for p in phones:
            p_num = p.get('number', '')
            print(f"   - {p_num} ({p.get('id')})")
            if phone_number_str in p_num.replace("+","").replace("-",""):
                phone_id = p.get('id')
    except Exception as e:
        print(f"❌ Failed to list phone numbers: {e}")

    print("\n--- 🚀 TRIGGER INFO ---")
    if sarah_id and phone_id:
        print(f"READY TO CALL.")
        print(f"Assistant ID: {sarah_id}")
        print(f"Phone ID: {phone_id}")
        return {"sarah_id": sarah_id, "phone_id": phone_id}
    else:
        print("⚠️ Missing IDs for Sarah or Business Phone.")
        return None

@app.local_entrypoint()
def main():
    debug_vapi_resources.remote()
