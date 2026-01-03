
import requests
import json

try:
    res = requests.get('http://localhost:3000/api/crm/clients')
    print("Status:", res.status_code)
    print("Clients:", json.dumps(res.json(), indent=2))
except Exception as e:
    print("Error:", e)
