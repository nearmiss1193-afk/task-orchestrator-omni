import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-1.5-flash')

print("Testing 1.5 Flash...")
try:
    # Test standard generation
    response = model.generate_content("Hello")
    print(f"Standard Gen: {response.text}")
except Exception as e:
    print(f"Standard Error: {e}")

try:
    # Test JSON mode specifically if that was the issue (though standard usually works)
    prompt = "Return JSON: {'test': 1}"
    response = model.generate_content(prompt)
    print(f"JSON Gen: {response.text}")
except Exception as e:
    print(f"JSON Error: {e}")
