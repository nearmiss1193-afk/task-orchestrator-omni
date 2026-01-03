
import modal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
try:
    from assets_data import FRAME_B64
except ImportError:
    FRAME_B64 = ""

app = modal.App("hvac-vsl")
image = modal.Image.debian_slim().pip_install("fastapi", "uvicorn")

@app.function(image=image)
@modal.web_endpoint()
def home():
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
            .video-container {{ max-width: 900px; margin: 40px auto; border: 2px solid #333; border-radius: 24px; overflow: hidden; background: #111; position: relative; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }}
            .video-container img {{ width: 100%; display: block; }}
            .play-overlay {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.3); }}
            .play-btn {{ width: 80px; height: 80px; background: rgba(255,255,255,0.9); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; color: #000; cursor: pointer; transition: transform 0.2s; }}
            .play-btn:hover {{ transform: scale(1.1); }}
            .cta-box {{ margin: 60px 0; padding: 0 20px; }}
            .btn {{ display: inline-block; padding: 20px 40px; background: #4facfe; color: #fff; text-decoration: none; border-radius: 12px; font-weight: 800; font-size: 1.25rem; box-shadow: 0 10px 20px rgba(79, 172, 254, 0.3); }}
        </style>
    </head>
    <body>
        <div class='header'>
            <h1>Intelligence Imperative</h1>
            <p class='subtitle'>The 2025 HVAC Dominance Strategy</p>
        </div>
        
        <div class='video-container'>
            <img src='data:image/png;base64,{FRAME_B64}' alt='Project VSL'>
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
