"""
SUPABASE DIAGNOSTIC V2 - Writes to file for full output
"""
import os
from dotenv import load_dotenv
load_dotenv()

output = []
output.append("="*60)
output.append("SUPABASE DIAGNOSTIC")
output.append("="*60)

# Check credentials
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
anon_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY') or os.getenv('SUPABASE_ANON_KEY')
service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

output.append(f"\nCREDENTIALS CHECK:")
output.append(f"   URL: {url[:50] if url else 'MISSING'}...")
output.append(f"   ANON KEY: {'SET' if anon_key else 'MISSING'}")
output.append(f"   SERVICE KEY: {'SET' if service_key else 'MISSING'}")

key_to_use = service_key or anon_key

if not url or not key_to_use:
    output.append("\nMISSING CREDENTIALS - Cannot proceed")
else:
    output.append(f"\nTESTING CONNECTION:")
    try:
        from supabase import create_client
        sb = create_client(url, key_to_use)
        output.append("   Client created successfully")
        
        output.append("\nCHECKING TABLES:")
        
        tables = ['leads', 'contacts_master', 'brain_logs', 'prospects']
        for table in tables:
            try:
                result = sb.table(table).select('*').limit(5).execute()
                data = result.data if result.data else []
                output.append(f"   {table}: {len(data)} rows returned")
                if data:
                    output.append(f"      Columns: {list(data[0].keys())[:5]}")
            except Exception as e:
                output.append(f"   {table}: ERROR - {str(e)[:80]}")
        
        # Try insert
        output.append("\nINSERT TEST:")
        try:
            test_data = {"company_name": "Diagnostic Test", "email": "diag@test.com", "status": "test"}
            result = sb.table('leads').insert(test_data).execute()
            if result.data:
                output.append(f"   INSERT SUCCESS - ID: {result.data[0].get('id')}")
                sb.table('leads').delete().eq('email', 'diag@test.com').execute()
                output.append("   CLEANUP SUCCESS")
            else:
                output.append("   INSERT returned empty data")
        except Exception as e:
            output.append(f"   INSERT FAILED: {str(e)[:100]}")
            
    except Exception as e:
        output.append(f"   Connection failed: {str(e)}")

output.append("\n" + "="*60)

# Write to file
with open("supabase_results.txt", "w") as f:
    f.write("\n".join(output))

# Also print
for line in output:
    print(line)
