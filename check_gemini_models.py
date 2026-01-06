
import os
import requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

key = os.environ.get('GEMINI_API_KEY', '')
print(f"Key: {key[:15]}..." if key else "No key found")

# List available models
url = f'https://generativelanguage.googleapis.com/v1beta/models?key={key}'
r = requests.get(url)
print(f"\nStatus: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print("\nAvailable models:")
    for m in data.get('models', [])[:15]:
        name = m.get('name', '')
        if 'flash' in name.lower() or 'pro' in name.lower():
            print(f"  -> {name}")
else:
    print(f"Error: {r.text[:200]}")
