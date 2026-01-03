
import modal
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = modal.App("bones")

image = modal.Image.debian_slim().pip_install("fastapi")

@app.function(image=image)
@modal.asgi_app(label="main")
def web():
    web_app = FastAPI()

    @web_app.get("/")
    def root():
        return HTMLResponse("<h1>BARE BONES: ONLINE</h1>")

    return web_app
