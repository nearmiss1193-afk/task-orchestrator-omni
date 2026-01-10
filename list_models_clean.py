import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('GEMINI_API_KEY')
# Use the list models endpoint
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

try:
    res = requests.get(url)
    data = res.json()
    if 'models' in data:
        print(f"Found {len(data['models'])} models.")
        for m in data['models']:
            if 'gemini' in m['name'] and 'flash' in m['name']:
                print(f"ID: {m['name']}")
    else:
        print(json.dumps(data, indent=2))
except Exception as e:
    print(e)
