
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Key found: {api_key[:5]}...")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    print("Sending request...")
    response = model.generate_content("Hello, are you ready to sell HVAC services?")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
