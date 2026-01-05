
import os
import requests
import json
try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

token = os.environ.get("GHL_API_TOKEN")
loc = os.environ.get("GHL_LOCATION_ID")

print(f"--- GHL STATE PROBE ---")
print(f"Location: {loc}")

headers = {
    "Authorization": f"Bearer {token}",
    "Version": "2021-07-28",
    "Accept": "application/json"
}

# 1. Search for conversation
url = f"https://services.leadconnectorhq.com/conversations/search?limit=5&sort=desc&sortBy=last_message_date&locationId={loc}"
res = requests.get(url, headers=headers)

if res.status_code == 200:
    convs = res.json().get('conversations', [])
    print(f"Found {len(convs)} active conversations.")
    for c in convs:
        name = c.get('contactName', 'Unknown')
        body = c.get('lastMessageBody', '')
        direction = c.get('lastMessageDirection', '')
        print(f"\n[CONV] {name} ({c['id']})")
        print(f"       Last Msg: {body} ({direction})")
        
        # 2. Get Messages
        m_url = f"https://services.leadconnectorhq.com/conversations/{c['id']}/messages"
        m_res = requests.get(m_url, headers=headers)
        if m_res.status_code == 200:
            msgs = m_res.json().get('messages', [])
            print(f"       History (Last 3):")
            for m in msgs[:3]:
                print(f"         - [{m.get('direction')}] {m.get('body')}")
else:
    print(f"Error: {res.status_code} - {res.text}")
