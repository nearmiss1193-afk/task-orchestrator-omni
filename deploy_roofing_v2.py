
import modal
from fastapi import HTMLResponse

app = modal.App("empire-roofing-v2")

image = modal.Image.debian_slim().pip_install("fastapi", "uvicorn")

@app.function(image=image)
@modal.web_endpoint(method="GET")
def entry():
    return HTMLResponse("<h1>Roofing App V2 - Verification</h1>")
