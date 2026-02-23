import os
from dotenv import dotenv_values
import google.generativeai as genai

env_vars = dotenv_values('.env')
keys = set()
for k, v in env_vars.items():
    if 'gemini' in k.lower() or 'google' in k.lower():
        if v and v.startswith('AIza'):
            keys.add(v)

print(f"Found {len(keys)} unique potential Gemini/Google API keys.")

valid_key = None
for idx, key in enumerate(keys):
    try:
        print(f"Testing key {idx+1}...")
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        res = model.generate_content('Say YES').text
        print(f"✅ Key {idx+1} works! Response: {res.strip()}")
        valid_key = key
        break
    except Exception as e:
        print(f"❌ Key {idx+1} failed: {e}")

if valid_key:
    # Inject the valid key to GitHub
    import subprocess
    repo = "nearmiss1193-afk/empire-unified-backup"
    print("Injecting valid Gemini key to GitHub...")
    subprocess.run(["gh", "secret", "set", "GEMINI_API_KEY", "-b", valid_key, "-R", repo])
    print("Done!")
else:
    print("All keys failed.")
