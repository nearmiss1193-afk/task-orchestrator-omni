"""Minimal Modal test app to verify platform works"""
import modal
from fastapi import FastAPI

image = modal.Image.debian_slim(python_version="3.11").pip_install("fastapi[standard]")
app = modal.App("empire-test-minimal", image=image)

@app.function()
@modal.asgi_app()
def minimal_api():
    api = FastAPI()
    
    @api.get("/health")
    def health():
        return {"status": "ok", "app": "minimal-test"}
    
    @api.get("/test")
    def test():
        return {"message": "Modal works!"}
    
    return api
