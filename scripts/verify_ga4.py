"""Deep check - what gtag code IS on aiserviceco.com?"""
import requests, re

r = requests.get('https://aiserviceco.com', timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
html = r.text

# Find all G- measurement IDs
g_ids = re.findall(r'G-[A-Z0-9]+', html)
print(f'Measurement IDs found: {g_ids}')

# Find gtag script src
scripts = re.findall(r'googletagmanager\.com/gtag/js\?id=([^\'"&]+)', html)
print(f'GTM script IDs: {scripts}')

# Find gtag config calls
configs = re.findall(r"gtag\('config',\s*'([^']+)'\)", html)
print(f'gtag config calls: {configs}')

# Check if our new tag is there
print(f'\nG-XZK2Z9K3TW present: {"G-XZK2Z9K3TW" in html}')

# Where does the site come from?
print(f'\nResponse headers:')
for h in ['server', 'x-vercel-id', 'x-powered-by', 'via', 'x-modal']:
    if h in r.headers:
        print(f'  {h}: {r.headers[h]}')

# Check lakeland finds too
print('\n---\n')
r2 = requests.get('https://lakelandfinds.com', timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
print(f'Lakeland Finds headers:')
for h in ['server', 'x-vercel-id', 'x-powered-by', 'via']:
    if h in r2.headers:
        print(f'  {h}: {r2.headers[h]}')
print(f'Has gtag: {"gtag" in r2.text}')
print(f'Has G-SZWJKJNSZ9: {"G-SZWJKJNSZ9" in r2.text}')

# Next.js Script with afterInteractive renders client-side, not in SSR HTML
# Check if it's in the __NEXT_DATA__ or page JS bundles
if '__NEXT_DATA__' in r2.text:
    print('Next.js SSR detected - Script tags with afterInteractive load client-side, not in HTML source')
