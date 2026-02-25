import os
import json
import time
from dotenv import load_dotenv
import psycopg2
import google.generativeai as genai

load_dotenv('C:/Users/nearm/.gemini/antigravity/scratch/empire-unified/.env')

# Setup Gemini
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_KEY:
    print("❌ GEMINI_API_KEY not found")
    exit(1)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Setup Supabase Postgres
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("❌ DATABASE_URL not found")
    exit(1)

def generate_market_analysis(keyword, industry, location):
    prompt = f"""
    You are an expert local SEO copywriter and market analyst for B2B home services.
    Write a highly unique, engaging 2-paragraph "Market Analysis" about the need for an "{keyword}" explicitly for the "{industry}" industry in "{location}".
    
    Rules:
    1. The first paragraph must mention specific, realistic geographical or climate details about {location} that affect the {industry} industry (e.g., intense summer humidity in Florida, specific storm seasons, high tourist populations, rapid local construction, etc.).
    2. The second paragraph must explain why missing phone calls in this specific market is a competitive disadvantage, and how a 24/7 AI booking agent is the ultimate operational upgrade for a {industry} business here.
    3. Keep it professional, conversion-focused, and extremely relevant to the local area.
    4. Do NOT use generic filler. Make the local connection feel authentic and well-researched.
    5. Output ONLY the two paragraphs of text. No intro, no outro, no markdown formatting.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def run_enrichment():
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Fetch all records
    cur.execute("SELECT slug, keyword, industry, location, content_data FROM seo_landing_pages;")
    records = cur.fetchall()
    
    print(f"🔍 Found {len(records)} SEO landing pages.")
    
    enriched_count = 0
    
    for row in records:
        slug, keyword, industry, location, content_data = row
        
        # Parse JSON
        if content_data is None:
            content_data = {}
        elif isinstance(content_data, str):
            content_data = json.loads(content_data)
            
        # Check if already enriched
        if "market_analysis" in content_data and content_data["market_analysis"]:
            continue
            
        print(f"🤖 Generating unique market analysis for: {industry} in {location}...")
        
        analysis_text = generate_market_analysis(keyword, industry, location)
        
        if analysis_text:
            content_data["market_analysis"] = analysis_text
            
            # Update DB
            cur.execute("""
                UPDATE seo_landing_pages
                SET content_data = %s::jsonb
                WHERE slug = %s
            """, (json.dumps(content_data), slug))
            conn.commit()
            
            enriched_count += 1
            print(f"✅ Enriched {slug} ({enriched_count} completed)")
            
            # Prevent rate limiting (Gemini free tier / standard tier limits)
            # Sleep a bit to be safe
            time.sleep(2)
        else:
            print(f"⚠️ Skipping {slug} due to AI generation error.")
            time.sleep(5) # Backoff on error
            
    cur.close()
    conn.close()
    
    print(f"🎉 Enrichment Loop Complete! Enhanced {enriched_count} pages.")

if __name__ == "__main__":
    # Just run 1 to test it first
    print("Testing connection...")
    test_res = generate_market_analysis("AI Phone Agent", "HVAC", "Tampa, FL")
    print("Test Output:\n", test_res)
    print("\nStarting full loop...")
    run_enrichment()
