
import requests
try:
    r = requests.get("https://empire-unified-backup-production.up.railway.app/stats", timeout=10)
    print(r.status_code)
    print(r.json())
except Exception as e:
    print(e)
