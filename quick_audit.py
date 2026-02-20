"""Quick script to:
1. Count CRONs in deploy.py
2. Export ALL contacts from Supabase to CSV on Desktop
"""
import os, csv, requests

# --- CRON COUNT ---
print("=" * 50)
print("CRON AUDIT")
print("=" * 50)
cron_count = 0
with open("deploy.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "schedule=modal.Cron" in line:
            cron_count += 1
            # Find function name
            func = "unknown"
            for j in range(i, min(i + 5, len(lines))):
                if "def " in lines[j]:
                    func = lines[j].strip().split("def ")[1].split("(")[0]
                    break
            schedule = line.split('Cron("')[1].split('")')[0] if 'Cron("' in line else "?"
            print(f"  {cron_count}. {func} -> {schedule}")

print(f"\nTotal CRONs: {cron_count} / 5 max")
if cron_count > 5:
    print("  *** OVER LIMIT! ***")
else:
    print(f"  OK ({5 - cron_count} slots remaining)")

# --- CSV EXPORT ---
print("\n" + "=" * 50)
print("GHL CSV EXPORT")
print("=" * 50)

# Load key from .env
key = None
for line in open(".env", "r", encoding="utf-8"):
    line = line.strip()
    if line.startswith("SUPABASE_KEY="):
        key = line.split("=", 1)[1]
        break

if not key:
    print("ERROR: No SUPABASE_KEY in .env")
    exit(1)

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}

all_leads = []
offset = 0
batch = 1000

while True:
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/contacts_master",
        headers=headers,
        params={
            "select": "id,full_name,email,phone,company_name,niche,status,lead_source,website_url",
            "status": "in.(new,research_done,outreach_sent,sequence_complete)",
            "offset": str(offset),
            "limit": str(batch),
        },
    )
    if resp.status_code != 200:
        print(f"ERROR {resp.status_code}: {resp.text[:200]}")
        break
    data = resp.json()
    if not data:
        break
    all_leads.extend(data)
    print(f"  Fetched {len(all_leads)} leads so far...")
    if len(data) < batch:
        break
    offset += batch

contactable = [l for l in all_leads if l.get("phone") or l.get("email")]

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
output_path = os.path.join(desktop, "ghl_contact_import.csv")

with open(output_path, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["First Name", "Last Name", "Email", "Phone", "Company Name", "Tags", "Website", "Source"])
    for lead in contactable:
        name = (lead.get("full_name") or "").strip()
        parts = name.split(" ", 1)
        first = parts[0] if parts else ""
        last = parts[1] if len(parts) > 1 else ""
        phone = (lead.get("phone") or "").replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
        if phone and not phone.startswith("+"):
            phone = f"+1{phone}"
        tags = ["import:supabase"]
        if lead.get("status"):
            tags.append(f"status:{lead['status']}")
        if lead.get("niche"):
            tags.append(f"niche:{lead['niche']}")
        w.writerow([
            first, last,
            lead.get("email") or "",
            phone,
            lead.get("company_name") or "",
            ", ".join(tags),
            lead.get("website_url") or "",
            lead.get("lead_source") or "supabase",
        ])

print(f"\nTotal fetched: {len(all_leads)}")
print(f"Contactable: {len(contactable)}")
print(f"Saved to: {output_path}")
