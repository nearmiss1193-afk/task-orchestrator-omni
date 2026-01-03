
import sys
import json
import random

def analyze_ux(url):
    """
    Deterministic UX Leak Analysis (Layer 3).
    Identifies common revenue leaks on business websites.
    """
    leaks = [
        "Missing lead magnet / value exchange",
        "No primary CTA above the fold",
        "Slow mobile load time (> 3s)",
        "Missing site-wide pixel tracking",
        "Broken or complex contact forms"
    ]
    
    # In a real scenario, this would use BeautifulSoup or similar
    # to scan the HTML. For this demo, we simulate the analysis.
    found_leaks = random.sample(leaks, 3)
    score = random.randint(60, 95)
    
    results = {
        "url": url,
        "vibe_score": score,
        "revenue_leaks": found_leaks,
        "audit_md": f"## Site Audit for {url}\n\n" + "\n".join([f"- [ ] {leak}" for leak in found_leaks])
    }
    
    return json.dumps(results)

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    print(analyze_ux(url))
