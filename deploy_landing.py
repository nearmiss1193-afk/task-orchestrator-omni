
import modal

app = modal.App("landing-page-host")

image = modal.Image.debian_slim().pip_install("fastapi", "requests")

@app.function(image=image)
@modal.web_endpoint()
def hvac():
    try:
        # Try importing from the co-located file
        import hvac_landing_root
        html = hvac_landing_root.get_hvac_landing_html(
            calendly_url="https://calendly.com/aiserviceco/demo",
            stripe_url="https://stripe.com/payment-placeholder"
        )
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html, status_code=200)
    except Exception as e:
        return {"error": str(e), "trace": "Import failed. Files in dir: " + str(os.listdir('.'))}

import os
