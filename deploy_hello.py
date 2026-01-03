
import modal

image = modal.Image.debian_slim().pip_install("fastapi")
app = modal.App("hello-check")

@app.function(image=image)
@modal.fastapi_endpoint()
def hello():
    return "System Check: ONLINE"
