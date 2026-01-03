
import modal
import deploy
import os
import json
import requests
import re

app = deploy.app

@app.local_entrypoint()
def main(url: str = "freeplumberai.com"):
    print(f"🚀 INITIATING TARGETED CAMPAIGN: {url}")
    result = adhoc_predator_resilient.remote(url)
    
    with open("ad_hoc_result.txt", "w", encoding="utf-8") as f:
        f.write(result)
    print("Done (Resilient Mode).")

@app.function(image=deploy.image, secrets=[deploy.VAULT])
def adhoc_predator_resilient(url: str):
    import google.generativeai as genai
    
    if not url.startswith("http"):
        url = f"https://{url}"
        
    log = []
    content = ""
    
    # 1. SCRAPE
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        content = res.text
        log.append(f" -> Scrape Status: {res.status_code}")
    except Exception as e:
        return f"❌ Scrape Failed: {e}"

    # 2. ANALYSIS ATTEMPT (Gemini)
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Analyze this website: {url}
        HTML: {content[:10000]}
        
        MISSION:
        1. Identify 3 Operational Inefficiencies.
        2. Write a 'Spartan' Outreach Hook (concise, lowercase).
        3. Rate Automation Potential (0-100).
        
        Return JSON: {{"inefficiencies": [], "hook": "", "score": 0}}
        """
        
        res = model.generate_content(prompt)
        text = res.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text)
        
        return format_output(url, data, "Gemini AI")
        
    except Exception as e:
        log.append(f"⚠️ AI Failed ({e}). Engaging Survival Mode (Heuristics).")
        
        # 3. SURVIVAL MODE (Heuristics)
        inefficiencies = []
        
        # Check for Chat
        if not re.search(r'tidio|intercom|drift|chat|widget', content, re.I):
            inefficiencies.append("No Intelligent Chat Widget detected (Leaking 24/7 leads).")
        
        # Check for Phone vs Form
        if "tel:" in content and "form" not in content:
            inefficiencies.append("Phone-Only CTA (High Friction for millennials).")
        
        # Check for Email
        if "mailto:" in content:
            inefficiencies.append("Manual Email Links detected (Slow response time).")
            
        if not inefficiencies:
            inefficiencies.append("Generic Contact Form (Likely <5% conversion).")
            
        hook = f"hey, saw {url.split('//')[1]}. noticed you're missing a 24/7 AI capture. you're likely paying for traffic that bounces. i built a fix."
        
        data = {
            "inefficiencies": inefficiencies,
            "hook": hook,
            "score": 65
        }
        return format_output(url, data, "Heuristic Engine")

def format_output(url, data, source):
    output = [
        f"🎯 CAMPAIGN RESULTS for {url} (Source: {source}):",
        f"------------------------------------------------",
        f"Inefficiencies: {json.dumps(data.get('inefficiencies'), indent=2)}",
        f"------------------------------------------------",
        f"🪝 HOOK: {data.get('hook')}",
        f"------------------------------------------------",
        f"Score: {data.get('score')}/100"
    ]
    return "\n".join(output)
