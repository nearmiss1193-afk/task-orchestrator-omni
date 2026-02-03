
import requests
import json

def list_assistants():
    key = "c412e873-10e3-4de9-9e12-309d49479e0a"
    url = "https://api.vapi.ai/assistant"
    headers = {"Authorization": f"Bearer {key}"}
    
    try:
        r = requests.get(url, headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code != 200:
            print(f"Response: {r.text}")
            return
            
        data = r.json()
        
        # Vapi can return a list or a dict with an 'assistants' key
        assistants = data if isinstance(data, list) else data.get('assistants', [])
        
        print("--- VAPI ASSISTANTS ---")
        for a in assistants:
            print(f"NAME: {a.get('name')} | ID: {a.get('id')}")
        print("-----------------------")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_assistants()
