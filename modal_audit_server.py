"""
Deploy Audit Reports to Modal as static file hosting
Creates an endpoint at https://nearmiss1193-afk--audit-server-serve.modal.run/[filename]
"""
import modal
import os

# Create app with static file serving
app = modal.App("audit-server")

# Mount the public/audits directory
audits_mount = modal.Mount.from_local_dir(
    os.path.join(os.path.dirname(__file__), "public", "audits"),
    remote_path="/audits"
)

image = modal.Image.debian_slim(python_version="3.11")

@app.function(image=image, mounts=[audits_mount])
@modal.web_endpoint(method="GET")
def serve(filename: str = "index.html"):
    """Serve audit report files"""
    from fastapi.responses import HTMLResponse, Response
    
    filepath = f"/audits/{filename}"
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return Response(
            content=f"Audit report not found: {filename}",
            status_code=404,
            media_type="text/plain"
        )

@app.function(image=image, mounts=[audits_mount])
@modal.web_endpoint(method="GET")
def list_audits():
    """List available audit reports"""
    import os
    files = os.listdir("/audits")
    html_files = [f for f in files if f.endswith('.html')]
    return {
        "count": len(html_files),
        "audits": html_files[:20],
        "base_url": "https://nearmiss1193-afk--audit-server-serve.modal.run"
    }

@app.local_entrypoint()
def main():
    print("Deploying audit server to Modal...")
    print("Files will be available at:")
    print("  https://nearmiss1193-afk--audit-server-serve.modal.run?filename=<name>.html")
