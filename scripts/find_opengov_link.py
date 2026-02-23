import requests
from bs4 import BeautifulSoup

url = "https://www.lakelandgov.net/departments/purchasing/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

found = set()
for a in soup.find_all('a', href=True):
    if 'opengov' in a['href'].lower() or 'procurement' in a['href'].lower():
        found.add(a['href'])

for val in found:
    print("Found potential link:", val)

if not found:
    print("No obvious procurement links found. Trying to print all links to find patterns.")
    for a in soup.find_all('a', href=True)[:20]:
        print(a['href'])
