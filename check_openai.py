import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv("OPENAI_API_KEY")
print(f"OPENAI_KEY_EXISTS: {bool(key)}")
if key:
    print(f"Key preview: {key[:5]}...")
