import os
from dotenv import load_dotenv
load_dotenv()

print("Checking Supabase...")

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

print(f'URL: {url}')
print(f'KEY: {key[:20] if key else "MISSING"}...')

if url and key:
    from supabase import create_client
    sb = create_client(url, key)
    
    # Check leads table
    try:
        leads = sb.table('leads').select('*').execute()
        total = len(leads.data) if leads.data else 0
        print(f'Total leads: {total}')
        
        if leads.data:
            ready = [l for l in leads.data if l.get('audit_link')]
            print(f'Ready (with audit link): {len(ready)}')
            contacted = [l for l in leads.data if l.get('status') == 'contacted']
            print(f'Already contacted: {len(contacted)}')
            
            print('\nLast 5 leads:')
            for l in leads.data[-5:]:
                print(f"  {l.get('company_name', '?')[:30]} | {l.get('email', 'N/A')} | audit: {'YES' if l.get('audit_link') else 'NO'}")
    except Exception as e:
        print(f'Error: {e}')
else:
    print('Missing credentials!')
