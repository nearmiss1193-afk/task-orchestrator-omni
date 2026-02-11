"""Check actual touch dates — are any leads 3+ days old?"""
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')
import os
from supabase import create_client

s = create_client(
    os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

# Oldest touches
oldest = s.table('outbound_touches').select('ts,company,variant_id').order('ts', desc=False).limit(5).execute()
print("Oldest 5 touches:")
for r in oldest.data:
    print("  %s | %s | %s" % (str(r.get('ts',''))[:22], r.get('variant_id',''), r.get('company','')))

# Newest touches
newest = s.table('outbound_touches').select('ts,company,variant_id').order('ts', desc=True).limit(5).execute()
print("\nNewest 5 touches:")
for r in newest.data:
    print("  %s | %s | %s" % (str(r.get('ts',''))[:22], r.get('variant_id',''), r.get('company','')))

# Total touches
total = s.table('outbound_touches').select('ts', count='exact').execute()
print("\nTotal touches all time: %d" % (total.count or 0))

# Touches by date
from datetime import datetime, timezone, timedelta
for days_ago in [0, 1, 2, 3, 7]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    ct = s.table('outbound_touches').select('ts', count='exact').gte('ts', cutoff).execute()
    print("  Last %d days: %d" % (days_ago, ct.count or 0))

# Check leads created_at distribution
print("\nLead created_at distribution:")
for days_ago in [0, 1, 3, 7, 14, 30]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    ct = s.table('contacts_master').select('id', count='exact').gte('created_at', cutoff).execute()
    print("  Created in last %d days: %d" % (days_ago, ct.count or 0))
