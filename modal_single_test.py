"""Single function test"""
import modal
from datetime import datetime

app = modal.App("orch-single")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "fastapi")

@app.function(image=image, timeout=30)
@modal.web_endpoint(method="GET")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
