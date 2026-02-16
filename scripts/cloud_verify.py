import modal
import json
import os

# Get the app
try:
    f_ingest = modal.Function.from_name("ghl-omni-automation", "trigger_manus_ingest")
    f_strike = modal.Function.from_name("ghl-omni-automation", "trigger_cinematic_strike")
    f_verify = modal.Function.from_name("ghl-omni-automation", "verify_strike_results")

    # 1. Ingest
    print("📥 Ingesting leads...")
    leads = json.load(open("manus_leads.json"))
    ingest_res = f_ingest.remote(leads_json=json.dumps(leads))
    print(f"✅ Ingested {ingest_res} leads.")

    # 2. Strike
    print("🚀 Triggering Cinematic Strike...")
    f_strike.remote()

    # 3. Verify
    print("📈 Verifying assets...")
    verified = f_verify.remote()
    print(f"✅ FINAL VERIFICATION: {verified}/19 leads confirmed with strike assets.")

except Exception as e:
    print(f"❌ Cloud Execution Failed: {e}")
