import json
import random

def search_competitors(niche, location):
    # Simulated search for market rivals
    competitors = [
        {"name": "AutoFlow Solutions", "url": "autoflow.ai", "leaks": ["No instant booking", "Cluttered UI"]},
        {"name": "SmallBiz AI Pro", "url": "smallbizai.io", "leaks": ["Missing case studies", "Slow mobile load"]},
        {"name": "Nexus Automation", "url": "nexusauto.com", "leaks": ["Broken footer links", "No lead magnet"]}
    ]
    return competitors

def generate_comparison(my_site, competitor):
    # Analyze why we win
    analysis = {
        "competitor": competitor['name'],
        "url": competitor['url'],
        "leaks": competitor['leaks'],
        "our_advantage": "Autonomous Spartan Responder (Instant SMS) vs their email-only contact form.",
        "estimated_annual_loss": random.randint(50000, 150000)
    }
    return analysis

if __name__ == "__main__":
    competitors = search_competitors("AI Automation", "Local/Global")
    dossiers = [generate_comparison("aiserviceco.com", c) for c in competitors]
    print(json.dumps(dossiers, indent=2))
