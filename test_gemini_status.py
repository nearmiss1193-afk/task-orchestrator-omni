import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('GEMINI_API_KEY')
print(f"Key present: {bool(key)}")

try:
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    print("Generating...")
    response = model.generate_content("Give me 5 random numbers in JSON format.")
    print(f"Response: {response.text}")
    print("✅ Gemini Working")
except Exception as e:
    print(f"❌ Gemini Error: {e}")
