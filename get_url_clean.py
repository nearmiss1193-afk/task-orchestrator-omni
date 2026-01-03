import requests
try:
    u = requests.get("http://127.0.0.1:4040/api/tunnels").json()['tunnels'][0]['public_url']
    with open("clean_url_final.txt", "w") as f:
        f.write(u.strip())
except:
    pass
