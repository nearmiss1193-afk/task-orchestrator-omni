"""
Execute all onboarding prep in one shot:
1. Reassign Rachel to +18636928474 in Vapi
2. Create Stripe payment links for both businesses
3. Set 2:15 PM reminder for Tiffany
"""
import os, json, subprocess
import requests
from dotenv import load_dotenv
load_dotenv('.env')

VAPI_KEY = os.environ['VAPI_PRIVATE_KEY']
STRIPE_KEY = os.environ['STRIPE_SECRET_KEY']
RACHEL_ASSISTANT_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"
PHONE_NUMBER_ID = "c2afdc74-8d2a-4ebf-8736-7eecc1992204"  # +18636928474

results = []

# ===== 1. REASSIGN RACHEL TO PHONE NUMBER =====
print("=" * 50)
print("1. REASSIGNING RACHEL TO +18636928474")
print("=" * 50)

r = requests.patch(
    f"https://api.vapi.ai/phone-number/{PHONE_NUMBER_ID}",
    headers={
        "Authorization": f"Bearer {VAPI_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "assistantId": RACHEL_ASSISTANT_ID,
        "name": "Rachel (Onboarding)"
    }
)

if r.status_code == 200:
    data = r.json()
    print(f"SUCCESS: +18636928474 now assigned to Rachel")
    print(f"  Assistant: {data.get('assistantId')}")
    print(f"  Name: {data.get('name')}")
    results.append("1. Rachel -> +18636928474: SUCCESS")
else:
    print(f"FAILED: {r.status_code} - {r.text[:200]}")
    results.append(f"1. Rachel -> +18636928474: FAILED ({r.status_code})")

# ===== 2. CREATE STRIPE PAYMENT LINKS =====
print("\n" + "=" * 50)
print("2. CREATING STRIPE PAYMENT LINKS")
print("=" * 50)

headers = {
    "Authorization": f"Bearer {STRIPE_KEY}",
    "Content-Type": "application/x-www-form-urlencoded"
}

# First check existing products
r = requests.get(
    "https://api.stripe.com/v1/products?limit=10",
    headers={"Authorization": f"Bearer {STRIPE_KEY}"}
)
existing = r.json().get('data', [])
print(f"Existing Stripe products: {len(existing)}")
for p in existing:
    print(f"  - {p['name']} ({p['id']}) active={p.get('active')}")

# Create product + price + payment link for Embracing Concerns
print("\nCreating: Embracing Concerns (Home Health) payment link...")
try:
    # Product
    r1 = requests.post("https://api.stripe.com/v1/products", headers=headers, data={
        "name": "AI Office Agent - Embracing Concerns (Home Health)",
        "description": "24/7 AI Receptionist & Office Manager for Embracing Concerns Home Health. Handles calls, scheduling, patient inquiries, and follow-ups."
    })
    product1 = r1.json()
    print(f"  Product: {product1.get('id', 'ERROR')}")
    
    # Price ($297/mo)
    r2 = requests.post("https://api.stripe.com/v1/prices", headers=headers, data={
        "product": product1['id'],
        "unit_amount": "29700",
        "currency": "usd",
        "recurring[interval]": "month"
    })
    price1 = r2.json()
    print(f"  Price: {price1.get('id', 'ERROR')} ($297/mo)")
    
    # Payment Link
    r3 = requests.post("https://api.stripe.com/v1/payment_links", headers=headers, data={
        "line_items[0][price]": price1['id'],
        "line_items[0][quantity]": "1",
        "after_completion[type]": "redirect",
        "after_completion[redirect][url]": "https://1staistep.com/welcome"
    })
    link1 = r3.json()
    link1_url = link1.get('url', 'ERROR')
    print(f"  Payment Link: {link1_url}")
    results.append(f"2a. Embracing Concerns link: {link1_url}")
except Exception as e:
    print(f"  ERROR: {e}")
    results.append(f"2a. Embracing Concerns: FAILED - {e}")
    link1_url = "ERROR"

# Create product + price + payment link for Clear Cut Tree Masters
print("\nCreating: Clear Cut Tree Masters payment link...")
try:
    r4 = requests.post("https://api.stripe.com/v1/products", headers=headers, data={
        "name": "AI Office Agent - Clear Cut Tree Masters",
        "description": "24/7 AI Receptionist for Clear Cut Tree Masters. Handles calls, job estimates, scheduling, and customer follow-ups."
    })
    product2 = r4.json()
    print(f"  Product: {product2.get('id', 'ERROR')}")
    
    r5 = requests.post("https://api.stripe.com/v1/prices", headers=headers, data={
        "product": product2['id'],
        "unit_amount": "29700",
        "currency": "usd",
        "recurring[interval]": "month"
    })
    price2 = r5.json()
    print(f"  Price: {price2.get('id', 'ERROR')} ($297/mo)")
    
    r6 = requests.post("https://api.stripe.com/v1/payment_links", headers=headers, data={
        "line_items[0][price]": price2['id'],
        "line_items[0][quantity]": "1",
        "after_completion[type]": "redirect",
        "after_completion[redirect][url]": "https://1staistep.com/welcome"
    })
    link2 = r6.json()
    link2_url = link2.get('url', 'ERROR')
    print(f"  Payment Link: {link2_url}")
    results.append(f"2b. Clear Cut Tree Masters link: {link2_url}")
except Exception as e:
    print(f"  ERROR: {e}")
    results.append(f"2b. Clear Cut Tree Masters: FAILED - {e}")
    link2_url = "ERROR"

# ===== 3. SET 2:15 PM REMINDER =====
print("\n" + "=" * 50)
print("3. SETTING 2:15 PM REMINDER FOR TIFFANY")
print("=" * 50)

try:
    result = subprocess.run([
        'schtasks', '/create', '/tn', 'TiffanyCallback215',
        '/tr', 'powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show(\'CALL IN 15 MIN! Tiffany - Embracing Concerns (Home Health) - Onboarding at 2:30 PM\', \'ONBOARDING REMINDER\', \'OK\', \'Warning\')"',
        '/sc', 'once', '/st', '14:15', '/sd', '02/18/2026', '/f'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("SUCCESS: 2:15 PM reminder set")
        results.append("3. Tiffany 2:15 PM reminder: SET")
    else:
        print(f"FAILED: {result.stderr}")
        results.append("3. Tiffany reminder: FAILED")
except Exception as e:
    print(f"ERROR: {e}")
    results.append(f"3. Reminder: FAILED - {e}")

# ===== SUMMARY =====
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
for r_line in results:
    print(f"  {r_line}")

# Save results + links to file
with open('scripts/onboarding_prep_result.txt', 'w', encoding='ascii', errors='replace') as f:
    f.write("\n".join(results))
    f.write(f"\n\nSTRIPE LINKS:\n")
    f.write(f"Embracing Concerns: {link1_url}\n")
    f.write(f"Clear Cut Tree Masters: {link2_url}\n")
