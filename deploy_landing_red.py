
import modal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = modal.App("landing-page-red")

# Read the local frame and encode for the image build
try:
    with open("clean_b64.txt", "r") as f:
        b64_content = f.read().strip()
except FileNotFoundError:
    # Fallback/Placeholder if file missing during local test, though it should exist
    b64_content = ""

image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "uvicorn")
)

@app.function(image=image)
@modal.web_endpoint(method="GET")
def home():
    b64 = b64_content # Inlined during build because b64_content is in scope
    
    html_content = f'''
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>2025 AI Planning | Intelligence Imperative</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;800&display=swap" rel='stylesheet'>
        <style>
            body {{ font-family: 'Inter', sans-serif; background: #000; color: #fff; margin: 0; padding: 0; text-align: center; overflow-x: hidden; }}
            .header {{ padding: 60px 20px; }}
            h1 {{ font-size: clamp(2rem, 8vw, 3.5rem); background: linear-gradient(45deg, #00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; margin: 0; }}
            p.subtitle {{ font-size: 1.2rem; color: #888; margin-top: 10px; }}
            .video-container {{ max-width: 900px; margin: 40px auto; border: 2px solid #333; border-radius: 24px; overflow: hidden; background: #111; position: relative; box-shadow: 0 20px 50px rgba(0,0,0,0.5); cursor: pointer; }}
            .video-container img {{ width: 100%; display: block; }}
            .play-overlay {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.3); }}
            .play-btn {{ width: 80px; height: 80px; background: rgba(255,255,255,0.9); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; color: #000; transition: transform 0.2s; }}
            .video-container:hover .play-btn {{ transform: scale(1.1); background: #fff; }}
            .cta-box {{ margin: 60px 0; padding: 0 20px; }}
            .btn {{ display: inline-block; padding: 20px 40px; background: #4facfe; color: #fff; text-decoration: none; border-radius: 12px; font-weight: 800; font-size: 1.25rem; box-shadow: 0 10px 20px rgba(79, 172, 254, 0.3); transition: transform 0.2s; }}
            .btn:hover {{ transform: translateY(-2px); }}
        </style>
    </head>
    <body>
        <div class='header'>
            <h1>Intelligence Imperative</h1>
            <p class='subtitle'>The 2025 HVAC Dominance Strategy</p>
        </div>
        
        <div class='video-container' onclick="window.location.href='https://calendly.com/aiserviceco/demo'">
            <img src='data:image/png;base64,{b64}' alt='Project VSL'>
            <div class='play-overlay'>
                <div class='play-btn'>▶</div>
            </div>
        </div>

        <div class='cta-box'>
            <a href='https://calendly.com/aiserviceco/demo' class='btn'>Secure Your Territory</a>
        </div>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content)
