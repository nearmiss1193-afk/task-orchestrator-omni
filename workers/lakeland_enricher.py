import os
import modal
import json
import time
from datetime import datetime, timezone
from core.apps import engine_app as app
from core.image_config import image, VAULT

@app.function(
    image=image,
    secrets=[VAULT],
    timeout=600
)
def run_enrichment_loop(limit: int = 15):
    """
    Worker to enrich Lakeland businesses using Gemini AI.
    Generates 'vibe summaries' and semantic insights for the directory.
    """
    import psycopg2
    import google.generativeai as genai
    
    # 1. Setup Connections
    neon_url = os.environ.get("NEON_DATABASE_URL")
    gemini_key = os.environ.get("GEMINI_API_KEY") # Ensure this is in Modal Secrets
    
    if not neon_url:
        print("❌ Error: NEON_DATABASE_URL missing")
        return {"error": "Missing NEON_DATABASE_URL"}
        
    if not gemini_key:
        # Fallback to checking Vault if not direct env
        print("⚠️ Warning: GEMINI_API_KEY missing from env, checking fallback...")
        # (Usually secret handles this)
    
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"❌ Gemini Config Error: {e}")
        return {"error": f"Gemini failure: {e}"}

    try:
        conn = psycopg2.connect(neon_url)
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ Neon Connection Error: {e}")
        return {"error": f"Neon failure: {e}"}

    # 2. Identify Targets (Businesses needing enrichment)
    # We prioritize those with websites as we can 'reason' over the URL/Context
    cur.execute("""
        SELECT id, name, category, website_url, address
        FROM businesses 
        WHERE vibe_summary IS NULL 
        LIMIT %s
    """, (limit,))
    
    targets = cur.fetchall()
    
    if not targets:
        print("🛌 No businesses identified for enrichment. Sleep.")
        cur.close()
        conn.close()
        return {"enriched": 0}

    print(f"🧠 AI ENRICHER: Starting batch of {len(targets)}")
    
    enriched_count = 0
    for biz_id, name, cat, website, address in targets:
        try:
            # Construct a high-leverage prompt
            prompt = f"""
            Task: Generate a 'Vibe Summary' for a local business in Lakeland, Florida.
            Business: {name}
            Category: {cat or 'Local Business'}
            Address: {address or 'Lakeland, FL'}
            Website: {website or 'Not provided'}

            Output Requirements:
            - Exactly 2 sentences.
            - Tone: Premium, helpful, and localized.
            - Goal: Help a user decide if they should visit.
            - Avoid: Generic buzzwords (e.g., 'exceptional service'). Use specific vibe details.
            """

            response = model.generate_content(prompt)
            vibe_summary = response.text.strip()
            
            if vibe_summary:
                # Update the database
                cur.execute("""
                    UPDATE businesses 
                    SET vibe_summary = %s, 
                        updated_at = NOW() 
                    WHERE id = %s
                """, (vibe_summary, biz_id))
                conn.commit()
                enriched_count += 1
                print(f"  ✅ Enriched: {name}")
            
            # Rate limit buffer for Gemini Free/Flash
            time.sleep(1) 
            
        except Exception as e:
            conn.rollback()
            print(f"  ❌ Failed to enrich {name}: {e}")

    # 3. Cleanup
    cur.close()
    conn.close()
    
    print(f"🚀 Enrichment Complete. Records Updated: {enriched_count}")
    return {"enriched": enriched_count}

if __name__ == "__main__":
    # Local Test Execution
    with app.run():
        run_enrichment_loop.remote(limit=3)
