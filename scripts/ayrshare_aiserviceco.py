"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  🏢 AI SERVICE CO ONLY — DO NOT USE FOR ANY OTHER BRAND                        ║
║                                                                               ║
║  This script posts ONLY to the AI Service Co social media accounts.           ║
║  Ayrshare account: owner@aiserviceco.com                                     ║
║                                                                               ║
║  DO NOT reuse this API key for LakelandFinds or any other brand.             ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Setup:
1. API key is hardcoded for AI Service Co (owner@aiserviceco.com account)
2. Platforms connected: Facebook, Instagram, LinkedIn, Twitter, TikTok, Snapchat
3. Run: python scripts/ayrshare_aiserviceco.py --test   (preview schedule)
4. Run: python scripts/ayrshare_aiserviceco.py          (schedule all posts)
"""

import os
import json
import requests
from datetime import datetime, timedelta

# ─── Config ───
# ⚠️ AISERVICECO ONLY — This API key belongs to owner@aiserviceco.com
AYRSHARE_API_KEY = os.environ.get("AYRSHARE_AISERVICECO_KEY", "207BDC47-B8044FFC-8055E78F-556332E9")

# Complete Omnichannel Roster
TEXT_PLATFORMS = ["facebook", "instagram", "linkedin", "twitter"]
VIDEO_PLATFORMS = ["tiktok", "snapchat"]
PLATFORMS = TEXT_PLATFORMS + VIDEO_PLATFORMS

BASE_URL = "https://www.aiserviceco.com"
BRAND = "AiServiceCo"

AYRSHARE_HEADERS = {
    "Authorization": f"Bearer {AYRSHARE_API_KEY}",
    "Content-Type": "application/json"
}


def _brand_guard():
    """Safety check — abort if this script is accidentally modified for another brand."""
    if BRAND != "AiServiceCo" or "aiserviceco" not in BASE_URL.lower():
        raise RuntimeError(
            "⛔ BRAND MISMATCH! This script is ONLY for AI Service Co."
        )


# ─── Content Library ───
# Each post has: text, time_offset (hours from start)
POSTS = [
    # === DAY 1: Introduction / Core Offer ===
    {
        "text": "Is your local business missing calls because you're busy on the job?\n\n85% of customers whose calls aren't answered will not call back. They call your competitor.\n\nEnter AI Service Co. Our AI Receptionists answer every call, 24/7, book appointments, and capture leads while you sleep.\n\nStop losing money to missed calls. \n\n👉 Learn more: www.aiserviceco.com\n\n#AIAutomation #SmallBusiness #LocalBusiness #AIServiceCo #GrowYourBusiness",
        "day": 0, "hour": 10,
    },
    {
        "text": "The secret weapon of 7-figure home service businesses? \n\nThey never miss a lead.\n\nAutomate your lead follow-up, inbound calls, and appointment booking with conversational AI that sounds exactly like a human employee.\n\nReady to scale without the payroll bloat? \n🔗 www.aiserviceco.com\n\n#BusinessGrowth #AI #Automation #LeadGeneration #AIServiceCo",
        "day": 0, "hour": 15,
    },

    # === DAY 2: Missed Call Text Back ===
    {
        "text": "What happens when a customer calls while you're on the other line?\n\nWith our Missed Call Text Back system, they instantly receive a text: \"Hi! Sorry we missed your call. How can we help you today?\"\n\nInstantly turn a missed call into a text conversation and save the deal.\n\nGet it set up today:\n📱 www.aiserviceco.com/features\n\n#CustomerService #SmallBizTips #AIforBusiness #SalesTips",
        "day": 1, "hour": 9,
    },
    {
        "text": "Stop letting leads slip through the cracks. 📉\n\nIf you take longer than 5 minutes to respond to a new web lead, your chances of closing them drop by 80%.\n\nAI Service Co implements speed-to-lead automation that contacts prospects within seconds of them filling out a form.\n\nBe the first to reply. Win the business. \n\n👉 www.aiserviceco.com\n\n#SalesAutomation #SpeedToLead #BusinessHacks #AIServiceCo",
        "day": 1, "hour": 14,
    },

    # === DAY 3: AI Voice Receptionist ===
    {
        "text": "Meet the employee who never sleeps, never takes sick days, and handles infinite calls simultaneously. 🤖📞\n\nOur Voice AI Receptionists can answer FAQs, pre-qualify leads, and book appointments directly onto your calendar.\n\nSound like a massive corporation while keeping the overhead of a lean startup.\n\nListen to a demo:\n🎙️ www.aiserviceco.com\n\n#VoiceAI #AIReceptionist #BusinessEfficiency #TechTrends",
        "day": 2, "hour": 11,
    },
    {
        "text": "\"I don't need AI, my front desk handles everything.\"\n\nBut what happens after 5 PM? Or on weekends? Or when both lines are ringing?\n\nAI isn't here to replace your staff; it's here to catch everything that spills over so your team can focus on the customers right in front of them.\n\nUpgrade your operations today. 📈\n\n🔗 www.aiserviceco.com\n\n#OperationalExcellence #FutureOfWork #AIIntegration #SmallBiz",
        "day": 2, "hour": 16,
    },

    # === DAY 4: Lead Reactivation ===
    {
        "text": "You're sitting on a goldmine. 💰\n\nThat list of old, \"dead\" leads from the past 2 years? They aren't dead. They just need the right message at the right time.\n\nOur Database Reactivation campaigns use AI to text your old leads with an irresistible offer, turning cold lists into hot appointments.\n\nLet's wake up your database:\n💥 www.aiserviceco.com\n\n#LeadReactivation #DatabaseMarketing #RevenueGrowth #AIServiceCo",
        "day": 3, "hour": 10,
    },
    {
        "text": "Why pay for new ads when you haven't squeezed all the juice out of the leads you already paid for?\n\nBefore you increase your ad spend, let us run an AI reactivation campaign on your old contacts. You'll be amazed at the appointments we can generate from \"dead\" leads.\n\nMaximize your ROI. \n\n👉 www.aiserviceco.com\n\n#MarketingROI #AdSpend #AIOutreach #BusinessStrategy",
        "day": 3, "hour": 15,
    },

    # === DAY 5: Reviews and Reputation ===
    {
        "text": "Does your business have a 4.8+ rating on Google? ⭐⭐⭐⭐⭐\n\nIf not, you are losing clicks to the guy down the street who does.\n\nOur automated reputation management system requests reviews from your happy customers on autopilot, burying negative feedback and boosting your local SEO.\n\nStart dominating local search.\n\n📍 www.aiserviceco.com\n\n#LocalSEO #ReputationManagement #GoogleReviews #SmallBizMarketing",
        "day": 4, "hour": 9,
    },
    {
        "text": "The highest-rated business in town gets the most calls. It's that simple.\n\nDon't manually text customers asking for reviews. Let our AI system do it automatically right after a job is completed.\n\nScale your reputation seamlessly:\n\n🔗 www.aiserviceco.com\n\n#BusinessGrowth #AutomaticReviews #AIServiceCo #MarketingAutomation",
        "day": 4, "hour": 14,
    },

    # === DAY 6: Workflow Automation ===
    {
        "text": "How many hours a week do you spend sending manual emails, updating spreadsheets, and copying data between apps? ⏳\n\nIf the answer is \"more than zero\", you are losing money.\n\nWe build custom Zapier & Make automations that connect your entire software stack so your business runs on autopilot.\n\nReclaim your time:\n\n⚙️ www.aiserviceco.com\n\n#WorkflowAutomation #Zapier #MakeCom #TimeIsMoney #WorkSmart",
        "day": 5, "hour": 11,
    },
    {
        "text": "Stop working IN your business, and start working ON it.\n\nBy automating your onboarding, lead nurturing, and internal notifications, you free up the mental bandwidth required to actually scale.\n\nLet the robots do the busywork. You focus on the strategy.\n\n🚀 www.aiserviceco.com\n\n#Entrepreneurship #ScaleYourBusiness #AIAutomation #AIServiceCo",
        "day": 5, "hour": 16,
    },

    # === DAY 7: The Future is Now ===
    {
        "text": "The businesses that adopt AI today will be untouchable in 3 years.\n\nThe ones that ignore it will be obsolete.\n\nWhich side of history are you going to be on?\n\nIt's time to build your autonomous empire. Let's talk.\n\n👉 www.aiserviceco.com\n\n#ArtificialIntelligence #TechInnovation #FutureProof #BusinessLeadership",
        "day": 6, "hour": 10,
    },
    {
        "text": "Building a custom AI infrastructure used to cost enterprise companies millions.\n\nToday, local businesses can deploy the exact same technology for a fraction of the cost.\n\nVoice agents, SMS marketing, CRM automation—we handle it all.\n\nReady to dominate your market? \n\n🔗 www.aiserviceco.com\n\n#SMB #EnterpriseTech #AutomateEverything #AIServiceCo",
        "day": 6, "hour": 15,
    },

    # === DAY 8: Voice Agents vs Call Centers ===
    {
        "text": "Still paying $2,500/month for a remote answering service?\n\nThey take messages. They don't close deals.\n\nOur Voice AI agents sound human, understand your inventory, handle objections, and book appointments directly on your calendar.\n\nCut costs. Increase revenue. \n\n👉 www.aiserviceco.com\n\n#VoiceAI #BusinessEfficiency #CallCenter #AIServiceCo",
        "day": 7, "hour": 11,
    },
    {
        "text": "What is the cost of a missed call during your busiest season?\n\nFor most contractors, missing a single call costs them $1,500+ in lost revenue.\n\nInstall an AI receptionist and ensure you never miss a job again.\n\n🔗 www.aiserviceco.com\n\n#ContractorTips #LocalBusiness #AIAutomation #HomeServices",
        "day": 7, "hour": 16,
    },

    # === DAY 9: Database Marketing ===
    {
        "text": "You already paid for the lead.\n\nStop throwing money at Facebook ads when you have 1,500 old contacts sitting dormant in your CRM.\n\nWe build \"AI Reactivation Campaigns\" that text your old leads with a personalized offer. It's the cheapest revenue you will ever generate.\n\nWake up your database today:\n\n📱 www.aiserviceco.com\n\n#DatabaseMarketing #CustomerRetention #BusinessGrowth #EmailMarketing",
        "day": 8, "hour": 10,
    },
    {
        "text": "The formula for local business growth:\n\n1. Answer every call instantly (AI Receptionist)\n2. Text back every missed call (Speed to Lead)\n3. Automatically ask for reviews (Reputation)\n4. Reactivate old customers (Database Marketing)\n\nWe do all four. Let's talk.\n\n👉 www.aiserviceco.com\n\n#LocalSEO #GrowthHacks #BusinessStrategy #AIServiceCo",
        "day": 8, "hour": 15,
    },

    # === DAY 10: The Sovereign Empire ===
    {
        "text": "A business that requires your physical presence 24/7 isn't a business. It's a highly stressful job.\n\nThe real goal is to build an \"Autonomous Empire\"—a business that captures, nurtures, and closes leads whether you are in the office, on a roof, or on vacation.\n\nThat's what we build.\n\n🚀 www.aiserviceco.com\n\n#Entrepreneur #BusinessOwner #AutomateYourBusiness #WorkSmart",
        "day": 9, "hour": 10,
    },
    {
        "text": "If you aren't using AI to handle your inbound, your competitors will be.\n\nIt's not a trend. It's the new standard for customer service.\n\nBook a demo today to see how a custom AI system can transform your local business.\n\n🔗 www.aiserviceco.com\n\n#ArtificialIntelligence #AIServiceCo #FutureOfBusiness #TechTrends",
        "day": 9, "hour": 15,
    }
]


def schedule_all_posts(start_date=None):
    """Schedule all posts starting from tomorrow (or a specific date)."""
    if start_date is None:
        # Start tomorrow at midnight ET
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    print(f"📅 Scheduling {len(POSTS)} posts starting {start_date.strftime('%Y-%m-%d')}")
    print("=" * 60)

    results = []
    for i, post in enumerate(POSTS):
        
        # WE ONLY WANT TO SCHEDULE DAYS 7, 8, and 9 for this run
        if post["day"] < 7:
            continue
            
        # Calculate scheduled time (ET → UTC, add 5 hours)
        post_time = start_date + timedelta(days=post["day"], hours=post["hour"] + 5)
        schedule_iso = post_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Truncate display text
        preview = post["text"][:80].replace("\n", " ") + "..."

        # Smart Platform Routing: TikTok & Snapchat REQUIRE media.
        has_media = bool(post.get("mediaUrls"))
        target_platforms = PLATFORMS if has_media else TEXT_PLATFORMS

        print(f"\n[{i+1}/{len(POSTS)}] Day {post['day']+1} @ {post['hour']}:00 ET")
        print(f"  📝 {preview}")
        print(f"  📱 Routing to: {', '.join(target_platforms)}")
        print(f"  🕐 Scheduled: {schedule_iso}")

        try:
            payload = {
                "post": post["text"],
                "platforms": target_platforms,
                "scheduleDate": schedule_iso,
            }
            if has_media:
                payload["mediaUrls"] = post["mediaUrls"]
                
            res = requests.post("https://app.ayrshare.com/api/post", headers=AYRSHARE_HEADERS, json=payload)
            response = res.json()

            if response.get("status") == "success":
                print(f"  ✅ Scheduled! ID: {response.get('id', 'N/A')}")
                results.append({"status": "success", "id": response.get("id"), "time": schedule_iso})
            else:
                print(f"  ❌ Failed: {response}")
                results.append({"status": "failed", "error": str(response), "time": schedule_iso})

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({"status": "error", "error": str(e), "time": schedule_iso})

    # Summary
    success = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - success
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {success} scheduled, {failed} failed")
    print(f"📅 Posts span {POSTS[-1]['day']+1} days")

    return results


if __name__ == "__main__":
    import sys

    _brand_guard()

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Dry run — just show the schedule
        start = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
        print("🧪 DRY RUN MODE — No posts will actually be scheduled.\n")
        print(f"📅 Previewing {len(POSTS)} posts starting {start.strftime('%Y-%m-%d')}")
        print("=" * 60)
        
        for i, post in enumerate(POSTS):
            post_time = start + timedelta(days=post["day"], hours=post["hour"])
            preview = post["text"][:100].replace("\n", " ") + "..."
            
            has_media = bool(post.get("mediaUrls"))
            target_platforms = PLATFORMS if has_media else TEXT_PLATFORMS
            
            print(f"Day {post['day']+1} @ {post['hour']:02d}:00 | {preview}")
            print(f"Platforms: {', '.join(target_platforms)}\n")
    else:
        # Schedule for real
        schedule_all_posts()
