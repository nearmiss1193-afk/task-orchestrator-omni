"""Deep check: get detailed call info to see if server messages were sent"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}'}

# Get the most recent call with full details
call_id = '019c4dde-3a6f-788f-9596-bfefeb46e004'  # Most recent
r = requests.get(f'https://api.vapi.ai/call/{call_id}', headers=headers)
call = r.json()

print("=== FULL CALL DETAILS ===")
# Print key fields
important_keys = ['id', 'status', 'duration', 'endedReason', 'serverUrl', 
                  'serverMessages', 'assistantId', 'phoneNumberId', 
                  'createdAt', 'endedAt', 'messages']
for k in important_keys:
    val = call.get(k)
    if k == 'messages' and val:
        print(f"\n{k}: ({len(val)} messages)")
        for m in val[-5:]:  # Last 5 messages
            print(f"  role={m.get('role','?')} | {str(m.get('message',''))[:80]}")
    elif k == 'serverUrl':
        print(f"{k}: {val if val else 'NULL/MISSING'}")
    else:
        val_str = str(val)[:100] if val else 'NULL'
        print(f"{k}: {val_str}")

# Check if there's an artifact/analysis field
print(f"\nassistant config's serverUrl: {call.get('assistant', {}).get('serverUrl', 'NOT IN RESPONSE')}")
print(f"phoneNumber config: {json.dumps(call.get('phoneNumber', {}), indent=2)[:300]}")
