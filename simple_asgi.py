"""Simple ASGI test"""
import modal
from fastapi import FastAPI

app = modal.App("simple-asgi-test")
image = modal.Image.debian_slim().pip_install("fastapi")

@app.function(image=image)
@modal.asgi_app()
def api():
    web_app = FastAPI()
    @web_app.get("/")
    def root():
        return {"hello": "world"}
    @web_app.get("/health")
    def health():
        return {"status": "ok"}
    return web_app
