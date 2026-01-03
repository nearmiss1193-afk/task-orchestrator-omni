
# Sovereign Deployment Patch for playwright in Modal (v40.0)
import modal
from modal import Image

# Custom image with system dependencies installed
# Added add_local_dir to ensure deploy.py is accessible
image = (
    Image.debian_slim()
    # Added all deploy.py dependencies to ensure valid import
    .pip_install("playwright==1.40.0", "modal-client", "python-dotenv", "requests", "supabase", "fastapi", "stripe", "google-generativeai>=0.5.0", "dnspython")
    .run_commands(
        "apt-get update",
        "apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libxkbcommon0 libgtk-3-0 libdrm2 libgbm1 libasound2 git",
        "playwright install chromium"
    )
    .add_local_dir(".", remote_path="/root", ignore=[
        "**/node_modules", 
        "**/.next", 
        "**/dist",
        "**/.git",
        "**/.ghl_browser_data",
        "**/backups",
        "**/*_b64.txt",
        "**/*.log",
        "**/__pycache__"
    ])
)

app = modal.App("imperium_deploy_patch")

@app.function(image=image, timeout=600)
def main():
    print("✅ Patched Playwright environment ready.")
    print("Launching sovereign deploy pipeline …")
    # Call your real deploy sequence here
    import subprocess
    # We try to import deploy first to check dependencies
    try:
        subprocess.run(["python", "-c", "import deploy; print('Deploy Module Importable')"], check=True)
        # Verify Playwright
        subprocess.run(["playwright", "--version"], check=True)
    except Exception as e:
        print(f"Environment Verification Failed: {e}")
        raise e

if __name__ == "__main__":
    # main.local() # Deprecated in some versions, using standard run
    with app.run():
        main.remote()
