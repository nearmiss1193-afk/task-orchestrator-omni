"""Check what analytics/tracking is on both sites"""
import requests, re

for site in ['https://aiserviceco.com', 'https://lakelandfinds.com']:
    print(f'\n{"="*60}')
    print(f'SITE: {site}')
    print(f'{"="*60}')
    
    r = requests.get(site, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
    html = r.text
    
    # Find Google Analytics IDs
    ga_ids = re.findall(r'(G-[A-Z0-9]+|UA-\d+-\d+|GTM-[A-Z0-9]+)', html)
    if ga_ids:
        print(f'Analytics IDs found: {ga_ids}')
    else:
        print('No Google Analytics/GTM IDs found')
    
    # Find all external script sources
    scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html)
    analytics_scripts = [s for s in scripts if any(k in s.lower() for k in 
        ['analytics', 'gtag', 'gtm', 'facebook', 'pixel', 'hotjar', 'clarity', 'plausible', 'tracking'])]
    
    if analytics_scripts:
        print(f'Analytics scripts:')
        for s in analytics_scripts:
            print(f'  {s}')
    else:
        print('No analytics script tags found')
    
    # Check for inline analytics
    if 'gtag(' in html:
        print('Found: gtag() calls (Google Analytics)')
    if 'fbq(' in html:
        print('Found: fbq() calls (Facebook Pixel)')
    if 'clarity(' in html.lower():
        print('Found: Clarity (Microsoft)')
    if 'analytics' in html.lower():
        # Find context
        idx = html.lower().find('analytics')
        context = html[max(0,idx-50):idx+80]
        print(f'Analytics keyword context: ...{context}...')
    
    # Check meta tags
    metas = re.findall(r'<meta[^>]*(verification|google-site|facebook|analytics)[^>]*>', html, re.IGNORECASE)
    if metas:
        print(f'Verification meta tags: {metas}')

print('\nDone.')
