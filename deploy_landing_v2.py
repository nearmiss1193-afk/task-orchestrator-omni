
import modal

app = modal.App("landing-page-v2")
image = modal.Image.debian_slim().pip_install("fastapi", "requests")

# Mount the 'assets' folder so the browser can serve the generated images
assets_mount = modal.Mount.from_local_dir("assets", remote_path="/assets")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Service Co | Growth Stack</title>
    <style>
        :root { --bg: #030712; --primary: #3b82f6; --glass: rgba(17, 24, 39, 0.7); --text: #f8fafc; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; }
        
        /* THE KEN BURNS EFFECT (CSS ONLY) */
        .video-card {
            position: relative;
            border-radius: 20px;
            overflow: hidden;
            aspect-ratio: 16/9;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .video-card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            animation: kenBurns 10s infinite alternate ease-in-out;
            will-change: transform;
        }
        @keyframes kenBurns {
            from { transform: scale(1.0); }
            to { transform: scale(1.1); }
        }
        
        .overlay {
            position: absolute; bottom: 0; left: 0; right: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.95), transparent);
            padding: 40px 20px 20px;
            z-index: 10;
        }
        
        /* General Layout */
        .container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 40px; }
        h1 { font-size: 3rem; text-align: center; margin-bottom: 60px; background: linear-gradient(to right, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        h3 { margin: 0; color: white; font-size: 1.5rem; }
        p { color: #94a3b8; font-size: 0.95rem; margin-top: 5px; }

        .btn { display: inline-block; padding: 16px 32px; background: var(--primary); color: white; text-decoration: none; border-radius: 12px; font-weight: 600; margin-top: 60px; }
        .center { text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>The Growth Stack</h1>
        
        <div class="grid">
            <!-- Social Autopilot -->
            <div class="video-card">
                <img src="/assets/generated/social_mockup.png" alt="Social Autopilot UI">
                <div class="overlay">
                    <h3>Social Autopilot</h3>
                    <p>We post on-brand content. Daily.</p>
                </div>
            </div>

            <!-- Ad Intelligence -->
            <div class="video-card">
                <img src="/assets/generated/ads_mockup.png" alt="Ads Dashboard UI">
                <div class="overlay">
                    <h3>Ad Intelligence</h3>
                    <p>Leads for $12, not $50.</p>
                </div>
            </div>
            
             <!-- Missed Call (Static Placeholder) -->
            <div class="video-card">
                 <div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; background:#111;">
                    <span style="font-size:3rem;">📞</span>
                 </div>
                <div class="overlay">
                    <h3>AI Receptionist</h3>
                    <p>Recover missed calls instantly.</p>
                </div>
            </div>
        </div>

        <div class="center">
            <a href="https://calendly.com/aiserviceco/demo" class="btn">Get Full Access</a>
        </div>
    </div>
</body>
</html>
"""

@app.function(image=image, mounts=[assets_mount])
@modal.web_endpoint()
def hvac():
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=HTML_TEMPLATE, status_code=200)

# Serve assets
@app.function(image=image, mounts=[assets_mount])
@modal.web_endpoint(method="GET", label="assets")
def serve_asset(request: Request):
    # Manual path parsing or just relying on a specific endpoint
    # Simpler: Just serve specific files based on query or path
    # Modal web_endpoints are distinct.
    # To mimic /assets/..., we might need a separate app or route
    pass

