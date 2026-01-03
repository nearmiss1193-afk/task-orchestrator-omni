import requests
import json

try:
    response = requests.get("http://127.0.0.1:4040/api/tunnels")
    data = response.json()
    public_url = data['tunnels'][0]['public_url']
    print(f"NGROK_URL={public_url}")
except Exception as e:
    print(f"Error fetching Ngrok URL: {e}")
