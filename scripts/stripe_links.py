"""Fix Stripe payment links - debug the API response"""
import os, requests
from dotenv import load_dotenv
load_dotenv('.env')

STRIPE_KEY = os.environ['STRIPE_SECRET_KEY']
headers = {"Authorization": f"Bearer {STRIPE_KEY}"}

# First check if products were partially created
r = requests.get("https://api.stripe.com/v1/products?limit=20", headers=headers)
data = r.json()
print(f"Status: {r.status_code}")
print(f"Products found: {len(data.get('data',[]))}")

for p in data.get('data', []):
    print(f"  {p['name']} | {p['id']} | active={p.get('active')}")

# Try creating product with explicit form data
print("\n--- Creating Embracing Concerns product ---")
r1 = requests.post(
    "https://api.stripe.com/v1/products",
    headers=headers,
    data={
        "name": "AI Office Agent - Embracing Concerns",
        "description": "24/7 AI Receptionist for Home Health"
    }
)
print(f"Response: {r1.status_code}")
resp1 = r1.json()
print(f"Body: {str(resp1)[:300]}")

if r1.status_code == 200:
    pid = resp1['id']
    print(f"Product ID: {pid}")
    
    # Create price
    r2 = requests.post("https://api.stripe.com/v1/prices", headers=headers, data={
        "product": pid,
        "unit_amount": "29700",
        "currency": "usd",
        "recurring[interval]": "month"
    })
    print(f"Price: {r2.status_code} - {str(r2.json())[:200]}")
    
    if r2.status_code == 200:
        price_id = r2.json()['id']
        
        # Create payment link
        r3 = requests.post("https://api.stripe.com/v1/payment_links", headers=headers, data={
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": "1"
        })
        print(f"Link: {r3.status_code} - {str(r3.json())[:300]}")
        if r3.status_code == 200:
            print(f"\nEMBRACING CONCERNS LINK: {r3.json()['url']}")

print("\n--- Creating Clear Cut Tree Masters product ---")
r4 = requests.post(
    "https://api.stripe.com/v1/products",
    headers=headers,
    data={
        "name": "AI Office Agent - Clear Cut Tree Masters",
        "description": "24/7 AI Receptionist for Tree Service"
    }
)
print(f"Response: {r4.status_code}")
resp4 = r4.json()
print(f"Body: {str(resp4)[:300]}")

if r4.status_code == 200:
    pid2 = resp4['id']
    
    r5 = requests.post("https://api.stripe.com/v1/prices", headers=headers, data={
        "product": pid2,
        "unit_amount": "29700",
        "currency": "usd",
        "recurring[interval]": "month"
    })
    print(f"Price: {r5.status_code} - {str(r5.json())[:200]}")
    
    if r5.status_code == 200:
        price_id2 = r5.json()['id']
        
        r6 = requests.post("https://api.stripe.com/v1/payment_links", headers=headers, data={
            "line_items[0][price]": price_id2,
            "line_items[0][quantity]": "1"
        })
        print(f"Link: {r6.status_code} - {str(r6.json())[:300]}")
        if r6.status_code == 200:
            print(f"\nCLEAR CUT LINK: {r6.json()['url']}")

# Save all links
links = {}
try:
    if r3.status_code == 200: links['embracing'] = r3.json()['url']
    if r6.status_code == 200: links['clearcut'] = r6.json()['url']
except: pass

with open('scripts/stripe_links.md', 'w', encoding='utf-8') as f:
    f.write(f"Embracing Concerns: {links.get('embracing','FAILED')}\n")
    f.write(f"Clear Cut Tree Masters: {links.get('clearcut','FAILED')}\n")
