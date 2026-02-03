
import os
import requests

def get_assistant_id():
    api_key = "c23c884d-0008-4b16-4eaf-8fb9-53d308f54a0e"
    url = "https://api.vapi.ai/assistant"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        res = requests.get(url, headers=headers)
        data = res.json()
        print(f"DEBUG: Data type is {type(data)}")
        
        if isinstance(data, list):
            for a in data:
                name = a.get("name", "")
                if "Sovereign" in name or "Executive" in name:
                    print(f"ID_FOUND:{a.get('id')}:{name}")
        elif isinstance(data, dict):
             # Some APIs return { "assistants": [...] }
             assistants = data.get("assistants", [])
             for a in assistants:
                name = a.get("name", "")
                if "Sovereign" in name or "Executive" in name:
                    print(f"ID_FOUND:{a.get('id')}:{name}")
        else:
            print(f"UNEXPECTED_DATA:{data}")
            
    except Exception as e:
        print(f"ERROR:{e}")

if __name__ == "__main__":
    get_assistant_id()
