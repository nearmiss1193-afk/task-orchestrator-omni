import modal

image = modal.Image.debian_slim().pip_install("fastapi")
app = modal.App("simple-deploy-label")

@app.function(image=image)
@modal.fastapi_endpoint(label="test")
def root():
    return {"status": "ok"}
