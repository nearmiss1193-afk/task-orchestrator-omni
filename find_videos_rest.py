
import requests
import json
import os

def find_videos_rest():
    url = "https://rzcpfwkygdvoshtwxncs.supabase.co/rest/v1/outbound_touches?channel=eq.social&order=ts.desc&limit=20"
    headers = {
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        with open("raw_social_touches.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"Captured {len(data)} touches.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_videos_rest()
