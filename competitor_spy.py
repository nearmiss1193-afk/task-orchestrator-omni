"""
COMPETITOR SPY
==============
Monitor competitor pricing, ads, and reviews.
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv('GROK_API_KEY')
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"


def analyze_competitor(competitor: dict) -> dict:
    """Analyze a competitor using Grok"""
    
    prompt = f"""Analyze this competitor for a home services business:

Company: {competitor.get('name')}
Website: {competitor.get('website', 'Unknown')}
Industry: {competitor.get('industry', 'HVAC')}
Location: {competitor.get('location', 'Florida')}

Research and provide:
1. Estimated pricing tier (low/mid/premium)
2. Key differentiators/USPs
3. Weaknesses to exploit
4. Their likely target customer
5. Recommended counter-strategy

Return JSON:
{{
    "pricing_tier": "low/mid/premium",
    "usps": ["list", "of", "differentiators"],
    "weaknesses": ["list", "of", "weaknesses"],
    "target_customer": "description",
    "counter_strategy": "recommendation",
    "threat_level": 1-10
}}"""

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "grok-3-mini",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            analysis = json.loads(response.json()['choices'][0]['message']['content'])
            return {**competitor, "analysis": analysis, "analyzed_at": datetime.now().isoformat()}
    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
    
    return {**competitor, "analysis": {"error": "Failed to analyze"}}


def monitor_competitors(competitors: list) -> list:
    """Monitor multiple competitors"""
    results = []
    high_threats = []
    
    for comp in competitors:
        print(f"[SPY] Analyzing {comp.get('name')}...")
        result = analyze_competitor(comp)
        results.append(result)
        
        if result.get('analysis', {}).get('threat_level', 0) >= 7:
            high_threats.append(result)
    
    # Alert on high threats
    if high_threats:
        alert_high_threats(high_threats)
    
    return results


def alert_high_threats(threats: list):
    """Send SMS alert for high-threat competitors"""
    names = [t.get('name') for t in threats]
    message = f"🚨 Competitor Alert: {', '.join(names)} rated HIGH threat. Check spy report."
    
    try:
        requests.post(GHL_SMS_WEBHOOK, json={
            "phone": os.getenv('TEST_PHONE', '+13529368152'),
            "message": message
        })
        print(f"[ALERT] High threat notification sent")
    except:
        pass


def save_intel(results: list, filename: str = "competitor_intel.json"):
    """Save competitor intelligence"""
    with open(filename, "w") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "competitors": results
        }, f, indent=2)
    print(f"[SAVED] Intel to {filename}")


if __name__ == "__main__":
    test_competitors = [
        {"name": "Tampa Air Experts", "website": "tampaairexperts.com", "industry": "HVAC", "location": "Tampa, FL"},
        {"name": "Florida Cooling Pros", "website": "floridacoolingpros.com", "industry": "HVAC", "location": "Tampa, FL"},
    ]
    
    results = monitor_competitors(test_competitors)
    save_intel(results)
