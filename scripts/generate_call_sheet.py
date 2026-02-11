"""
Generate Dan's personalized call sheet.
Columns: Business, Contact, Phone, Niche, Last Outreach (channel+date), What's Broken, The Offer, Website URL, Email
"""
import os, csv, json
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')
from supabase import create_client

s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

print("=" * 60)
print("  GENERATING PERSONALIZED CALL SHEET")
print("=" * 60)

# 1. Get all contacts with phone numbers
contacts = s.table('contacts_master').select(
    'id,company_name,full_name,phone,email,niche,status,website_url,raw_research,ai_strategy'
).neq('phone', '').order('niche').execute()
print(f"Contacts with phone: {len(contacts.data)}")

# 2. Get outbound touches - uses phone as link, not contact_id
touches = s.table('outbound_touches').select(
    'phone,ts,channel,variant_name,status'
).order('ts', desc=True).execute()
print(f"Total outbound touches: {len(touches.data)}")

# Build lookup: phone -> most recent touch
touch_lookup = {}
for t in touches.data:
    phone = t.get('phone', '')
    if phone and phone not in touch_lookup:
        touch_lookup[phone] = {
            'date': t.get('ts', '')[:10] if t.get('ts') else 'Unknown',
            'channel': t.get('channel', '?'),
            'variant': t.get('variant_name', 'Standard outreach'),
            'status': t.get('status', '?'),
        }

print(f"Unique phones with outreach history: {len(touch_lookup)}")

# 3. Parse audit findings from raw_research / ai_strategy
def extract_findings(contact):
    findings = []
    raw = contact.get('raw_research') or ''
    strategy = contact.get('ai_strategy') or ''

    for data_str in [raw, strategy]:
        if not data_str:
            continue
        try:
            if isinstance(data_str, str) and (data_str.startswith('{') or data_str.startswith('[')):
                data = json.loads(data_str)
            elif isinstance(data_str, dict):
                data = data_str
            else:
                data = {}
            if isinstance(data, dict):
                for key in ['issues', 'findings', 'problems', 'recommendations', 'website_issues',
                            'seo_issues', 'technical_issues', 'pain_points']:
                    if key in data:
                        val = data[key]
                        if isinstance(val, list):
                            findings.extend([str(v) for v in val[:3]])
                        elif isinstance(val, str):
                            findings.append(val)
        except:
            pass

    combined = (str(raw) + ' ' + str(strategy)).lower()
    if not findings:
        if 'ssl' in combined or 'not secure' in combined:
            findings.append('SSL/Security issue')
        if 'mobile' in combined or 'responsive' in combined:
            findings.append('Not mobile-friendly')
        if 'slow' in combined or 'speed' in combined:
            findings.append('Slow page load')
        if 'seo' in combined or 'meta' in combined:
            findings.append('Missing SEO basics')
        if 'broken' in combined:
            findings.append('Broken links/pages')

    return findings[:3] if findings else ['Needs website audit']

def generate_offer(findings, has_website):
    if not has_website:
        return "Free one-page website setup"
    f_lower = ' '.join(findings).lower()
    if 'ssl' in f_lower or 'security' in f_lower:
        return "Free SSL/security fix"
    if 'mobile' in f_lower:
        return "Free mobile optimization audit"
    if 'slow' in f_lower or 'speed' in f_lower:
        return "Free speed optimization"
    if 'seo' in f_lower:
        return "Free SEO quick-fix (titles, meta)"
    if 'broken' in f_lower:
        return "Free broken link/page fix"
    return "Free 5-min website health check"

# 4. Generate CSV
output_path = os.path.join('scripts', 'call_sheet.csv')
rows_written = 0

with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Business Name', 'Contact Name', 'Phone', 'Niche',
        'Last Outreach', 'Outreach Date', 'Channel',
        "What's Broken", 'Your Offer', 'Website URL', 'Email'
    ])

    for c in contacts.data:
        company = c.get('company_name') or 'Unknown Business'
        contact_name = c.get('full_name') or 'Business Owner'
        phone = c.get('phone', '')
        niche = c.get('niche') or 'Local Business'
        website = c.get('website_url') or ''
        email = c.get('email') or ''

        # Outreach history — match by phone
        touch = touch_lookup.get(phone, {})
        last_outreach = f"{touch.get('channel','None')} - {touch.get('variant','No outreach yet')}" if touch else 'No outreach yet'
        outreach_date = touch.get('date', 'N/A') if touch else 'N/A'
        outreach_channel = touch.get('channel', 'None') if touch else 'None'

        findings = extract_findings(c)
        findings_str = '; '.join(findings)
        offer = generate_offer(findings, bool(website))

        writer.writerow([
            company, contact_name, phone, niche,
            last_outreach, outreach_date, outreach_channel,
            findings_str, offer, website, email
        ])
        rows_written += 1

print(f"\nCall sheet generated: scripts/call_sheet.csv")
print(f"{rows_written} rows written")

# 5. Preview
print(f"\n{'='*60}")
print("  PREVIEW (first 5 rows)")
print(f"{'='*60}")
with open(output_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for i, row in enumerate(reader):
        if i >= 5:
            break
        print(f"\n  {row[0]}")
        print(f"     Contact: {row[1]} | Phone: {row[2]}")
        print(f"     Niche: {row[3]}")
        print(f"     Last Outreach: {row[4]} ({row[5]})")
        print(f"     Broken: {row[7]}")
        print(f"     Offer: {row[8]}")
        print(f"     Website: {row[9]}")

# 6. Niche breakdown
niche_counts = {}
with open(output_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        n = row['Niche']
        niche_counts[n] = niche_counts.get(n, 0) + 1

print(f"\n{'='*60}")
print("  BREAKDOWN BY NICHE")
print(f"{'='*60}")
for n, c in sorted(niche_counts.items(), key=lambda x: -x[1]):
    print(f"  {n}: {c}")
