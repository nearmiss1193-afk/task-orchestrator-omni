"""Get both Performance AND SEO details from PageSpeed API"""
import requests, json

for category in ['PERFORMANCE', 'SEO']:
    print(f"\n{'='*60}")
    print(f"  {category}")
    print(f"{'='*60}")
    
    r = requests.get(
        'https://www.googleapis.com/pagespeedonline/v5/runPagespeed',
        params={
            'url': 'https://www.aiserviceco.com/',
            'strategy': 'mobile',
            'category': category
        },
        timeout=90
    )
    d = r.json()
    lr = d.get('lighthouseResult', {})
    
    # Score
    score = lr.get('categories', {}).get(category.lower(), {}).get('score', 0)
    print(f"\nSCORE: {int(score*100)}")
    
    # Audits
    audits = lr.get('audits', {})
    
    if category == 'PERFORMANCE':
        # Key metrics
        for m in ['first-contentful-paint', 'largest-contentful-paint', 'total-blocking-time', 
                   'cumulative-layout-shift', 'speed-index', 'interactive']:
            a = audits.get(m, {})
            print(f"  {a.get('title', m)}: {a.get('displayValue', '?')} (score: {a.get('score', '?')})")
        
        # Opportunities
        print("\nOPPORTUNITIES:")
        for k, v in audits.items():
            details = v.get('details', {})
            savings = details.get('overallSavingsMs', 0)
            if details.get('type') == 'opportunity' and savings > 0:
                print(f"  {v.get('title')}: {v.get('displayValue', '')} (saves {savings}ms)")
                for item in (details.get('items', [])[:3]):
                    url = item.get('url', '')
                    if url: print(f"    - {url[:80]}... ({item.get('wastedMs', 0)}ms)")
    
    elif category == 'SEO':
        # All failed audits
        print("\nFAILING SEO AUDITS:")
        for k, v in audits.items():
            s = v.get('score')
            if s is not None and s < 1:
                print(f"  ❌ {v.get('title')}: score={s}")
                desc = v.get('description', '')[:150]
                if desc: print(f"     {desc}")
                # Show details
                details = v.get('details', {})
                for item in (details.get('items', [])[:3]):
                    print(f"     -> {json.dumps(item)[:150]}")
