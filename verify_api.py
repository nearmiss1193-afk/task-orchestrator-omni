import requests

url = "https://nearmiss1193-afk--ghl-omni-automation-api-list-files.modal.run"
try:
    print(f"Testing {url}...")
    res = requests.get(url)
    print(f"Status: {res.status_code}")
    print(f"Content: {res.text[:200]}...")
except Exception as e:
    print(f"Error: {e}")

url2 = "https://nearmiss1193-afk--ghl-omni-automation-api-read-file.modal.run" # underscores might be hyphens
try:
    print(f"Testing {url2}?path=README.md...")
    res = requests.get(url2 + "?path=README.md")
    print(f"Status: {res.status_code}")
    print(f"Content: {res.text[:200]}...")
except Exception as e:
    print(f"Error: {e}")
