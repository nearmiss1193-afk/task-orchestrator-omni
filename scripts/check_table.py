import os, requests

url = os.environ.get('SUPABASE_URL', 'https://rzcpfwkygdvoshtwxncs.supabase.co')
key = os.environ['SUPABASE_KEY']
headers = {'apikey': key, 'Authorization': 'Bearer ' + key}

r = requests.get(url + '/rest/v1/audit_reports?select=id&limit=1', headers=headers)
print('Status:', r.status_code)
print('Body:', r.text[:300])

if r.status_code == 200:
    print('TABLE EXISTS')
else:
    print('TABLE MISSING - need to create via Supabase dashboard')
