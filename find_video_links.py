
from modules.database.supabase_client import get_supabase
import json

def find_video_links():
    sb = get_supabase()
    res = sb.table("outbound_touches").select("*").eq("channel", "social").order("ts", desc=True).limit(20).execute()
    
    found = []
    for touch in res.data:
        meta = touch.get("metadata", {})
        # Look for video identifiers or media URLs
        if "video" in str(meta).lower() or "mp4" in str(meta).lower():
            found.append({
                "ts": touch.get("ts"),
                "platform": meta.get("platform"),
                "post_url": meta.get("post_url") or meta.get("postUrl"),
                "media_urls": meta.get("mediaUrls")
            })
            
    if not found:
        print("No recent video posts found in outbound_touches.")
    else:
        print(json.dumps(found, indent=2))

if __name__ == "__main__":
    find_video_links()
