"""Minimal Modal test to diagnose deployment issues"""
import modal

app = modal.App("test-deploy")
image = modal.Image.debian_slim(python_version="3.11").pip_install("fastapi")

@app.function(image=image)
@modal.web_endpoint(method="GET")
def health():
    return {"status": "ok", "test": True}
