import requests
from bs4 import BeautifulSoup

url = "https://www.lakelandgov.net/departments/purchasing/bid-opportunities/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

resp = requests.get(url, headers=headers)
print("Status Code:", resp.status_code)
if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    print("Page Title:", soup.title.string if soup.title else "No Title")
    
    # Let's try to find tables or lists containing bids
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables")
    
    # Try to find common keywords like "Bid" or "RFP"
    bids_found = 0
    for a in soup.find_all('a', href=True):
        text = a.text.strip().lower()
        if 'bid' in text or 'rfp' in text or 'rfq' in text or 'project' in text:
            print(f"Link: {text} -> {a['href']}")
            bids_found += 1
            if bids_found > 10:
                break
