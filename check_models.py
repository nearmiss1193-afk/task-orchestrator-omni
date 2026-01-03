
import os
import google.generativeai as genai
from dotenv import load_dotenv
import sys

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("No API Key found")
    exit()

genai.configure(api_key=api_key)

print("Listing models...")
with open("models.txt", "w", encoding="utf-8") as f:
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model: {m.name}")
                f.write(f"{m.name}\n")
    except Exception as e:
        print(f"Error listing models: {e}")
        f.write(f"Error: {e}\n")
