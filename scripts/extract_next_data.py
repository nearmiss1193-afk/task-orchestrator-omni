import requests
from bs4 import BeautifulSoup
import json

url = "https://procurement.opengov.com/portal/lakelandgov"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')

next_data = soup.find('script', id='__NEXT_DATA__')
if next_data:
    data = json.loads(next_data.string)
    # The bids are usually in props.pageProps.initialState or similar
    try:
        projects = data['props']['pageProps']['initialState']['portals']['activePortal']['projects']
        print(f"BINGO! Found {len(projects)} projects directly in JSON.")
        for p in projects[:3]:
            print(f"- {p.get('title')} (Closes: {p.get('dueDate')})")
    except KeyError as e:
        print("KeyError navigating the JSON:", e)
        # dump the keys
        print(data['props'].keys())
        if 'pageProps' in data['props']:
             print(data['props']['pageProps'].keys())
else:
    print("No __NEXT_DATA__ script block found.")
