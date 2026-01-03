
import modal
import os
import sys

# Add current path
sys.path.append("/root")

app = modal.App("constructor-debug")

image = (
    modal.Image.debian_slim()
    .pip_install("requests")
    .add_local_dir(".", remote_path="/root", ignore=["**/node_modules", "**/.next", "**/dist", "**/.git"])
)

@app.function(image=image, secrets=[modal.Secret.from_name("agency-vault")])
def run_architect_check():
    from modules.constructor.workflow_architect import WorkflowArchitect
    
    print("\n--- 🏗️ CONSTRUCTOR AGENT DIAGNOSTIC ---")
    arch = WorkflowArchitect()
    
    # 1. Check Auth
    print(f"Token Present: {bool(arch.token)}")
    print(f"Location ID: {arch.location_id}")
    
    # 2. Scan for Known Assets
    # We look for a common form (or one we know exists)
    forms = ["Roofing Intake", "General Intake", "Lead Form"]
    
    found_any = False
    for name in forms:
        fid = arch.find_form(name)
        if fid:
            print(f"✅ VERIFIED: Found '{name}' with ID: {fid}")
            found_any = True
        else:
            print(f"❌ MISSING: Could not find form '{name}'")
            
    if not found_any:
        print("⚠️ WARNING: Constructor is blind. Check Permissions or Form Names.")
    else:
        print("✅ SYSTEM READY: Constructor can see the environment.")

if __name__ == "__main__":
    # Local run logic if needed, but Modal is better for secrets
    pass
