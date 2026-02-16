import requests
import re
import json

urls = [
    "https://manus.im/share/file/c6858721-1153-498e-92fb-f2865e73d799",
    "https://manus.im/share/file/d39b9b83-5ffd-43ce-845a-66dad9664ce1",
    "https://manus.im/share/file/b216f77a-7e1b-4e47-99e6-c7c13b5347df"
]

for url in urls:
    print(f"--- FETCHING: {url} ---")
    try:
        response = requests.get(url, timeout=10)
        # Look for script tags containing JSON data
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});</script>', response.text)
        if match:
            state = json.loads(match.group(1))
            # Just print keys and a peek to understand structure
            print(f"Keys: {state.keys()}")
            # Print specifically for recruitment data
            if 'file' in state:
                print(f"File Content Preview: {str(state['file'])[:1000]}")
        else:
            print("No INITIAL_STATE found. Content might be dynamic.")
    except Exception as e:
        print(f"Error: {e}")
