
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    models = []
    for m in genai.list_models():
        models.append({"name": m.name, "methods": m.supported_generation_methods})
    
    with open("gemini_models.json", "w") as f:
        json.dump(models, f, indent=2)
    print("✅ Models saved to gemini_models.json")
except Exception as e:
    print(f"❌ Error: {e}")
