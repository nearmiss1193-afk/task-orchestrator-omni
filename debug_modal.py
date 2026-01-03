import modal

image = modal.Image.debian_slim().pip_install("fastapi")
app = modal.App("debug-app", image=image)

@app.function()
@modal.fastapi_endpoint()
def test_endpoint():
    return {"status": "ok"}

@app.local_entrypoint()
def main():
    print("Entrypoint ran.")
