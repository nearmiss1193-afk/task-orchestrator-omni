import os
import json
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)

def main():
    print("[PLANNING] Initiating Social Media Operations...")
    
    prompt = """
    MISSION: SOCIAL CONTENT DOMINATION
    TARGET AUDIENCE: HVAC & Service Business Owners
    GOAL: Drive traffic to https://aiserviceco.com/demo
    MOTTO: "Learn, Evolve, and Grow Always" (MUST BE INCLUDED IN EVERY POST)
    
    TASK: Generate a 10-Item Content Plan.
    
    FORMAT:
    1. FB/Insta REEL Script (x3): 15-30s video script. Hook -> Value -> Call to Action.
    2. FB/Insta Static Post (x3): Image concept + Caption.
    3. Twitter Thread (x2): 3-tweet thread.
    4. GMB Update (x2): Local SEO focused update.
    
    OUTPUT JSON:
    {
      "reels": [{"title": "...", "script": "...", "caption": "..."}],
      "static": [{"title": "...", "image_idea": "...", "caption": "..."}],
      "twitter": [{"thread": ["tweet1", "tweet2", "tweet3"]}],
      "gmb": [{"update_text": "..."}]
    }
    """
    
    model = genai.GenerativeModel("gemini-1.5-flash") # Use specific model name
    print("[GENERATING] Synthesizing Content Matrix...")
    
    import time
    from google.api_core import exceptions
    
    def generate_with_retry(model, prompt, retries=5):
        base_delay = 2
        for i in range(retries):
            try:
                return model.generate_content(prompt)
            except exceptions.ResourceExhausted:
                wait = base_delay * (2 ** i)
                print(f"⚠️ Quota Exceeded. Retrying in {wait}s...")
                time.sleep(wait)
            except Exception as e:
                print(f"⚠️ API Error: {e}. Retrying...")
                time.sleep(2)
        raise Exception("Max retries exceeded for Social Generation")

    try:
        response = generate_with_retry(model, prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        plan = json.loads(text)
        
        outfile = "SOCIAL_CONTENT_PLAN.md"
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(f"# 📱 Social Domination Plan (10 Posts)\n")
            f.write("**Motto:** Learn, Evolve, and Grow Always\n\n")
            
            f.write("## 🎥 Reels / TikToks (x3)\n")
            for i, reel in enumerate(plan.get('reels', [])):
                f.write(f"### Reel {i+1}: {reel['title']}\n")
                f.write(f"**Script:**\n> {reel['script']}\n\n")
                f.write(f"**Caption:**\n> {reel['caption']}\n\n")
                f.write("---\n")
                
            f.write("## 🖼️ Static Posts (FB/Insta) (x3)\n")
            for i, post in enumerate(plan.get('static', [])):
                f.write(f"### Post {i+1}: {post['title']}\n")
                f.write(f"**Image Idea:** {post['image_idea']}\n")
                f.write(f"**Caption:**\n> {post['caption']}\n\n")
                f.write("---\n")
                
            f.write("## 🐦 Twitter Threads (x2)\n")
            for i, thread in enumerate(plan.get('twitter', [])):
                f.write(f"### Thread {i+1}:\n")
                for t in thread.get('thread', []):
                    f.write(f"- {t}\n")
                f.write("\n---\n")
                
            f.write("## 📍 Google Business Profile (x2)\n")
            for i, gmb in enumerate(plan.get('gmb', [])):
                f.write(f"### Update {i+1}:\n")
                f.write(f"> {gmb['update_text']}\n\n")
                
        print(f"[SUCCESS] Social Plan Generated: {outfile}")
        
    except Exception as e:
        import traceback
        with open("social_error.log", "w") as f:
            f.write(traceback.format_exc())
        print(f"[ERROR] Generation Failed: See social_error.log")

if __name__ == "__main__":
    main()
