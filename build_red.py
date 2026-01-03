
import base64

# Load Assets
try:
    with open("assets/generated/social.jpg", "rb") as f:
        social_b64 = base64.b64encode(f.read()).decode('utf-8')
    with open("assets/generated/ads.jpg", "rb") as f:
        ads_b64 = base64.b64encode(f.read()).decode('utf-8')
except:
    social_b64 = ""
    ads_b64 = ""

SCRIPT = f'''
import modal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = modal.App("landing-page-red")

# Use minimal image
image = modal.Image.debian_slim().pip_install("fastapi", "uvicorn", "requests")

# Embed Content
SOCIAL_URI = "data:image/jpeg;base64,{social_b64}"
ADS_URI = "data:image/jpeg;base64,{ads_b64}"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Service Co | Automated Growth</title>
    <style>
        :root {{ --bg: #030712; --primary: #3b82f6; --text: #f8fafc; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; }}
        
        .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 20px; }}
        .header {{ text-align: center; margin-bottom: 60px; }}
        h1 {{ 
            font-size: 3.5rem; 
            background: linear-gradient(to right, #60a5fa, #c084fc); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }}
        
        /* CARDS */
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }}
        .card {{
            position: relative;
            border-radius: 16px;
            overflow: hidden;
            aspect-ratio: 16/9;
            border: 1px solid rgba(255,255,255,0.1);
            background: #111;
        }}
        .card img {{
            width: 100%; height: 100%; object-fit: cover;
            animation: kenBurns 15s infinite alternate ease-in-out;
        }}
        @keyframes kenBurns {{ from {{ transform: scale(1.0); }} to {{ transform: scale(1.15); }} }}
        
        .overlay {{
            position: absolute; bottom: 0; left: 0; right: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
            padding: 20px;
        }}
        h3 {{ margin: 0; color: white; font-size: 1.25rem; }}
        p {{ margin: 5px 0 0; color: #cbd5e1; font-size: 0.9rem; }}
        
        .cta-box {{ text-align: center; margin-top: 60px; }}
        .btn {{ 
            display: inline-block; padding: 16px 32px; 
            background: var(--primary); color: white; 
            text-decoration: none; border-radius: 8px; font-weight: 600; 
            font-size: 1.2rem;
        }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>The Growth Engine</h1>
            <p>Automated Systems for HVAC Professionals</p>
        </div>
        
        <div class="grid">
             <!-- Social -->
            <div class="card">
                <img src="{""" + SOCIAL_URI + """}" alt="Social">
                <div class="overlay">
                    <h3>Social Autopilot</h3>
                    <p>On-brand posts generated daily.</p>
                </div>
            </div>
            
            <!-- Ads -->
            <div class="card">
                <img src="{""" + ADS_URI + """}" alt="Ads">
                <div class="overlay">
                    <h3>Ad Intelligence</h3>
                    <p>Lower CPA. Higher Conversion.</p>
                </div>
            </div>
            
            <!-- Missed Call -->
            <div class="card">
                 <div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; background:#0f172a;">
                    <div style="font-size:4rem;">📞</div>
                 </div>
                <div class="overlay">
                    <h3>AI Receptionist</h3>
                    <p>Never miss a lead again.</p>
                </div>
            </div>
        </div>
        
        <div class="cta-box">
            <a href="https://calendly.com/aiserviceco/demo" class="btn">Start Free Trial</a>
        </div>
    </div>
</body>
</html>
"""

@app.function(image=image)
@modal.web_endpoint()
def home():
    return HTMLResponse(content=HTML, status_code=200)
'''

with open("deploy_landing_red.py", "w", encoding="utf-8") as f:
    f.write(SCRIPT)

print("✅ Built deploy_landing_red.py")
