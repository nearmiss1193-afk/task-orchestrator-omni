
import modal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = modal.App("min-dash")

image = modal.Image.debian_slim().pip_install("fastapi", "uvicorn", "google-generativeai", "supabase")

@app.function(image=image)
@modal.asgi_app(label="main")
def web():
    web_app = FastAPI()

    @web_app.get("/")
    def root():
        return HTMLResponse("<h1>EMPIRE COMMAND CENTER: ONLINE</h1><p>Minimal Deployment Successful.</p>")

    return web_app
