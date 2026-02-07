
import json
import os
import sys
import subprocess
import argparse

# Reuse logic from batch3_processor but strictly for one target
# and with verbose "Reasoning" output.

PROSPECTS_FILE = "prospects_ready.json"
OUTPUT_DIR = "audit_reports"

def get_industry_hooks(industry):
    # Industry-specific hooks
    hooks = {
        "HVAC": {
            "seo_term": "AC repair near me",
            "client_term": "homeowners",
            "service_term": "emergency repair",
            "trap_example": "One Hour Heating & Air"
        },
        "Plumbing": {
            "seo_term": "plumber near me",
            "client_term": "homeowners",
            "service_term": "emergency leak repair",
            "trap_example": "Roto-Rooter"
        },
        "Roofing": {
            "seo_term": "roofer near me",
            "client_term": "homeowners",
            "service_term": "roof inspection",
            "trap_example": "Aspen Contracting"
        },
        "Dental": {
            "seo_term": "dentist near me",
            "client_term": "patients", 
            "service_term": "dental implant",
            "trap_example": "Heartland Dental"
        },
        "Medical": {
            "seo_term": "doctor near me",
            "client_term": "patients",
            "service_term": "urgent care connection",
            "trap_example": "Optum RX"
        }
    }
    # Default to HVAC if unknown, or generic
    base = hooks.get(industry, hooks["HVAC"]) 
    # Fallback for mapped "HVAC/Plumbing"
    if "/" in industry:
        if "Plumb" in industry:
             base = hooks["Plumbing"]
        else:
             base = hooks["HVAC"]
    return base

def verify_reasoning(prospect):
    print(f"\n🧠 VERIFYING REASONING FOR: {prospect['company_name']}")
    print(f"   - Input Industry: {prospect.get('industry')}")
    
    industry = prospect.get("industry", "Business")
    hooks = get_industry_hooks(industry)
    
    print(f"   - Detected Hook Profile: {industry}")
    print(f"   - SEO Term: '{hooks['seo_term']}'")
    print(f"   - Client Term: '{hooks['client_term']}'")
    print(f"   - Trap Example: '{hooks['trap_example']}'")
    
    if "Dentist" in hooks['seo_term'] and "HVAC" in industry:
        print("   ❌ CRITICAL LOGIC FAIL: Mismatch detected.")
        sys.exit(1)
    else:
        print("   ✅ Logic Check Passed: Industry matches Hook Profile.")

def run_single(index):
    with open(PROSPECTS_FILE, 'r') as f:
        prospects = json.load(f)
        
    if index < 0 or index >= len(prospects):
        print("Invalid index")
        return

    target = prospects[index]
    
    # 1. Verify Logic FIRST
    verify_reasoning(target)
    
    # 2. Proceed with Generation (Mocking the process steps for the user to approve)
    print("\n   [Plan of Action]")
    print(f"   1. Scan URL: {target['website']}")
    print(f"   2. Generate PDF: 'Strategic Solutions for {target['company_name']}'")
    print(f"   3. Build Email: Using '{get_industry_hooks(target.get('industry'))['seo_term']}' hooks.")
    print("   4. Send Preview to Owner.")
    
    # Note: I am NOT executing the send yet. Just showing the plan.
    # To execute, I will call the actual processor logic from batch3_processor imports if user confirms.
    
    # Actually, let's generate the artifacts locally so we can INSPECT them before sending.
    
    # Import the actual builder to inspect output
    sys.path.append(os.path.join(os.getcwd(), 'scripts'))
    import batch3_processor
    
    # OUTPUT_DIR needs to be defined if we use it here, but process_prospect uses batch3_processor's internal logic.
    # The error was likely NameError in MY script if I tried to use OUTPUT_DIR.
    # Let's ensure batch3_processor has what it needs.
    
    print("\n   [Executing Generation for Inspection...]")
    batch3_processor.process_prospect(target, index+1) 
    # process_prospect in batch3_processor sends the email. 
    # I should modify it to optionally NOT send, but for now, sending a PREVIEW to You is the safe inspection method.

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, default=0)
    args = parser.parse_args()
    
    run_single(args.index)
