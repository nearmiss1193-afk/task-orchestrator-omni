
import os
import time
import requests
import json
import pg8000.native
import urllib.parse
import ssl
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

# --- DATABASE CONNECTION ---
def get_db_connection():
    if not DATABASE_URL: return None
    try:
        result = urllib.parse.urlparse(DATABASE_URL)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        con = pg8000.native.Connection(
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432,
            database=result.path[1:],
            ssl_context=ssl_context
        )
        return con
    except Exception as e:
        print(f"DB Error: {e}")
        return None

def analyze_sentiment():
    print("🔍 Scanning Call Logs for Negative Sentiment...")
    con = get_db_connection()
    if not con:
        print("⚠️ No DB Connection. Using Mock Data.")
        return ["Customer complained about waiting 3 days for service.", "Client upset about 'hidden fees' from competitor."]

    try:
        # Fetch last 20 transcripts
        rows = con.run("SELECT transcript FROM interactions WHERE type='VAPI_CALL' ORDER BY created_at DESC LIMIT 20")
        transcripts = [r[0] for r in rows]
        con.close()
        return transcripts if transcripts else ["No calls yet. Mock: Client hates voicemail."]
    except Exception as e:
        print(f"Query Error: {e}")
        return ["Mock: Client hates voicemail."]

def generate_ad_copy(pain_points):
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY missing.")
        return

    prompt = f"""
    You are a Master Direct Response copywriter.
    
    INPUT DATA (Recent Technician Complaints):
    {json.dumps(pain_points)}

    TASK:
    Write 3 Facebook Ad Headlines and 1 Primary Text based on these specific complaints.
    Agitate the pain point found in the logs.
    
    FORMAT:
    Headline 1: ...
    Headline 2: ...
    Headline 3: ...
    Primary Text: ...
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        generated_text = result['candidates'][0]['content']['parts'][0]['text']
        
        print("\n✨ OPTIMIZED AD COPY GENERATED ✨")
        print("====================================")
        print(generated_text)
        print("====================================")
        return generated_text

    except Exception as e:
        print(f"AI Generation Error: {e}")

if __name__ == "__main__":
    pain_points = analyze_sentiment()
    generate_ad_copy(pain_points)
