"""Get PageSpeed Insights detail for aiserviceco.com mobile"""
import requests, json

r = requests.get(
    'https://www.googleapis.com/pagespeedonline/v5/runPagespeed',
    params={
        'url': 'https://www.aiserviceco.com/',
        'strategy': 'mobile',
        'category': 'PERFORMANCE'
    },
    timeout=60
)
d = r.json()
lr = d.get('lighthouseResult', {})

# Overall score
score = lr.get('categories', {}).get('performance', {}).get('score', 0)
print(f"PERFORMANCE SCORE: {int(score*100)}")

# Key metrics
audits = lr.get('audits', {})
metrics = ['first-contentful-paint', 'largest-contentful-paint', 'total-blocking-time', 
           'cumulative-layout-shift', 'speed-index', 'interactive']
print("\nKEY METRICS:")
for m in metrics:
    a = audits.get(m, {})
    print(f"  {a.get('title', m)}: {a.get('displayValue', '?')} (score: {a.get('score', '?')})")

# Opportunities (things with savings)
print("\nOPPORTUNITIES:")
for k, v in audits.items():
    details = v.get('details', {})
    if details.get('type') == 'opportunity' and details.get('overallSavingsMs', 0) > 0:
        savings = details.get('overallSavingsMs', 0)
        print(f"  {v.get('title')}: {v.get('displayValue', '')} (saves {savings}ms)")
        # Show items
        for item in (details.get('items', [])[:3]):
            url = item.get('url', '')
            if url:
                print(f"    - {url[:80]}... ({item.get('wastedMs', 0)}ms)")

# Diagnostics
print("\nDIAGNOSTICS:")
for k, v in audits.items():
    details = v.get('details', {})
    if details.get('type') == 'table' and v.get('score', 1) is not None and v.get('score', 1) < 0.5:
        print(f"  ❌ {v.get('title')}: {v.get('displayValue', '')}")
