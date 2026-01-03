
import modal
import os

# Define a lightweight image without Playwright/Chromium
# This ensures fast build and fewer failure points for simple HTML serving.
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("fastapi", "python-dotenv", "requests")
    # Surgical Mounts to avoid uploading 30,000+ files from polluted directory
    .add_local_file("modules/__init__.py", remote_path="/root/modules/__init__.py")
    .add_local_file("modules/web/__init__.py", remote_path="/root/modules/web/__init__.py")
    .add_local_file("modules/web/hvac_landing.py", remote_path="/root/modules/web/hvac_landing.py")
    .add_local_file("modules/web/plumber_landing.py", remote_path="/root/modules/web/plumber_landing.py")
    .add_local_file("modules/web/roofer_landing.py", remote_path="/root/modules/web/roofer_landing.py")
    .add_local_file("modules/web/electrician_landing.py", remote_path="/root/modules/web/electrician_landing.py")
    .add_local_file("modules/web/solar_landing.py", remote_path="/root/modules/web/solar_landing.py")
    .add_local_file("modules/web/landscaping_landing.py", remote_path="/root/modules/web/landscaping_landing.py")
    .add_local_file("modules/web/pest_landing.py", remote_path="/root/modules/web/pest_landing.py")
    .add_local_file("modules/web/cleaning_landing.py", remote_path="/root/modules/web/cleaning_landing.py")
    .add_local_file("modules/web/restoration_landing.py", remote_path="/root/modules/web/restoration_landing.py")
    .add_local_file("modules/web/autodetail_landing.py", remote_path="/root/modules/web/autodetail_landing.py")
    .add_local_file("sovereign_config.json", remote_path="/root/sovereign_config.json")

)

app = modal.App("ghl-omni-light")

# Mount Secrets (Safe Defaults)
import dotenv
dotenv.load_dotenv()
dotenv.load_dotenv(".env.local")

def safe_env(key):
    return os.environ.get(key) or ""

VAULT = modal.Secret.from_dict({
    "SUPABASE_URL": safe_env("NEXT_PUBLIC_SUPABASE_URL"),
    "SUPABASE_SERVICE_ROLE_KEY": safe_env("SUPABASE_SERVICE_ROLE_KEY"),
})


@app.function(image=image)
@modal.fastapi_endpoint()
def hello():
    return "Sovereign Light System Online"

# Re-declare the endpoints using the lightweight image
@app.function(image=image)
@modal.fastapi_endpoint()
def hvac_landing():
    # Dynamic Import to avoid top-level dependency issues
    from modules.web.hvac_landing import get_hvac_landing_html
    html = get_hvac_landing_html(
        calendly_url="https://calendar.google.com/calendar", 
        stripe_url="/checkout"
    )
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

@app.function(image=image)
@modal.fastapi_endpoint()
def plumber_landing():
    from modules.web.plumber_landing import get_plumber_landing_html
    html = get_plumber_landing_html()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

@app.function(image=image)
@modal.fastapi_endpoint()
def roofer_landing():
    from modules.web.roofer_landing import get_roofer_landing_html
    html = get_roofer_landing_html()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

@app.function(image=image)
@modal.fastapi_endpoint()
def electrician_landing():
    from modules.web.electrician_landing import get_electrician_landing_html
    html = get_electrician_landing_html()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

@app.function(image=image)
@modal.fastapi_endpoint()
def solar_landing():
    from modules.web.solar_landing import get_solar_landing_html
    html = get_solar_landing_html()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

@app.function(image=image)
@modal.fastapi_endpoint()
def landscaping_landing():
    from modules.web.landscaping_landing import get_landscaping_landing_html
    html = get_landscaping_landing_html()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

@app.function(image=image)
@modal.fastapi_endpoint()
def pest_landing():
    from modules.web.pest_landing import get_pest_landing_html
    html = get_pest_landing_html()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

@app.function(image=image)
@modal.fastapi_endpoint()
def cleaning_landing():
    from modules.web.cleaning_landing import get_cleaning_landing_html
    html = get_cleaning_landing_html()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

@app.function(image=image)
@modal.fastapi_endpoint()
def restoration_landing():
    from modules.web.restoration_landing import get_restoration_landing_html
    html = get_restoration_landing_html()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)

@app.function(image=image)
@modal.fastapi_endpoint()
def autodetail_landing():
    from modules.web.autodetail_landing import get_autodetail_landing_html
    html = get_autodetail_landing_html()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)
