
import requests
import sys

url = "https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-1.5-flash:streamGenerateContent?key=AIzaSyBJkAvxzQauCGEnAjz_oVu5qkOp73L7AUA"
payload = {"contents": [{"role": "user", "parts": [{"text": "Hello"}]}]}
try:
    r = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
    print(f"STATUS:{r.status_code}|BODY:{r.text[:200]}")
except Exception as e:
    print(f"ERROR:{e}")
