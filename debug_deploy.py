
import modal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = modal.App("debug-landing")

image = modal.Image.debian_slim().pip_install("fastapi", "uvicorn")

@app.function(image=image)
@modal.web_endpoint()
def root():
    return HTMLResponse("<h1>DEBUG: Root Endpoint is Live</h1>")

@app.function(image=image)
@modal.web_endpoint(label="custom-label")
def labeled():
    return HTMLResponse("<h1>DEBUG: Custom Label is Live</h1>")
