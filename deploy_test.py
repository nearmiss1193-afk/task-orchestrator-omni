
import modal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = modal.App("hvac-vsl-simple")
image = modal.Image.debian_slim().pip_install("fastapi", "uvicorn")

HTML = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Landing Page Test</h1><p>If you see this, Modal is working.</p></body>
</html>
"""

@app.function(image=image)
@modal.web_endpoint()
def home():
    return HTMLResponse(content=HTML)
