import json
import sys

try:
    with open('modal_list.json', 'r', encoding='utf-16') as f:
        data = json.load(f)
except:
    try:
        with open('modal_list.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print("Failed to load JSON")
        sys.exit(1)

print(f"Total Apps: {len(data)}")
if len(data) > 0:
    print(f"Keys: {list(data[0].keys())}")

for app in data:
    state = app.get("State")
    if state == "deployed":
        print(f"{app.get('App ID')} | {app.get('Description', 'Unknown')}")
