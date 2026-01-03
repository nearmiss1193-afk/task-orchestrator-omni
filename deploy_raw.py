
import modal

app = modal.App("landing-page-raw")

@app.function()
@modal.web_endpoint()
def home():
    return "RAW OK"
