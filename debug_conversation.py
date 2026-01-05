
from modules.communication.sovereign_dispatch import dispatcher
import json
import requests # Added missing import

USER_PHONE = "+13529368152"

print(f"🔍 Inspecting Conversation for {USER_PHONE}...")

# 1. Resolve Contact ID
cid = dispatcher._get_or_create_contact(phone=USER_PHONE, name="Debug User")
if not cid:
    print("❌ Could not resolve Contact ID.")
    exit()

print(f"✅ Contact ID: {cid}")

# 2. Get Conversations
# We need to find the conversation ID linked to this contact.
headers = {
    "Authorization": f"Bearer {dispatcher.ghl_token}",
    "Version": "2021-07-28",
    "Accept": "application/json"
}
url = f"https://services.leadconnectorhq.com/conversations/search?contactId={cid}"
res = requests.get(url, headers=headers)

if res.status_code == 200:
    data = res.json()
    convs = data.get('conversations', [])
    print(f"Found {len(convs)} Conversations.")
    for c in convs:
        print(f"--- Conv {c['id']} ---")
        print(f"Last Msg: {c.get('lastMessageBody')}")
        print(f"Direction: {c.get('lastMessageDirection')}")
        print(f"Unread: {c.get('unreadCount')}")
        # print(json.dumps(c, indent=2))
else:
    print(f"❌ Search Failed: {res.text}")
