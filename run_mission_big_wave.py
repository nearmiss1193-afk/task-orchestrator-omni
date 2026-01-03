
import modal
import deploy
import requests
import json
import time

app = deploy.app

# --- STANDALONE LOGIC (Bypassing broken DB) ---

@app.local_entrypoint()
def main():
    print("🌊 OPERATION BIG WAVE: INIT (Simulation Mode)")
    
    target_url = "https://bigwaverestoration.com" # Verified from snippets
    
    print(f"🦖 Releasing Predator on {target_url}...")
    
    # Run the research remotely
    res = perform_research.remote(target_url)
    
    print("\n--- 🦖 PREDATOR REPORT ---")
    print(json.dumps(res, indent=2))
    print("--------------------------\n")
    
    hook = res.get('hook', 'No hook generated')
    
    print("📝 DRAFT EMAIL GENERATED:")
    print(f"Subject: question re: big wave restoration")
    print(f"Body:\nhey big wave team,\n\n{hook}\n\nmind if i send over a 30s video showing exactly how to fix it?")
    
    # Save Report
    with open("output/mission_report.json", "w") as f:
        json.dump({"hook": hook, "research": res}, f, indent=2)

@app.function(image=deploy.image, secrets=[deploy.VAULT])
def perform_research(url):
    print(f"🕵️‍♂️ Scanning {url}...")
    import json
    
    # 1. PREDATOR: SCRAPE (Simulated/Lightweight for speed or Real?)
    # Let's do a REAL scan if possible, or just analyze the URL text if playwright fails?
    # We will use the 'requests' + 'text' scraping for speed/robustness in this one-off
    
    scraped_text = "Homepage: 24/7 Water Damage Restoration. Locally Owned. Emergency Service. Call Now. Insurance Claims Specialists."
    # Try to fetch real home page?
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            # Simple text extraction
            from html.parser import HTMLParser
            class MLStripper(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.reset()
                    self.strict = False
                    self.convert_charrefs= True
                    self.text = []
                def handle_data(self, d):
                    self.text.append(d)
                def get_data(self):
                    return "".join(self.text)
            
            s = MLStripper()
            s.feed(res.text)
            scraped_text = s.get_data()[:10000] # Limit
    except:
        print("Falling back to simulated scrape text.")
        
    print(f"✅ Scrape Complete. Length: {len(scraped_text)}")
    
    # 2. GEMINI ANALYSIS
    import google.generativeai as genai
    import os
    
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-pro') # Fallback to Pro
    except:
        model = deploy.get_gemini_model() # Default
    
    prompt = f"""
    Analyze this service business based on their digital footprint.
    
    URL: {url}
    SCRAPED CONTENT: {scraped_text}
    
    MISSION: PREDATOR DISCOVERY
    1. Identify 3 specific 'Operational Inefficiencies'.
    2. Write a 1-sentence 'Spartan' outreach hook. 
       Tone: Casual, Lowercase, 'Peer-to-Peer', Insightful.
       Bad: "I can save you money."
       Good: "noticed your contact form doesn't auto-reply, you're likely losing 30% of traffic there."
    
    Format as JSON: {{"inefficiencies": [], "hook": "", "automation_score": 0}}
    """
    
    try:
        response = model.generate_content(prompt)
        raw = response.text.replace('```json', '').replace('```', '').strip()
        analysis = json.loads(raw)
        return analysis
    except Exception as e:
        return {"error": str(e), "hook": "saw your site, noticed a quick fix for the intake process."}
