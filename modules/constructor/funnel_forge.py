
import os

class FunnelForge:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def generate_landing_page(self, niche, offer, link_url):
        print(f"🏗️ Forging Landing Page for {niche}...")
        
        copy_bank = {
            "Plumbers": {"h": "Stop Leaking Revenue.", "p": "Every missed call is a flooded basement."},
            "Lawyers": {"h": "Silence is Expensive.", "p": "A missed call is a missed retainer."},
            "Med Spas": {"h": "Full Calendar. Zero Effort.", "p": "Don't let clients book elsewhere."},
            "Roofers": {"h": "Catch Every Storm Lead.", "p": "When it rains, it pours calls."},
            "Real Estate": {"h": "Speed to Lead Wins.", "p": "Zillow gives the lead away if you are slow."}
        }
        
        d = copy_bank.get(niche, {"h": f"Grow Your {niche} Business", "p": "Missed calls are bad."})

        return f"""
<html>
<head><title>{niche} Offer</title></head>
<body>
<h1>{d['h']}</h1>
<p>{d['p']}</p>
<a href="{link_url}">Claim {offer}</a>
</body>
</html>
"""
