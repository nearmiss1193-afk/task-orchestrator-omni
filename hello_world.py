
import modal

app = modal.App("hello-world")

@app.function()
@modal.web_endpoint(label="main")
def hello():
    return "<h1>Hello from Modal</h1>"
