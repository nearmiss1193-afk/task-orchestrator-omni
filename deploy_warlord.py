import modal
import os
import shutil

# Define Image
image = (
    modal.Image.debian_slim()
    .pip_install(
        "streamlit",
        "pandas",
        "plotly",
        "supabase",
        "python-dotenv",
        "httpx"
    )
    .add_local_dir(
        "c:/Users/nearm/.gemini/antigravity/scratch/empire-unified",
        remote_path="/root/empire",
        ignore=["**/node_modules", "**/.git", "**/backups"]
    )
)

app = modal.App("warlord-map")

# Shared Secret Reference
import dotenv
dotenv.load_dotenv()
VAULT = modal.Secret.from_dict({
    "SUPABASE_URL": os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL"),
    "SUPABASE_SERVICE_ROLE_KEY": os.environ.get("SUPABASE_SERVICE_ROLE_KEY"),
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
    "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY"),
    "GHL_LOCATION_ID": os.environ.get("GHL_LOCATION_ID"),
})

@app.function(
    image=image,
    secrets=[VAULT],
    allow_concurrent_inputs=100,
)
@modal.web_server(port=8501)
def warlord_live():
    # Streamlit needs to run in the background
    # We change dir to where the code is
    os.chdir("/root/empire")
    
    # Run Streamlit
    cmd = "streamlit run warlord_map.py --server.port 8501 --server.enableCORS=false --server.enableXsrfProtection=false"
    os.system(cmd)

if __name__ == "__main__":
    # Local Test or Deploy
    print("To deploy: python -m modal deploy deploy_warlord.py")
