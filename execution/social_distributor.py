"""
Social Distributor - Multi-Platform Publishing Engine
======================================================

Unified posting to all major social platforms via:
- Ayrshare API (13 platforms)
- GHL Social Planner API (backup/GHL-specific)

Part of the Content Engine & Social Command Center.
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union

# Self-annealing integration
try:
    from annealing_engine import self_annealing, log_annealing_event
    ANNEALING_ENABLED = True
except ImportError:
    ANNEALING_ENABLED = False
    def self_annealing(func):
        return func

# Configuration
AYRSHARE_API_BASE = "https://api.ayrshare.com/api"
GHL_API_BASE = "https://services.leadconnectorhq.com"

# Supported platforms
AYRSHARE_PLATFORMS = [
    "facebook", "instagram", "twitter", "linkedin",
    "youtube", "tiktok", "pinterest", "reddit",
    "telegram", "threads", "gmb",  # Google Business Profile
    "snapchat", "bluesky"
]

GHL_PLATFORMS = [
    "facebook", "instagram", "linkedin", "gmb", "tiktok"
]

# Platform-specific limits
PLATFORM_LIMITS = {
    "twitter": {"text": 280, "media": 4},
    "instagram": {"text": 2200, "hashtags": 30},
    "facebook": {"text": 63206, "media": 10},
    "linkedin": {"text": 3000, "media": 9},
    "tiktok": {"text": 2200, "video_max_seconds": 180},
    "youtube": {"title": 100, "description": 5000},
    "pinterest": {"text": 500},
    "threads": {"text": 500},
}


class SocialDistributor:
    """
    Unified multi-platform social media publishing.
    
    Uses Ayrshare as primary API, GHL as backup.
    """
    
    def __init__(
        self,
        ayrshare_key: Optional[str] = None,
        ghl_api_key: Optional[str] = None,
        ghl_location_id: Optional[str] = None
    ):
        """
        Initialize Social Distributor.
        
        Args:
            ayrshare_key: Ayrshare API key
            ghl_api_key: GHL API key
            ghl_location_id: GHL location ID
        """
        self.ayrshare_key = ayrshare_key or os.getenv("AYRSHARE_API_KEY")
        self.ghl_api_key = ghl_api_key or os.getenv("GHL_API_KEY")
        self.ghl_location_id = ghl_location_id or os.getenv("GHL_LOCATION_ID")
        
        self.post_history = []
        
        # Check configuration
        if self.ayrshare_key:
            print(f"[SOCIAL] Ayrshare: Configured")
        else:
            print("[SOCIAL] Warning: AYRSHARE_API_KEY not set")
        
        if self.ghl_api_key:
            print(f"[SOCIAL] GHL: Configured")
        else:
            print("[SOCIAL] Warning: GHL_API_KEY not set")
    
    def _ayrshare_headers(self) -> Dict[str, str]:
        """Get Ayrshare API headers."""
        return {
            "Authorization": f"Bearer {self.ayrshare_key}",
            "Content-Type": "application/json"
        }
    
    def _ghl_headers(self) -> Dict[str, str]:
        """Get GHL API headers."""
        return {
            "Authorization": f"Bearer {self.ghl_api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }
    
    def _optimize_for_platform(
        self,
        text: str,
        platform: str,
        hashtags: Optional[List[str]] = None
    ) -> str:
        """
        Optimize content for specific platform limits.
        
        Args:
            text: Original text content
            platform: Target platform
            hashtags: Optional hashtags to append
        
        Returns:
            Optimized text
        """
        limits = PLATFORM_LIMITS.get(platform, {})
        max_length = limits.get("text", 5000)
        
        # Add hashtags if provided
        if hashtags:
            max_hashtags = limits.get("hashtags", 30)
            hashtag_str = " ".join(f"#{tag}" for tag in hashtags[:max_hashtags])
            text = f"{text}\n\n{hashtag_str}"
        
        # Truncate if necessary
        if len(text) > max_length:
            text = text[:max_length - 3] + "..."
        
        return text
    
    @self_annealing
    def post_to_ayrshare(
        self,
        text: str,
        platforms: List[str],
        media_url: Optional[str] = None,
        schedule_time: Optional[datetime] = None,
        hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Post to multiple platforms via Ayrshare.
        
        Args:
            text: Post content
            platforms: List of platforms to post to
            media_url: URL to image/video
            schedule_time: Optional scheduled post time
            hashtags: Optional hashtags
        
        Returns:
            Post status with platform-specific IDs
        """
        if not self.ayrshare_key:
            return {"success": False, "error": "AYRSHARE_API_KEY not configured"}
        
        # Validate platforms
        valid_platforms = [p for p in platforms if p in AYRSHARE_PLATFORMS]
        if not valid_platforms:
            return {"success": False, "error": f"No valid platforms. Supported: {AYRSHARE_PLATFORMS}"}
        
        print(f"[SOCIAL] Posting to: {', '.join(valid_platforms)}")
        
        # Build payload
        payload = {
            "post": text,
            "platforms": valid_platforms
        }
        
        if media_url:
            payload["mediaUrls"] = [media_url]
        
        if schedule_time:
            payload["scheduleDate"] = schedule_time.isoformat()
        
        # Add platform-specific content
        if hashtags:
            platform_posts = {}
            for platform in valid_platforms:
                optimized = self._optimize_for_platform(text, platform, hashtags)
                platform_posts[platform] = {"post": optimized}
            payload["platformPosts"] = platform_posts
        
        try:
            response = requests.post(
                f"{AYRSHARE_API_BASE}/post",
                headers=self._ayrshare_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                post_record = {
                    "id": result.get("id"),
                    "platforms": valid_platforms,
                    "text": text[:100],
                    "media_url": media_url,
                    "scheduled": schedule_time.isoformat() if schedule_time else None,
                    "posted_at": datetime.now().isoformat(),
                    "api": "ayrshare",
                    "response": result
                }
                self.post_history.append(post_record)
                
                print(f"[SOCIAL] ✅ Posted successfully to {len(valid_platforms)} platforms")
                
                return {
                    "success": True,
                    "post_id": result.get("id"),
                    "platforms": valid_platforms,
                    "platform_ids": result.get("postIds", {}),
                    "status": "scheduled" if schedule_time else "posted"
                }
            else:
                return {
                    "success": False,
                    "error": f"API error {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @self_annealing
    def post_to_ghl(
        self,
        text: str,
        platforms: List[str],
        media_url: Optional[str] = None,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Post via GHL Social Planner API.
        
        Args:
            text: Post content
            platforms: List of platforms
            media_url: Media URL
            schedule_time: Scheduled time
        
        Returns:
            Post status
        """
        if not self.ghl_api_key or not self.ghl_location_id:
            return {"success": False, "error": "GHL API not configured"}
        
        valid_platforms = [p for p in platforms if p in GHL_PLATFORMS]
        if not valid_platforms:
            return {"success": False, "error": f"No valid GHL platforms. Supported: {GHL_PLATFORMS}"}
        
        print(f"[SOCIAL] GHL posting to: {', '.join(valid_platforms)}")
        
        payload = {
            "locationId": self.ghl_location_id,
            "summary": text,
            "platforms": valid_platforms,
            "type": "post"
        }
        
        if media_url:
            payload["media"] = [{"url": media_url, "type": "image"}]
        
        if schedule_time:
            payload["scheduledAt"] = schedule_time.isoformat()
        
        try:
            response = requests.post(
                f"{GHL_API_BASE}/social-media-posting/posts",
                headers=self._ghl_headers(),
                json=payload
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    "success": True,
                    "post_id": result.get("id"),
                    "platforms": valid_platforms,
                    "api": "ghl"
                }
            else:
                return {
                    "success": False,
                    "error": f"GHL API error: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post(
        self,
        text: str,
        platforms: List[str],
        media_url: Optional[str] = None,
        schedule_time: Optional[datetime] = None,
        hashtags: Optional[List[str]] = None,
        prefer_api: str = "ayrshare"
    ) -> Dict[str, Any]:
        """
        Post to platforms using best available API.
        
        Args:
            text: Post content
            platforms: Target platforms
            media_url: Optional media URL
            schedule_time: Optional schedule time
            hashtags: Optional hashtags
            prefer_api: "ayrshare" or "ghl"
        
        Returns:
            Unified post result
        """
        if prefer_api == "ayrshare" and self.ayrshare_key:
            result = self.post_to_ayrshare(text, platforms, media_url, schedule_time, hashtags)
            if result.get("success"):
                return result
            # Fall back to GHL
            print("[SOCIAL] Ayrshare failed, trying GHL...")
        
        if self.ghl_api_key:
            return self.post_to_ghl(text, platforms, media_url, schedule_time)
        
        return {"success": False, "error": "No API configured"}
    
    def schedule_week(
        self,
        posts: List[Dict[str, Any]],
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Schedule a week's worth of posts.
        
        Args:
            posts: List of {text, platforms, media_url}
            start_date: When to start (default: tomorrow)
        
        Returns:
            Scheduling results
        """
        start_date = start_date or (datetime.now() + timedelta(days=1))
        results = []
        
        for i, post in enumerate(posts):
            # Spread posts throughout the day (9am, 12pm, 3pm, 6pm)
            hours = [9, 12, 15, 18]
            day_offset = i // len(hours)
            hour = hours[i % len(hours)]
            
            schedule_time = start_date.replace(hour=hour, minute=0) + timedelta(days=day_offset)
            
            result = self.post(
                text=post.get("text", ""),
                platforms=post.get("platforms", ["facebook", "instagram"]),
                media_url=post.get("media_url"),
                schedule_time=schedule_time,
                hashtags=post.get("hashtags")
            )
            
            results.append({
                "scheduled_for": schedule_time.isoformat(),
                "result": result
            })
            
            time.sleep(0.5)  # Rate limiting
        
        return {
            "success": all(r["result"].get("success") for r in results),
            "scheduled_posts": len(results),
            "results": results
        }
    
    def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """
        Get engagement analytics for a post.
        
        Args:
            post_id: Ayrshare post ID
        
        Returns:
            Engagement metrics
        """
        if not self.ayrshare_key:
            return {"success": False, "error": "Ayrshare not configured"}
        
        try:
            response = requests.get(
                f"{AYRSHARE_API_BASE}/analytics/post",
                headers=self._ayrshare_headers(),
                params={"id": post_id}
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "analytics": response.json()
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_comments(self, post_id: str) -> Dict[str, Any]:
        """
        Get comments on a post.
        
        Args:
            post_id: Ayrshare post ID
        
        Returns:
            Comments list
        """
        if not self.ayrshare_key:
            return {"success": False, "error": "Ayrshare not configured"}
        
        try:
            response = requests.get(
                f"{AYRSHARE_API_BASE}/comments",
                headers=self._ayrshare_headers(),
                params={"id": post_id}
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "comments": response.json()
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def reply_to_comment(
        self,
        post_id: str,
        comment_id: str,
        reply_text: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Reply to a comment.
        
        Args:
            post_id: Post ID
            comment_id: Comment ID to reply to
            reply_text: Reply content
            platform: Platform name
        
        Returns:
            Reply status
        """
        if not self.ayrshare_key:
            return {"success": False, "error": "Ayrshare not configured"}
        
        try:
            response = requests.post(
                f"{AYRSHARE_API_BASE}/comments",
                headers=self._ayrshare_headers(),
                json={
                    "id": post_id,
                    "platforms": [platform],
                    "comment": reply_text,
                    "commentId": comment_id
                }
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "reply": response.json()
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


# Convenience functions
def quick_post(
    text: str,
    platforms: List[str] = ["facebook", "instagram", "twitter"],
    hashtags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Quick post to multiple platforms."""
    distributor = SocialDistributor()
    return distributor.post(text, platforms, hashtags=hashtags)


def post_ad_content(
    content_metadata: Dict[str, Any],
    caption: str,
    platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Post content from the content library.
    
    Args:
        content_metadata: Metadata from content library
        caption: Post caption
        platforms: Target platforms (default: all)
    """
    platforms = platforms or ["facebook", "instagram", "twitter", "linkedin"]
    
    media_url = content_metadata.get("file_url") or content_metadata.get("video_url")
    
    distributor = SocialDistributor()
    return distributor.post(
        text=caption,
        platforms=platforms,
        media_url=media_url
    )


if __name__ == "__main__":
    print("[SOCIAL] Social Distributor - Multi-Platform Publishing")
    print("=" * 60)
    
    # Check configuration
    ayrshare_key = os.getenv("AYRSHARE_API_KEY")
    ghl_key = os.getenv("GHL_API_KEY")
    
    print()
    print("Configuration Status:")
    print(f"  Ayrshare: {'✅ Configured' if ayrshare_key else '⚠️ Not set'}")
    print(f"  GHL: {'✅ Configured' if ghl_key else '⚠️ Not set'}")
    
    print()
    print("Supported Platforms:")
    print(f"  Ayrshare: {', '.join(AYRSHARE_PLATFORMS)}")
    print(f"  GHL: {', '.join(GHL_PLATFORMS)}")
    
    # Initialize
    distributor = SocialDistributor()
    print()
    print(f"[SOCIAL] Post History: {len(distributor.post_history)} posts")
