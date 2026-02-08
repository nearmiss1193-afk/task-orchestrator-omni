"""
Phone Number Migration Script - Sarah Memory Fix
Board Approved: 4/4 (Claude, ChatGPT, Gemini, Grok)

Purpose: Normalize all phone numbers in customer_memory to E.164 format
Run ONCE to fix existing records, then deploy updated code.
"""
import os
import re
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv('.env')
load_dotenv('.secrets/secrets.env')

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not url or not key:
    print("❌ Missing Supabase credentials")
    exit(1)

supabase = create_client(url, key)


def normalize_phone(raw_phone: str) -> str:
    """
    Standardize phone to E.164 format: +1XXXXXXXXXX
    Same logic as deploy.py to ensure consistency.
    """
    if not raw_phone:
        return ""
    digits = re.sub(r'\D', '', raw_phone)
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    elif len(digits) > 11:
        return f"+{digits}"  # Already has country code
    return f"+{digits}" if digits else ""


print("=" * 60)
print("PHONE NUMBER MIGRATION - Sarah Memory Fix")
print("=" * 60)
print(f"Timestamp: {datetime.now().isoformat()}")
print()

# Step 1: Backup current records
print("📦 Step 1: Backing up current records...")
records = supabase.table('customer_memory').select('*').execute()
backup_file = f"memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(backup_file, 'w') as f:
    json.dump(records.data, f, indent=2, default=str)
print(f"   ✅ Backup saved to {backup_file}")
print(f"   Total records: {len(records.data)}")
print()

# Step 2: Analyze and migrate
print("🔄 Step 2: Analyzing and migrating phone numbers...")
migrated = 0
skipped = 0
errors = []

for record in records.data:
    old_phone = record.get('phone_number', '')
    customer_id = record.get('customer_id')
    
    # Normalize
    new_phone = normalize_phone(old_phone)
    
    if not new_phone:
        print(f"   ⚠️ Skipping invalid: '{old_phone}'")
        skipped += 1
        continue
    
    if old_phone == new_phone:
        print(f"   ✓ Already normalized: {old_phone}")
        skipped += 1
        continue
    
    # Update the record
    print(f"   🔄 Migrating: '{old_phone}' → '{new_phone}'")
    
    try:
        result = supabase.table('customer_memory').update({
            'phone_number': new_phone,
            'last_interaction': datetime.now().isoformat()
        }).eq('customer_id', customer_id).execute()
        
        if result.data:
            migrated += 1
            print(f"      ✅ Success: {customer_id}")
        else:
            errors.append(f"No data returned for {customer_id}")
            print(f"      ❌ Failed: No data returned")
    except Exception as e:
        errors.append(f"{customer_id}: {str(e)}")
        print(f"      ❌ Error: {e}")

print()
print("=" * 60)
print("MIGRATION SUMMARY")
print("=" * 60)
print(f"   Migrated: {migrated}")
print(f"   Skipped:  {skipped}")
print(f"   Errors:   {len(errors)}")

if errors:
    print()
    print("Errors:")
    for e in errors:
        print(f"   - {e}")

# Step 3: Update Dan's record name
print()
print("🔄 Step 3: Updating Dan's record (fixing 'Michael' → 'Dan')...")
dan_phone = normalize_phone("(352) 936-8152")  # Dan's phone
print(f"   Looking for: {dan_phone}")

try:
    result = supabase.table('customer_memory').update({
        'context_summary': {
            "contact_name": "Dan",
            "questions_asked": ["business_type", "challenge"]
        },
        'last_interaction': datetime.now().isoformat()
    }).eq('phone_number', dan_phone).execute()
    
    if result.data:
        print(f"   ✅ Updated Dan's record context")
    else:
        print(f"   ⚠️ No record found for {dan_phone} (may have been migrated)")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("=" * 60)
print("VERIFICATION - Post-migration records:")
print("=" * 60)
final = supabase.table('customer_memory').select('phone_number,context_summary,last_interaction').execute()
for r in final.data:
    phone = r.get('phone_number', 'N/A')
    context = r.get('context_summary', {})
    name = context.get('contact_name', 'Unknown') if isinstance(context, dict) else 'Unknown'
    print(f"   {phone} → {name}")

print()
print("✅ Migration complete! Now deploy the updated code:")
print("   modal deploy deploy.py")
