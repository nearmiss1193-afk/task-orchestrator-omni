
import modal
from fastapi.responses import HTMLResponse

app = modal.App("landing-page-final")

# 1. Image Definition (Explicit FastAPI)
image = modal.Image.debian_slim().pip_install("fastapi", "uvicorn", "requests")

# 2. HTML Content (V6 TradeFlow Design)
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TradeFlow AI | Stop Losing Jobs</title>
    <style>
        :root { --bg: #030712; --primary: #3b82f6; --text: #f8fafc; --surface: #1e293b; --border: #334155; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; line-height: 1.5; }
        .container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
        .header { text-align: center; margin-bottom: 60px; padding-top: 40px; }
        h1 { font-size: 3.5rem; margin-bottom: 10px; background: linear-gradient(to right, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
        .lead { font-size: 1.25rem; color: #94a3b8; margin-bottom: 40px; }
        .calc-box { background: var(--surface); padding: 40px; border-radius: 20px; border: 1px solid var(--border); max-width: 700px; margin: 0 auto 80px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }
        .calc-input { width: 100%; padding: 12px; background: #0f172a; border: 1px solid var(--border); color: white; border-radius: 8px; font-size: 16px; margin-top: 8px; box-sizing: border-box; }
        .result-box { text-align: center; background: #0f172a; padding: 20px; border-radius: 12px; margin-top: 20px; border: 1px solid rgba(239,68,68,0.3); }
        .btn { display: inline-block; padding: 18px 40px; background: var(--primary); color: white; text-decoration: none; border-radius: 12px; font-weight: 700; font-size: 1.2rem; margin-top: 20px;}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="font-weight:800; color:white; margin-bottom:20px; font-size:1.2rem;">⚡ TradeFlow AI</div>
            <h1>Stop Losing Jobs.</h1>
            <p class="lead">He answers instantly. You send to voicemail. <br>He gets the $15k install. You get nothing.</p>
            <a href="https://calendly.com/aiserviceco/demo" class="btn">Get My (863) AI Number</a>
        </div>
        
        <div class="calc-box">
            <h3 style="text-align: center; margin-top: 0; color: #fff; font-size:1.5rem;">💸 Calculate Your Lost Revenue</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div><label style="font-size: 14px; color: #94a3b8;">Missed Calls / Week</label><input type="number" id="calls" value="8" class="calc-input"></div>
                <div><label style="font-size: 14px; color: #94a3b8;">Avg. Job Value ($)</label><input type="number" id="val" value="450" class="calc-input"></div>
            </div>
            <div class="result-box">
                <p style="margin: 0; font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">You are burning:</p>
                <h2 id="result" style="margin: 5px 0; color: #ef4444; font-size: 3rem; font-weight: 800;">$144,000 / yr</h2>
            </div>
            <script>
                const inputs = document.querySelectorAll('input');
                function calc() {
                    const calls = document.getElementById('calls').value;
                    const v = document.getElementById('val').value;
                    const loss = calls * 0.7 * v * 52;
                    document.getElementById('result').innerText = "$" + loss.toLocaleString() + " / yr";
                }
                inputs.forEach(e => e.addEventListener('input', calc));
                calc();
            </script>
        </div>
    </div>
</body>
</html>
"""

# 3. Web Endpoint (Explicit Label for URL Consistency)
@app.function(image=image)
@modal.web_endpoint(label="home")
def home():
    return HTMLResponse(content=HTML, status_code=200)
