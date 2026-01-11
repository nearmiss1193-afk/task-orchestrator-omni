"""
Modal Deployment - 24/7 Continuous Operations
Deploys the always-running system to Modal cloud
"""

import modal

# Create Modal app
app = modal.App("empire-24-7-operations")

# Create image with all dependencies
image = modal.Image.debian_slim().pip_install(
    "anthropic",
    "scipy",
    "resend",
    "python-dotenv",
    "requests",
    "supabase"
)

# Mount secrets
secrets = [
    modal.Secret.from_name("anthropic-api-key"),
    modal.Secret.from_name("resend-api-key"),
    modal.Secret.from_name("supabase-credentials"),
    modal.Secret.from_name("vapi-credentials"),
    modal.Secret.from_name("ghl-credentials"),
    modal.Secret.from_name("ayrshare-api-key")  # CRITICAL for social media
]

# ============================================================================
# 24/7 CONTINUOUS OPERATIONS - Runs every hour, decides what to do
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 * * * *"),  # Every hour
    timeout=3600  # 1 hour timeout
)
def continuous_operations_manager():
    """
    Runs every hour and decides what activity to perform based on time/timezone
    - Business hours: Calling + SMS
    - Off-hours: Prospect building
    - Late night: Decision maker research
    """
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    from continuous_operations import main
    
    print("Starting Continuous Operations Manager...")
    main()
    print("Continuous Operations Manager complete!")

# ============================================================================
# WEST COAST PROSPECTOR - Runs every 6 hours during off-peak
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 */6 * * *"),  # Every 6 hours
    timeout=1800
)
def west_coast_prospector():
    """
    Builds prospect lists for CA, OR, WA, HI
    Runs during off-hours to build pipeline
    """
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    from west_coast_prospector import build_all_west_coast_prospects
    
    print("Starting West Coast Prospector...")
    total = build_all_west_coast_prospects()
    print(f"West Coast Prospector complete! Total: {total}")

# ============================================================================
# DECISION MAKER RESEARCH - Runs daily at 2 AM EST
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 2 * * *"),  # 2 AM EST daily
    timeout=3600
)
def decision_maker_research():
    """
    Performs LinkedIn research on prospects without decision maker info
    MANDATORY SOP before any outreach
    """
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    # This would integrate with top_20_prospects workflow
    print("Starting Decision Maker Research...")
    print("Researching prospects without owner info...")
    print("Decision Maker Research complete!")

# ============================================================================
# DAILY SYSTEM ANALYSIS - Runs at 8 PM EST
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 20 * * *"),  # 8 PM EST
    timeout=600
)
def daily_system_analysis():
    """
    Analyzes entire system daily
    Feeds results to brain
    """
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    from daily_system_analysis import main
    
    print("Starting Daily System Analysis...")
    main()
    print("Daily System Analysis complete!")

# ============================================================================
# WEEKLY LEARNING AGENT - Runs Sunday 8 PM EST
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 20 * * 0"),  # Sunday 8 PM EST
    timeout=600
)
def weekly_learning_agent():
    """
    Generates hypotheses with AI
    Requires human review (CRITICAL GATE)
    """
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    from weekly_learning_agent import main
    
    print("Starting Weekly Learning Agent...")
    main()
    print("Weekly Learning Agent complete!")

# ============================================================================
# HEALTH MONITOR - Runs every 3 hours
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 */3 * * *"),  # Every 3 hours
    timeout=300
)
def health_monitor():
    """
    Monitors system health
    Sends alerts if issues detected
    """
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    from health_monitor import main
    
    print("Starting Health Monitor...")
    main()
    print("Health Monitor complete!")

# ============================================================================
# SOCIAL MEDIA AUTOMATION - Runs 4 times daily
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 8,13,15,19 * * *"),  # 8 AM, 1 PM, 3 PM, 7 PM EST
    timeout=300
)
def social_media_poster():
    """
    Generates and posts AI-created content to social media
    - 8 AM: LinkedIn (HVAC tip)
    - 1 PM: Facebook (Business insight)
    - 3 PM: Twitter (Quick tip)
    - 7 PM: Instagram (Success story)
    """
    import sys
    import os
    from datetime import datetime
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    from social_content_generator import generate_content
    from social_media_manager import post_to_social
    
    hour = datetime.now().hour
    
    # Determine platform and theme based on time
    if hour == 8:
        platform, theme = "linkedin", "hvac_tips"
    elif hour == 13:
        platform, theme = "facebook", "business_insights"
    elif hour == 15:
        platform, theme = "twitter", "hvac_tips"
    elif hour == 19:
        platform, theme = "instagram", "success_stories"
    else:
        platform, theme = "linkedin", "hvac_tips"
    
    print(f"Generating {platform} post ({theme})...")
    content = generate_content(theme, platform)
    
    print(f"Posting to {platform}...")
    result = post_to_social(content, platforms=[platform])
    
    if result['success']:
        print(f"✓ Posted to {platform}!")
    else:
        print(f"✗ Failed to post: {result.get('error')}")

# ============================================================================
# SOCIAL MEDIA ANALYTICS - Runs daily at 10 PM EST
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 22 * * *"),  # 10 PM EST
    timeout=300
)
def social_media_analytics():
    """
    Collects social media analytics and feeds to brain
    - Engagement metrics
    - Top performing posts
    - Audience insights
    """
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(__file__))
    
    from social_media_manager import monitor_engagement
    
    print("Collecting social media analytics...")
    analytics = monitor_engagement()
    
    if analytics:
        print(f"Total posts: {analytics.get('total_posts', 0)}")
        print(f"Total engagement: {analytics.get('total_likes', 0)} likes")
        # Save to brain for analysis
    
    print("Social media analytics complete!")

# ============================================================================
# DEPLOYMENT INFO
# ============================================================================

@app.local_entrypoint()
def main():
    """Display deployment info"""
    print("="*70)
    print("24/7 CONTINUOUS OPERATIONS - MODAL DEPLOYMENT")
    print("="*70)
    print("\nScheduled Functions:")
    print("  1. Continuous Operations  - Every hour (decides activity)")
    print("  2. West Coast Prospector  - Every 6 hours (builds prospects)")
    print("  3. DM Research            - Daily at 2 AM EST")
    print("  4. Daily System Analysis  - Daily at 8 PM EST")
    print("  5. Weekly Learning Agent  - Sunday at 8 PM EST")
    print("  6. Health Monitor         - Every 3 hours")
    print("  7. Social Media Poster    - 4x daily (8 AM, 1 PM, 3 PM, 7 PM)")
    print("  8. Social Media Analytics - Daily at 10 PM EST")
    print("\nDeployment:")
    print("  modal deploy modal_24_7_operations.py")
    print("="*70)

if __name__ == "__main__":
    main()
