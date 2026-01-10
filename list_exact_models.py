import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('GEMINI_API_KEY')
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

try:
    response = requests.get(url)
    data = response.json()
    if 'models' in data:
        print("AVAILABLE MODELS:")
        for m in data['models']:
            print(f"- {m['name']}")
    else:
        print("ERROR:", data)
except Exception as e:
    print("CRASH:", e)
