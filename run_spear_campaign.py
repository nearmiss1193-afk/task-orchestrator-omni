import os
import json
import asyncio
import sys
import modal
from supabase import create_client
import google.generativeai as genai
from modules.sales.site_auditor import SiteAuditor
from dotenv import load_dotenv

# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# --- MODAL CONFIG ---
image = modal.Image.debian_slim().pip_install(
    "supabase", 
    "google-generativeai", 
    "python-dotenv", 
    "playwright", 
    "requests"
).run_commands("playwright install-deps", "playwright install chromium").add_local_dir(".", remote_path="/root", ignore=[
    "**/node_modules", 
    "**/.next", 
    "**/dist",
    "**/.git",
    "**/.ghl_browser_data",
    "**/backups",
])

app = modal.App("spear-campaign-runner")

# Secrets - Replicated from deploy.py to match local .env injection
VAULT = modal.Secret.from_dict({
    "SUPABASE_URL": os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL"),
    "SUPABASE_SERVICE_ROLE_KEY": os.environ.get("SUPABASE_SERVICE_ROLE_KEY"),
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
})

# --- CONFIG (Loaded from Vault in Cloud) ---
@app.function(image=image, secrets=[VAULT], timeout=600)
async def run_spear():
    print("🎯 Initiating Operation Spear (Cloud Execution)...")
    from modules.sales.site_auditor import SiteAuditor # Lazy Load to fix Import Error

    # Env vars are injected by VAULT
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

    genai.configure(api_key=GEMINI_KEY)
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Select Targets (Top 30)
    print("[SCAN] Scanning contacts_master for Top 30 High-Probability Targets...")
    res = supabase.table("contacts_master").select("*").order("created_at", desc=True).limit(30).execute()
    
    if not res.data:
        print("[CRITICAL] No leads in database.")
        return

    leads = res.data
    print(f"[TARGETS] Locked: {len(leads)} Prospects")
    
    review_file = "SPEAR_BATCH_REVIEW.md" # Note: This writes to container, need to print or return
    
    # Initialize Report (In Memory for Cloud Return)
    output_lines = []
    output_lines.append(f"# Spear Batch Review (Top {len(leads)})\n")
    output_lines.append("**Motto:** Learn, Evolve, and Grow Always\n\n")

    auditor = SiteAuditor()

    for i, lead in enumerate(leads):
        name = lead.get('full_name', 'Founder')
        company = lead.get('company_name', 'Company')
        url = lead.get('website_url')
        print(f"[{i+1}/{len(leads)}] Processing: {name} ({url})...")
        
        # 2. Intel Gathering
        try:
             # Direct call since we are in async function
            audit_res = auditor.audit_site(url)
        except Exception as e:
            audit_res = {"mobile_friendly": False, "chat_widget": False, "load_speed": "Unknown"}

        # 3. Strategy Generation (LLM)
        prompt = f"""
        MISSION: HYPER-PERSONALIZED SPEAR
        TARGET: {name} ({company})
        URL: {url}
        AUDIT FINDINGS: {json.dumps(audit_res)}
        
        TASK: Generate Campaign Assets & Strategy.
        1. EMAIL 1 (Pattern Interrupt):
           - Rule 1: MUST start body with "Learn, Evolve, and Grow Always".
           - Rule 2: MUST include "Book a Call: https://calendly.com/aiserviceco/demo".
           - Tone: Helpful, Peer-to-Peer.
        2. SMS 1 (Nudge):
           - Rule: MUST end with "Learn, Evolve, and Grow Always".
        3. OUTPUT JSON: {{ "email_subject": "...", "email_body": "...", "sms_body": "..." }}
        """
        
        try:
            model = genai.GenerativeModel("gemini-pro") # Switch to Stable Pro
            response = model.generate_content(prompt)
            strategy = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            
            output_lines.append(f"## Target {i+1}: {name} | {company}\n")
            output_lines.append(f"**URL:** {url}\n")
            output_lines.append(f"### 📧 Email Draft\n")
            output_lines.append(f"**Subject:** `{strategy.get('email_subject')}`\n")
            output_lines.append(f"**Body:**\n> {strategy.get('email_body')}\n\n")
            output_lines.append(f"### 📱 SMS Draft\n")
            output_lines.append(f"**Body:**\n> {strategy.get('sms_body')}\n")
            output_lines.append("---\n\n")
                
        except Exception as e:
            print(f"[ERROR] Generating for {name}: {e}")
            output_lines.append(f"## Target {i+1}: {name} - FAILED ({e})\n\n")

    full_dossier = "".join(output_lines)
    print("--- DOSSIER START ---")
    print(full_dossier)
    print("--- DOSSIER END ---")
    return full_dossier

if __name__ == "__main__":
    # Local entry point triggering remote function
    print("🚀 Triggering Cloud Job...")
    asyncio.run(run_spear.remote())
