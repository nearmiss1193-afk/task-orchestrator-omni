
import os

def build_final_script():
    # Read the base64 content
    try:
        with open("clean_b64.txt", "r") as f:
            b64_data = f.read().strip()
    except FileNotFoundError:
        print("Error: clean_b64.txt not found!")
        return

    # Create the python script content with the string embedded
    script_content = f"""
import modal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = modal.App("landing-page-production")

image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "uvicorn")
)

# HARDCODED ASSET - NO FILE IO REQUIRED
LOGO_B64 = "{b64_data}"

@app.function(image=image)
@modal.web_endpoint(method="GET")
def web():
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
            .header {{ padding: 60px 20px 20px; }}
            h1 {{ font-size: clamp(2rem, 8vw, 3.5rem); background: linear-gradient(45deg, #00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; margin: 0; }}
            p.subtitle {{ font-size: 1.2rem; color: #888; margin-top: 10px; }}
            
            .hero-image {{ max-width: 900px; margin: 40px auto; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }}
            .hero-image img {{ width: 100%; display: block; }}
            
            .cta-box {{ margin: 60px 0; padding: 0 20px; }}
            .btn {{ display: inline-block; padding: 20px 40px; background: #4facfe; color: #fff; text-decoration: none; border-radius: 12px; font-weight: 800; font-size: 1.25rem; box-shadow: 0 10px 20px rgba(79, 172, 254, 0.3); transition: transform 0.2s; }}
            .btn:hover {{ transform: translateY(-2px); }}
            
            .footer {{ margin-top: 80px; color: #444; font-size: 0.9rem; padding-bottom: 40px; }}
        </style>
    </head>
    <body>
        <div class='header'>
            <h1>Intelligence Imperative</h1>
            <p class='subtitle'>The 2025 HVAC Dominance Strategy</p>
        </div>
        
        <div class="hero-image">
            <img src="data:image/png;base64,{{LOGO_B64}}" alt="Growth Engine">
        </div>

        <div class='cta-box'>
            <a href='https://calendly.com/aiserviceco/demo' class='btn'>Secure Your Territory</a>
        </div>
        
        <div class="footer">
            &copy; 2024 AI Service Co. All Rights Reserved.
        </div>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content)
"""
    
    with open("deploy_final_sso.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("Successfully built deploy_final_sso.py with embedded assets.")

if __name__ == "__main__":
    build_final_script()
