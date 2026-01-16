"""
Modal Audit Report Server - Serves static HTML audit reports
Endpoint: https://nearmiss1193-afk--audit-reports-serve.modal.run?f=<filename>
"""
import modal
import os

app = modal.App("audit-reports")

# Create image with FastAPI (required for web endpoints)
image = modal.Image.debian_slim(python_version="3.11").pip_install("fastapi")

# Local audit directory
AUDITS_DIR = os.path.join(os.path.dirname(__file__), "public", "audits")

@app.function(image=image)
@modal.web_endpoint(method="GET")
def serve(f: str = "index.html"):
    """Serve audit report by filename - usage: ?f=company-name-id.html"""
    from fastapi.responses import HTMLResponse, Response
    import urllib.request
    import os
    
    # Read from GitHub raw (since local files aren't available in Modal)
    # For now, return a simple redirect to the local file or generate on-the-fly
    
    # Check if we have the file bundled
    local_path = f"/tmp/audits/{f}"
    
    if os.path.exists(local_path):
        with open(local_path, "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    
    # Generate a simple report on-the-fly as fallback
    company = f.replace("-", " ").replace(".html", "").title()
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketing Audit: {company}</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #0f172a; color: #f1f5f9; padding: 40px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #3b82f6; }}
        .stat {{ font-size: 48px; color: #ef4444; font-weight: bold; }}
        .cta {{ background: #3b82f6; color: white; padding: 16px 32px; border-radius: 8px; text-decoration: none; display: inline-block; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Marketing Audit: {company}</h1>
        <p>Generated for your business</p>
        <div class="stat">$144,000</div>
        <p>Estimated revenue opportunity per year</p>
        <a href="tel:+18633373705" class="cta">Call (863) 337-3705</a>
    </div>
</body>
</html>'''
    
    return HTMLResponse(content=html)

@app.function(image=image)
@modal.web_endpoint(method="GET")
def list_reports():
    """List available audit reports"""
    return {{
        "service": "audit-reports",
        "status": "active",
        "usage": "GET /serve?f=company-name.html",
        "base_url": "https://nearmiss1193-afk--audit-reports-serve.modal.run"
    }}

@app.local_entrypoint()
def main():
    print("Modal Audit Reports Server")
    print("Deploy with: modal deploy modal_audit_reports.py")
    print("Access at: https://nearmiss1193-afk--audit-reports-serve.modal.run?f=<filename>")
