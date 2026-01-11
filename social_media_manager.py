"""
Social Media Manager - Ayrshare Integration
Posts content and monitors engagement across all platforms
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

AYRSHARE_API_KEY = os.getenv("AYRSHARE_API_KEY")
AYRSHARE_BASE_URL = "https://app.ayrshare.com/api"

def post_to_social(content, platforms=["linkedin", "facebook", "twitter"]):
    """
    Post content to multiple social media platforms via Ayrshare
    
    Args:
        content: dict with 'content', 'hashtags', 'call_to_action'
        platforms: list of platforms to post to
    
    Returns:
        dict with post results
    """
    
    # Format content with hashtags
    full_content = content['content']
    if content.get('hashtags'):
        hashtags_str = ' '.join(['#' + h for h in content['hashtags']])
        full_content = f"{full_content}\n\n{hashtags_str}"
    
    # Ayrshare API payload
    payload = {
        "post": full_content,
        "platforms": platforms,
        "scheduleDate": None  # Post immediately, or set future date
    }
    
    headers = {
        "Authorization": f"Bearer {AYRSHARE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{AYRSHARE_BASE_URL}/post",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Posted to {', '.join(platforms)}")
            return {
                "success": True,
                "platforms": platforms,
                "post_id": result.get("id"),
                "posted_at": datetime.now().isoformat()
            }
        else:
            print(f"✗ Error posting: {response.status_code}")
            print(f"Response: {response.text}")
            return {
                "success": False,
                "error": response.text
            }
            
    except Exception as e:
        print(f"✗ Exception posting: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def schedule_post(content, platforms, schedule_time):
    """
    Schedule a post for future publication
    
    Args:
        content: dict with post content
        platforms: list of platforms
        schedule_time: ISO format datetime string
    """
    
    full_content = content['content']
    if content.get('hashtags'):
        hashtags_str = ' '.join(['#' + h for h in content['hashtags']])
        full_content = f"{full_content}\n\n{hashtags_str}"
    
    payload = {
        "post": full_content,
        "platforms": platforms,
        "scheduleDate": schedule_time
    }
    
    headers = {
        "Authorization": f"Bearer {AYRSHARE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{AYRSHARE_BASE_URL}/post",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✓ Scheduled for {schedule_time}")
            return response.json()
        else:
            print(f"✗ Error scheduling: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Exception scheduling: {e}")
        return None

def get_analytics(post_id=None):
    """
    Get analytics for posts
    
    Args:
        post_id: Specific post ID, or None for all recent posts
    """
    
    headers = {
        "Authorization": f"Bearer {AYRSHARE_API_KEY}"
    }
    
    try:
        if post_id:
            url = f"{AYRSHARE_BASE_URL}/analytics/post/{post_id}"
        else:
            url = f"{AYRSHARE_BASE_URL}/analytics/social"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"✗ Error getting analytics: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Exception getting analytics: {e}")
        return None

def monitor_engagement():
    """
    Monitor engagement across all platforms
    Returns summary of likes, comments, shares
    """
    
    analytics = get_analytics()
    
    if not analytics:
        return None
    
    summary = {
        "total_posts": 0,
        "total_likes": 0,
        "total_comments": 0,
        "total_shares": 0,
        "by_platform": {},
        "checked_at": datetime.now().isoformat()
    }
    
    # Parse analytics data
    # (Structure depends on Ayrshare API response)
    
    return summary

def main():
    """Test social media posting"""
    from social_content_generator import generate_content
    
    print("="*70)
    print("SOCIAL MEDIA MANAGER - TEST")
    print("="*70)
    
    # Generate content
    print("\nGenerating content...")
    content = generate_content("hvac_tips", "linkedin")
    
    print(f"\nContent:\n{content['content']}")
    print(f"\nHashtags: {content['hashtags']}")
    
    # Post to social
    print("\nPosting to social media...")
    result = post_to_social(content, platforms=["linkedin"])
    
    if result['success']:
        print(f"\n✓ Successfully posted!")
        print(f"Post ID: {result.get('post_id')}")
    else:
        print(f"\n✗ Failed to post")
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    main()
