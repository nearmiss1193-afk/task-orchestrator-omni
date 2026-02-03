import requests

URL = "https://rzcpfwkygdvoshtwxncs.supabase.co/rest/v1/"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

def inspect():
    headers = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
    try:
        r = requests.get(URL, headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            definitions = r.json().get('definitions', {})
            print("Exposed Tables:")
            for table in definitions.keys():
                print(f" - {table}")
        else:
            print(r.text)
    except Exception as e:
        print(e)
inspect()
