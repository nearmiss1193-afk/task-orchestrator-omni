import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': 'Bearer ' + key}

def get_assistants():
    r = requests.get('https://api.vapi.ai/assistant', headers=headers)
    if r.status_code == 200:
        data = r.json()
        print(json.dumps([{'id': a.get('id'), 'name': a.get('name')} for a in data], indent=2))
        with open('assistants_map.json', 'w') as f:
            json.dump(data, f, indent=2)
    else:
        print(f"Error: {r.status_code} - {r.text}")

if __name__ == "__main__":
    get_assistants()
