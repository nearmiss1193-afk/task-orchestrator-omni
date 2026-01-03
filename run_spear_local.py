import os
import json
import asyncio
import sys
from supabase import create_client
import google.generativeai as genai
from dotenv import load_dotenv

# Import audit logic - assuming modules exist locally
try:
    from modules.sales.site_auditor import SiteAuditor
except ImportError:
    # Fallback if module path is an issue, though it should be fine in root
    sys.path.append(os.getcwd())
    from modules.sales.site_auditor import SiteAuditor

# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

async def run_spear():
    print("🎯 Initiating Operation Spear (Local Override)...")
    
    # Env vars
    SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("[CRITICAL] Supabase Credentials Missing.")
        return

    genai.configure(api_key=GEMINI_KEY)
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Select Targets (Top 30)
    print("[SCAN] Scanning contacts_master for Top 30 High-Probability Targets...")
    try:
        res = supabase.table("contacts_master").select("*").order("created_at", desc=True).limit(30).execute()
        leads = res.data
    except Exception as e:
        print(f"[ERROR] Database Connection Failed: {e}")
        return
    
    if not leads:
        print("[CRITICAL] No leads in database.")
        return

    print(f"[TARGETS] Locked: {len(leads)} Prospects")
    
    output_lines = []
    output_lines.append(f"# Spear Batch Review (Top {len(leads)})\n")
    output_lines.append("**Motto:** Learn, Evolve, and Grow Always\n\n")

    auditor = SiteAuditor()

    for i, lead in enumerate(leads):
        name = lead.get('full_name', 'Founder')
        # Handle schema drift (company_name might be in raw_research)
        company = lead.get('company_name')
        if not company and lead.get('raw_research'):
            company = lead.get('raw_research', {}).get('company_name')
        if not company:
            company = "Company"
            
        url = lead.get('website_url')
        if not url or url == "None":
            print(f"[{i+1}/{len(leads)}] Skipping {name}: No URL")
            continue

        print(f"[{i+1}/{len(leads)}] Processing: {name} ({url})...")
        
        # 2. Intel Gathering
        try:
             # Run sync audit in a separate thread to avoid blocking asyncio loop
            loop = asyncio.get_running_loop()
            audit_res = await loop.run_in_executor(None, auditor.audit_site, url)
        except Exception as e:
            print(f"   [WARN] Audit fail: {e}")
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
            # Dynamic Model Selection / Fallback
            model_name = "models/gemini-2.0-flash"
            try: 
                 model = genai.GenerativeModel(model_name)
                 response = model.generate_content(prompt)
            except:
                 try:
                    model_name = "models/gemini-3-flash-preview"
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                 except:
                    # Last Resort
                    model_name = "models/gemini-2.0-flash-lite" 
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)

            text_cleaned = response.text.replace('```json', '').replace('```', '').strip()
            strategy = json.loads(text_cleaned)
            
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
    
    # Write to file
    with open("SPEAR_BATCH_REVIEW.md", "w", encoding="utf-8") as f:
        f.write(full_dossier)
        
    print("--- DOSSIER GENERATED: SPEAR_BATCH_REVIEW.md ---")

if __name__ == "__main__":
    asyncio.run(run_spear())
