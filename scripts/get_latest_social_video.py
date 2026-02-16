
from modules.database.supabase_client import get_supabase
import json

def get_latest_video_post():
    supabase = get_supabase()
    res = supabase.table("contacts_master").select("id", "company_name", "raw_research").execute()
    leads = res.data if hasattr(res, 'data') else []
    
    published_videos = []
    for lead in leads:
        raw_data = lead.get("raw_research")
        if not raw_data: continue
        
        if isinstance(raw_data, str):
            try:
                raw = json.loads(raw_data)
            except:
                continue
        else:
            raw = raw_data
            
        drafts = raw.get("social_drafts", [])
        for d in drafts:
            if d.get("status") == "published" and d.get("video_url"):
                published_videos.append({
                    "company": lead.get("company_name"),
                    "platform": d["platform"],
                    "video_url": d["video_url"],
                    "published_at": d.get("published_at", "Unknown")
                })
    
    # Sort by published_at (assume ISO format)
    published_videos.sort(key=lambda x: x["published_at"], reverse=True)
    
    if published_videos:
        latest = published_videos[0]
        print(f"\n--- LATEST SOCIAL VIDEO POST ---")
        print(f"Company: {latest['company']}")
        print(f"Platform: {latest['platform']}")
        print(f"Published At: {latest['published_at']}")
        print(f"URL: {latest['video_url']}")
    else:
        print("\n📭 No published social video posts found.")

if __name__ == "__main__":
    get_latest_video_post()
