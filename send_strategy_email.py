
import os
import resend

try:
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v.strip('"').strip("'")
except: pass

resend.api_key = os.environ.get("RESEND_API_KEY")

# Read the Strategy File
try:
    with open(r"C:\Users\nearm\.gemini\antigravity\brain\1dc252aa-5552-4742-8763-0a1bcda94400\EMPIRE_EXPANSION_STRATEGY.md", "r") as f:
        strategy_content = f.read()
    
    # Convert Markdown to basic HTML (simple replace for newlines)
    html_content = f"<h1>Empire Expansion Strategy</h1><pre>{strategy_content}</pre>"

    params = {
        "from": "alert@aiserviceco.com",
        "to": ["nearmiss1193@gmail.com"],
        "subject": "📄 Empire Expansion Strategy (7-Day Plan)",
        "html": html_content
    }

    email = resend.Emails.send(params)
    print(f"✅ Strategy Email Sent! ID: {email.get('id')}")

except Exception as e:
    print(f"❌ Failed: {e}")
