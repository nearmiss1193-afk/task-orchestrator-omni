import json
import os
from datetime import datetime, timezone
from modules.database.supabase_client import get_supabase

def draft_social_multiplier_posts(lead_id: str = None):
    """
    Identifies successful audits and drafts high-leverage social posts.
    If lead_id is provided, only drafts for that lead.
    """
    supabase = get_supabase()
    if not supabase:
        print("❌ Supabase connection failed")
        return
    
    if lead_id:
        res = supabase.table("contacts_master").select("*").eq("id", lead_id).execute()
    else:
        # Find 'research_done' leads with video_teaser_url or rich audits
        res = supabase.table("contacts_master").select("*").eq("status", "research_done").limit(5).execute()
    
    leads = res.data
    
    if not leads:
        if not lead_id: print("📭 No recent audit wins found to multiply.")
        return
    
    drafted = 0
    for lead in leads:
        try:
            # Check if already drafted (only if running bulk)
            if not lead_id:
                existing = supabase.table("social_drafts").select("id").eq("lead_id", lead['id']).execute()
                if existing.data:
                    continue
            
            raw = json.loads(lead.get("raw_research") or "{}")
            company = lead.get('company_name') or lead.get('full_name') or "Unknown"
            
            print(f"🎬 Drafting Multiplier for {company}...")
            
            # Platform Variants (OMNIPRESENCE TOGGLED ON)
            platforms = ["linkedin", "x", "facebook", "instagram", "tiktok", "youtube"]
            for platform in platforms:
                content = generate_post_content(lead, platform)
                
                draft = {
                    "platform": platform,
                    "content": content,
                    "status": "draft",
                    "video_url": raw.get("video_teaser_url"),
                    "metadata": {
                        "niche": lead.get("niche"),
                        "city": lead.get("city") or "Lakeland"
                    },
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                # FALLBACK: Try dedicated table, then raw_research metadata
                try:
                    supabase.table("social_drafts").upsert({**draft, "lead_id": lead['id']}, on_conflict="lead_id,platform").execute()
                except Exception as e:
                    if "relation \"social_drafts\" does not exist" in str(e):
                        print(f"  ⚠️ Table missing. Storing in raw_research metadata...")
                        social_drafts = raw.get("social_drafts", [])
                        # Dedupe metadata drafts
                        social_drafts = [d for d in social_drafts if d.get("platform") != platform]
                        social_drafts.append(draft)
                        
                        raw["social_drafts"] = social_drafts
                        supabase.table("contacts_master").update({
                            "raw_research": json.dumps(raw)
                        }).eq("id", lead['id']).execute()
                    else:
                        raise e
                        
                drafted += 1
                
        except Exception as e:
            print(f"⚠️ Failed to draft for {lead.get('id')}: {e}")
            
    print(f"✅ Processed {drafted} social drafts.")
    return drafted

def publish_social_multiplier_posts():
    """
    Publishes ready drafts to social channels.
    Runs 2x/day (9 AM, 4 PM EST).
    """
    supabase = get_supabase()
    if not supabase:
        print("❌ Supabase connection failed")
        return
    
    # 1. Fetch leads with research_done and social_drafts metadata
    res = supabase.table("contacts_master").select("*").eq("status", "research_done").limit(50).execute()
    leads = res.data
    
    if not leads:
        print("📭 No leads found for social publishing.")
        return
        
    published = 0
    webhook_url = os.environ.get("SOCIAL_PUBLISHING_WEBHOOK")
    
    for lead in leads:
        raw = json.loads(lead.get("raw_research") or "{}")
        drafts = raw.get("social_drafts", [])
        
        if not drafts:
            continue
            
        updated = False
        for draft in drafts:
            if draft.get("status") == "draft":
                print(f"🚀 Publishing {draft['platform']} for {lead.get('company_name')}...")
                
                # --- ACTUAL PUBLISHING LOGIC (Integrated Ayrshare) ---
                success = broadcast_to_social_channels(
                    lead_id=lead['id'],
                    platform=draft['platform'],
                    content=draft['content'],
                    video_url=draft.get("video_url")
                )
                
                if not success and webhook_url:
                    # Fallback to webhook if configured
                    try:
                        import requests
                        requests.post(webhook_url, json={
                            "lead_id": lead['id'],
                            "company": lead.get("company_name"),
                            "platform": draft['platform'],
                            "content": draft['content'],
                            "video_url": draft.get("video_url")
                        }, timeout=10)
                        print(f"  ✅ Fallback Webhook sent to {webhook_url}")
                        success = True
                    except Exception as e:
                        print(f"  ❌ Fallback Webhook failed: {e}")
                
                if success:
                    # Update status only on success
                    draft["status"] = "published"
                    draft["published_at"] = datetime.now(timezone.utc).isoformat()
                    updated = True
                    published += 1
                else:
                    print(f"  ⚠️ Publication failed for {draft['platform']}. Staying in draft mode.")
                
        if updated:
            raw["social_drafts"] = drafts
            supabase.table("contacts_master").update({
                "raw_research": json.dumps(raw)
            }).eq("id", lead['id']).execute()
            
    print(f"🏁 Published {published} social posts.")
    return published

def broadcast_to_social_channels(lead_id: str, platform: str, content: str, video_url: str = None):
    """
    Broadcasts a post to social channels via Ayrshare.
    """
    api_key = os.environ.get("AYRSHARE_API_KEY")
    if not api_key:
        print("  ⚠️ AYRSHARE_API_KEY not found. Skipping live broadcast.")
        return False
        
    try:
        from ayrshare import SocialPost
        sp = SocialPost(api_key)
        
        # Map internal platform names to Ayrshare names
        platform_map = {
            "linkedin": "linkedin",
            "twitter": "twitter",
            "facebook": "facebook",
            "instagram": "instagram",
            "tiktok": "tiktok",
            "youtube": "youtube"
        }
        ayr_platform = platform_map.get(platform, "linkedin")
        
        payload = {
            "post": content,
            "platforms": [ayr_platform]
        }
        
        if video_url:
            payload["mediaUrls"] = [video_url]
            
        res = sp.post(payload)
        if res.get("status") == "success":
            print(f"  ✅ Ayrshare Success: {res.get('id')}")
            return True
        else:
            print(f"  ❌ Ayrshare Error: {res.get('message')}")
            return False
            
    except Exception as e:
        print(f"  ❌ Ayrshare Exception: {e}")
        return False

def generate_post_content(lead: dict, platform: str) -> str:
    """Uses logic to generate platform-specific authority content."""
    company = lead.get("company_name")
    niche = lead.get("niche", "Local Business")
    city = lead.get("city") or "Lakeland"
    
    if platform == "linkedin":
        return (
            f"🚀 Transforming {niche} in {city}! \n\n"
            f"We just performed a deep AI audit for {company}. The results were eye-opening. "
            f"By identifying critical visibility gaps and FDBR compliance risks, we're not just saving "
            f"their reputation—we're positioning them for the next decade of growth.\n\n"
            f"Lakeland isn't quiet anymore. It's evolving. #LakelandBusiness #AIOps #SovereignEmpire"
        )
    elif platform in ["tiktok", "instagram", "youtube"]:
        # Short, punchy, curiosity-based for visual platforms
        return f"🚨 LOCAL ALERT: {company} just hit the high-visibility radar! 🚀 Watch how they're dominating {city} {niche} in seconds. #LocalDominance #{niche.replace(' ', '')} #{city}"
        
    elif platform == "facebook":
        return f"Attention {city}! 🏙️ We just completed a performance audit for {company}. The results for the local {niche} scene are incredible. Check out the full breakdown below! 👇 #SupportLocal #{city}Business"

    elif platform in ["x", "twitter"]:
        return (
            f"Just finished a localized AI audit for {company} in {city}. 🎯\n\n"
            f"Visibility gap identified. Compliance risk solved. Video teaser sent. \n\n"
            f"{city} is moving fast. Are you? ⚡️ #{city}Local #AIBusiness"
        )
    
    return f"New Audit Win: {company} in {city} is now optimized for the digital age. 📈"

if __name__ == "__main__":
    draft_social_multiplier_posts()
