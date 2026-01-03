
import requests
import json

url = "http://localhost:3000/api/leads"
data = {
    "name": "Backend Test",
    "phone": "555-BACKEND",
    "email": "backend@test.com",
    "industry": "TEST_AUTO"
}
try:
    print(f"POST {url}")
    res = requests.post(url, json=data)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Error: {e}")
