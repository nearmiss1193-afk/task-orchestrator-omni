
import modal

app = modal.App("landing-page-v7")

# Explicitly installing standard dependencies
image = (
    modal.Image.debian_slim()
    # Install standard to get uvicorn[standard], email-validator, etc.
    .pip_install("fastapi[standard]")
)

HTML = """
<!DOCTYPE html>
<html><body><h1>TradeFlow AI Online</h1><p>System operational.</p></body></html>
"""

@app.function(image=image)
@modal.web_endpoint()
def home():
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=HTML)
