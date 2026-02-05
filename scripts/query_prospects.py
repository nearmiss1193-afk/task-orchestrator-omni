"""
Query prospects from contacts_master for email outreach.
Get 10 prospects with website URLs to run PageSpeed tests on.

// turbo-all
"""
import os
from dotenv import load_dotenv

# Load env
env_path = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.env.local"
load_dotenv(env_path)

from supabase import create_client

def get_prospects_for_outreach(limit: int = 10):
    """Get prospects with websites that need PageSpeed analysis"""
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        print(f"   URL: {'set' if url else 'MISSING'}")
        print(f"   KEY: {'set' if key else 'MISSING'}")
        return []
    
    client = create_client(url, key)
    
    # Query contacts with website URLs that haven't been outreached yet
    result = client.table("contacts_master") \
        .select("id, full_name, first_name, last_name, email, phone, company_name, website_url, status, industry, city") \
        .not_.is_("website_url", "null") \
        .not_.eq("website_url", "") \
        .in_("status", ["new", "research_done"]) \
        .limit(limit) \
        .execute()
    
    prospects = result.data
    
    print(f"\n📊 Found {len(prospects)} prospects with websites")
    print("=" * 70)
    
    for i, p in enumerate(prospects, 1):
        print(f"\n{i}. {p.get('company_name', 'Unknown')} ({p.get('full_name', 'Unknown')})")
        print(f"   📧 Email: {p.get('email', 'N/A')}")
        print(f"   🌐 Website: {p.get('website_url', 'N/A')}")
        print(f"   📍 City: {p.get('city', 'N/A')}")
        print(f"   🏢 Industry: {p.get('industry', 'N/A')}")
        print(f"   📊 Status: {p.get('status', 'N/A')}")
    
    return prospects


if __name__ == "__main__":
    print("=" * 70)
    print("PROSPECT QUERY - Email Outreach Candidates")
    print("=" * 70)
    
    prospects = get_prospects_for_outreach(10)
    
    if prospects:
        print(f"\n✅ {len(prospects)} prospects ready for PageSpeed testing")
    else:
        print("\n❌ No prospects found with website URLs")
