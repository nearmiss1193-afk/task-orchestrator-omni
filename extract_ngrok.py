import requests
try:
    response = requests.get("http://127.0.0.1:4040/api/tunnels")
    data = response.json()
    public_url = data['tunnels'][0]['public_url']
    print(f"NGROK_URL={public_url}")
    with open("ngrok.txt", "w") as f:
        f.write(public_url.strip())
except Exception as e:
    print(f"Error: {e}")
