import os
import requests
import zipfile
import base64
from dotenv import load_dotenv

load_dotenv()

GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/uFYcZA7Zk6EcBze5B4oH/webhook-trigger/4ac9b8e9-d444-461d-840b-a14ebf09c4dc"

include_files = [
    'public/index.html', 'public/features.html', 'public/media.html', 'public/payment.html',
    'public/assets/sarah-widget.js', 'operational_memory.md', 'scripts/traffic_light_automation.py'
]

zip_name = "aiserviceco-full-project-v1.zip"

print("📦 Zipping...")
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in include_files:
        if os.path.exists(f):
            z.write(f, os.path.basename(f))
    for sf in os.listdir('sql'):
        if sf.endswith('.sql'):
            z.write(os.path.join('sql', sf), f'sql/{sf}')

size_mb = os.path.getsize(zip_name) / 1024 / 1024
print(f"✅ ZIP: {size_mb:.2f} MB")

print("📧 Sending via GHL...")
payload = {
    "email": "nearmiss1193@gmail.com",
    "subject": "FULL PROJECT ZIP – FOR ARA",
    "body": f"Here's the zipped project ({size_mb:.2f} MB). Check drift, fix site, return clean code. File is in project root: aiserviceco-full-project-v1.zip"
}
res = requests.post(GHL_EMAIL_WEBHOOK, json=payload)
if res.status_code in [200, 201, 204]:
    print(f"✅ EMAIL SENT via GHL – {size_mb:.2f} MB")
else:
    print(f"❌ GHL Failed: {res.text}")
