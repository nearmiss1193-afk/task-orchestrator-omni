import modal

# Shared Constants
VAULT = modal.Secret.from_dict({
    "SUPABASE_URL": "https://rzcpfwkygdvoshtwxncs.supabase.co",
    "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
    "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
    "SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo",
    "DATABASE_URL": "postgresql://postgres:Inez11752990@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres"
})
APP_NAME = "ghl-omni-automation"

# Unified Image Configuration
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg")
    .pip_install(
        "fastapi[standard]",
        "requests",
        "supabase",
        "python-dotenv",
        "openai",
        "google-generativeai",
        "reportlab",
        "playwright",
        "psycopg2-binary",
        "beautifulsoup4",
        "lxml",
        "pytz"
    )
    .run_commands("playwright install chromium")
    .add_local_dir("core", "/root/core")
    .add_local_dir("workers", "/root/workers")
    .add_local_dir("handlers", "/root/handlers")
    .add_local_dir("modules", "/root/modules")
    .add_local_dir("scripts", "/root/scripts")
)

from core.apps import engine_app as app
