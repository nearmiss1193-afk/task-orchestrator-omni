"""
UPDATE VAPI WEBHOOK
===================
Updates the Vapi assistant with the new permanent webhook URL.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_PRIVATE_KEY")
NEW_WEBHOOK_URL = "https://nearmiss1193-afk--vapi-live.modal.run"

def get_assistants():
    """List all Vapi assistants."""
    response = requests.get(
        "https://api.vapi.ai/assistant",
        headers={"Authorization": f"Bearer {VAPI_API_KEY}"}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get assistants: {response.text}")
        return []

def update_assistant_webhook(assistant_id, webhook_url):
    """Update an assistant's server URL."""
    response = requests.patch(
        f"https://api.vapi.ai/assistant/{assistant_id}",
        headers={
            "Authorization": f"Bearer {VAPI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "serverUrl": webhook_url
        }
    )
    
    if response.status_code == 200:
        print(f"✅ Updated assistant {assistant_id} with webhook: {webhook_url}")
        return True
    else:
        print(f"❌ Failed to update: {response.text}")
        return False

def main():
    print("🔧 Updating Vapi Assistants with New Webhook URL")
    print("=" * 50)
    print(f"New URL: {NEW_WEBHOOK_URL}")
    print("")
    
    if not VAPI_API_KEY:
        print("❌ VAPI_PRIVATE_KEY not found in .env")
        return
    
    assistants = get_assistants()
    
    if not assistants:
        print("No assistants found or API error.")
        return
    
    print(f"Found {len(assistants)} assistant(s):")
    
    for assistant in assistants:
        name = assistant.get('name', 'Unnamed')
        aid = assistant.get('id')
        current_url = assistant.get('serverUrl', 'Not set')
        
        print(f"\n📞 {name} (ID: {aid})")
        print(f"   Current: {current_url}")
        
        # Update the webhook
        update_assistant_webhook(aid, NEW_WEBHOOK_URL)
    
    print("\n✅ Vapi webhook update complete!")

if __name__ == "__main__":
    main()
