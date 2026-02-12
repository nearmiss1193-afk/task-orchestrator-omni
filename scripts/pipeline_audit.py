import os
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
from supabase import create_client
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY'))

# 1. Lead status breakdown
print("=" * 50)
print("CONTACTS_MASTER STATUS BREAKDOWN")
print("=" * 50)
all_leads = sb.table('contacts_master').select('status', count='exact').execute()
print("Total leads: " + str(all_leads.count))

# Get distinct statuses
statuses = sb.table('contacts_master').select('status').execute()
status_counts = {}
for row in statuses.data:
    s = row.get('status', 'NULL')
    status_counts[s] = status_counts.get(s, 0) + 1

for s, c in sorted(status_counts.items(), key=lambda x: -x[1]):
    print("  " + str(s) + ": " + str(c))

# 2. Sample of recently added leads
print("\n" + "=" * 50)
print("MOST RECENT 5 LEADS (by creation)")
print("=" * 50)
recent = sb.table('contacts_master').select('*').order('created_at', desc=True).limit(5).execute()
if recent.data:
    for r in recent.data:
        name = r.get('business_name') or r.get('name') or r.get('first_name', '') + ' ' + r.get('last_name', '')
        print("  " + str(r.get('created_at', '?'))[:19] + " | " + str(r.get('status', '?')) + " | " + str(name)[:40] + " | email: " + str(bool(r.get('email'))) + " | phone: " + str(bool(r.get('phone'))))

# 3. Check if any leads were added TODAY
print("\n" + "=" * 50)
print("LEADS ADDED TODAY")
print("=" * 50)
today = sb.table('contacts_master').select('*', count='exact').gte('created_at', '2026-02-11T00:00:00').execute()
print("Leads added today: " + str(today.count))

# 4. Check how many have email vs don't
print("\n" + "=" * 50)
print("CONTACT INFO AVAILABILITY")
print("=" * 50)
with_email = sb.table('contacts_master').select('*', count='exact').not_.is_('email', 'null').execute()
with_phone = sb.table('contacts_master').select('*', count='exact').not_.is_('phone', 'null').execute()
print("With email: " + str(with_email.count))
print("With phone: " + str(with_phone.count))

# 5. The 1 contactable lead
print("\n" + "=" * 50)
print("THE CONTACTABLE LEAD(S)")
print("=" * 50)
contactable = sb.table('contacts_master').select('*').in_('status', ['new', 'research_done']).execute()
for r in contactable.data:
    name = r.get('business_name') or r.get('name') or 'Unknown'
    print("  Status: " + str(r.get('status')))
    print("  Name: " + str(name))
    print("  Email: " + str(r.get('email', 'NONE')))
    print("  Phone: " + str(r.get('phone', 'NONE')))
    print("  Created: " + str(r.get('created_at', '?'))[:19])
