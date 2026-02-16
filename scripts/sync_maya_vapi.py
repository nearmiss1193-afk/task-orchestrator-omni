import modal
import os
import requests
import json

app = modal.App("vapi-sync")

# Use the image from deploy.py or as similar as possible
image = modal.Image.debian_slim().pip_install("requests")
VAULT = modal.Secret.from_name("sovereign-vault")

@app.function(image=image, secrets=[VAULT])
def update_vapi_assistant(assistant_id: str, server_url: str):
    vapi_key = os.environ.get("VAPI_API_KEY") or os.environ.get("VAPI_KEY")
    
    if not vapi_key:
        print("❌ VAPI_API_KEY not found in vault.")
        return {"error": "VAPI_API_KEY missing"}

    print(f"🔄 Updating Vapi Assistant: {assistant_id}")
    print(f"🌐 Setting Server URL: {server_url}")

    url = f"https://api.vapi.ai/assistant/{assistant_id}"
    headers = {
        "Authorization": f"Bearer {vapi_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "serverUrl": server_url
    }

    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ Successfully updated assistant configuration.")
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"❌ Failed to update assistant: {err}")
        if response.text:
            print(f"   Error details: {response.text}")
        return {"error": str(err), "details": response.text}
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return {"error": str(e)}

@app.local_entrypoint()
def main():
    ASSISTANT_ID = "5c8c6c65-8f2f-4715-b6e0-61954999c60b"
    SERVER_URL = "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"
    
    update_vapi_assistant.remote(ASSISTANT_ID, SERVER_URL)
