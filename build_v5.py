
import base64

# Load Assets (Compressed JPEGs)
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

app = modal.App("landing-page-v5")
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
    <title>TradeFlow AI | Stop Losing Jobs</title>
    <style>
        :root {{ --bg: #030712; --primary: #3b82f6; --text: #f8fafc; --surface: #1e293b; --border: #334155; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; line-height: 1.5; }}
        
        .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 20px; }}
        .header {{ text-align: center; margin-bottom: 60px; padding-top: 40px; }}
        h1 {{ 
            font-size: 3.5rem; margin-bottom: 10px;
            background: linear-gradient(to right, #60a5fa, #c084fc); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: -0.03em;
        }}
        .lead {{ font-size: 1.25rem; color: #94a3b8; margin-bottom: 40px; }}
        
        /* TRUST BADGES */
        .trust-row {{ display: flex; justify-content: center; gap: 30px; margin-bottom: 40px; opacity: 0.5; filter: grayscale(100%); }}
        .trust-badge {{ font-weight: 700; font-size: 1.1rem; color: #fff; display: flex; align-items: center; gap: 8px; }}
        
        /* CALCULATOR WIDGET */
        .calc-box {{
            background: var(--surface); padding: 40px; border-radius: 20px; border: 1px solid var(--border);
            max-width: 700px; margin: 0 auto 80px; box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }}
        .calc-input {{ 
            width: 100%; padding: 12px; background: #0f172a; border: 1px solid var(--border); 
            color: white; border-radius: 8px; font-size: 16px; margin-top: 8px; box-sizing: border-box;
        }}
        .result-box {{ text-align: center; background: #0f172a; padding: 20px; border-radius: 12px; margin-top: 20px; border: 1px solid rgba(239,68,68,0.3); }}
        
        /* CARDS */
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }}
        .card {{
            position: relative; border-radius: 16px; overflow: hidden; aspect-ratio: 16/9;
            border: 1px solid rgba(255,255,255,0.1); background: #111;
        }}
        .card img {{
            width: 100%; height: 100%; object-fit: cover;
            animation: kenBurns 15s infinite alternate ease-in-out;
        }}
        @keyframes kenBurns {{ from {{ transform: scale(1.0); }} to {{ transform: scale(1.15); }} }}
        
        .overlay {{
            position: absolute; bottom: 0; left: 0; right: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.95), transparent);
            padding: 20px;
        }}
        h3 {{ margin: 0; color: white; font-size: 1.25rem; }}
        p {{ margin: 5px 0 0; color: #cbd5e1; font-size: 0.9rem; }}
        
        .btn {{ 
            display: inline-block; padding: 18px 40px; 
            background: var(--primary); color: white; 
            text-decoration: none; border-radius: 12px; font-weight: 700; 
            font-size: 1.2rem; transition: transform 0.2s;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
        }}
        .btn:hover {{ transform: translateY(-2px); }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="font-weight:800; color:white; margin-bottom:20px; font-size:1.2rem; display:flex; align-items:center; justify-content:center; gap:10px;">
                ⚡ TradeFlow AI
            </div>
            <h1>Stop Losing Jobs.</h1>
            <p class="lead">He answers instantly. You send to voicemail. <br>He gets the $15k install. You get nothing.</p>
            
            <div class="trust-row">
                <span class="trust-badge">ServiceTitan</span>
                <span class="trust-badge">Jobber</span>
                <span class="trust-badge">Housecall Pro</span>
                <span class="trust-badge">Google Maps</span>
            </div>
            
            <a href="https://calendly.com/aiserviceco/demo" class="btn">Get My (863) AI Number</a>
        </div>
        
        <!-- REVENUE CALCULATOR -->
        <div class="calc-box">
            <h3 style="text-align: center; margin-top: 0; color: #fff; font-size:1.5rem;">💸 Calculate Your Lost Revenue</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div>
                    <label style="font-size: 14px; color: #94a3b8;">Missed Calls / Week</label>
                    <input type="number" id="calls" value="8" class="calc-input">
                </div>
                <div>
                    <label style="font-size: 14px; color: #94a3b8;">Avg. Job Value ($)</label>
                    <input type="number" id="val" value="450" class="calc-input">
                </div>
            </div>
            <div class="result-box">
                <p style="margin: 0; font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">You are burning:</p>
                <h2 id="result" style="margin: 5px 0; color: #ef4444; font-size: 3rem; font-weight: 800;">$144,000 / yr</h2>
            </div>
            <script>
                const inputs = document.querySelectorAll('input');
                function calc() {{
                    const calls = document.getElementById('calls').value;
                    const v = document.getElementById('val').value;
                    const loss = calls * 0.7 * v * 52;
                    document.getElementById('result').innerText = "$" + loss.toLocaleString() + " / yr";
                }}
                inputs.forEach(e => e.addEventListener('input', calc));
                calc();
            </script>
        </div>
        
        <div class="grid">
             <!-- Social -->
            <div class="card">
                <img src="{""" + SOCIAL_URI + """}" alt="Social">
                <div class="overlay">
                    <h3>Social Autopilot</h3>
                    <p>Daily posts generated by your Brand DNA.</p>
                </div>
            </div>
            
            <!-- Ads -->
            <div class="card">
                <img src="{""" + ADS_URI + """}" alt="Ads">
                <div class="overlay">
                    <h3>Ad Management</h3>
                    <p>Leads for $20, not $100.</p>
                </div>
            </div>
            
            <!-- Missed Call -->
            <div class="card">
                 <div style="width:100%; height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#020617; text-align:center;">
                    <div style="font-size:3rem; margin-bottom:10px;">😫</div>
                    <div style="color:#ef4444; font-weight:bold;">MISSED CALL</div>
                    <div style="color:#64748b; font-size:0.8rem;">Potential Loss: $500</div>
                 </div>
                <div class="overlay">
                    <h3>The Problem</h3>
                    <p>He just lost $500. Don't be him.</p>
                </div>
            </div>
        </div>
        
        <div style="text-align:center; margin-top:80px; color:#64748b;">
            <p>&copy; 2025 TradeFlow AI. A Subsidiary of World Unities.</p>
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

with open("deploy_landing_v5.py", "w", encoding="utf-8") as f:
    f.write(SCRIPT)

print("✅ Built deploy_landing_v5.py (TradeFlow AI Edition)")
