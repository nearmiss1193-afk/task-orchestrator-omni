import os
import modal

app = modal.App("lead-checker")
image = modal.Image.debian_slim().pip_install("supabase")
VAULT = modal.Secret.from_name("sovereign-vault")

@app.function(image=image, secrets=[VAULT])
def find_test_lead():
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)
    
    # Search for "Test" or user-like names
    res = supabase.table("contacts_master").select("*").ilike("first_name", "%Test%").execute()
    if res.data:
        print(f"✅ Found {len(res.data)} test leads:")
        for lead in res.data:
            print(f"ID: {lead['id']} | Name: {lead.get('first_name')} {lead.get('last_name')} | Phone: {lead.get('phone')}")
        return res.data[0]['id']
    
    # Fallback: just get the newest lead
    print("⚠️ No lead with 'Test' found. Getting latest lead...")
    res = supabase.table("contacts_master").select("*").order("created_at", desc=True).limit(1).execute()
    if res.data:
        lead = res.data[0]
        print(f"✅ Latest Lead: ID: {lead['id']} | Name: {lead.get('first_name')} {lead.get('last_name')} | Phone: {lead.get('phone')}")
        return lead['id']
    
    print("❌ No leads found in contacts_master.")
    return None

if __name__ == "__main__":
    with modal.Retrier(max_retries=3):
        find_test_lead.remote()
