"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  LAKELANDFINDS.COM ONLY — DO NOT USE FOR ANY OTHER BRAND               ║
║                                                                               ║
║  This script posts ONLY to the LakelandFinds Facebook + Instagram accounts.  ║
║  Ayrshare account: danc@lakelandfinds.com                                    ║
║                                                                               ║
║  DO NOT reuse this API key for AiServiceCo, empire-unified, or any other     ║
║  brand. Each brand must have its own Ayrshare profile and API key.           ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Setup:
1. pip install social-post-api
2. API key is hardcoded for LakelandFinds (danc@lakelandfinds.com account)
3. Connect Facebook Page + Instagram in the Ayrshare dashboard
4. Run: python ayrshare_poster.py --test   (preview schedule)
5. Run: python ayrshare_poster.py          (schedule all posts)
"""

import os
import json
from datetime import datetime, timedelta
from social_post_api import SocialPost

# ─── Config ───
# ⚠️ LAKELANDFINDS.COM ONLY — This API key belongs to danc@lakelandfinds.com
# DO NOT replace with any other Ayrshare key. Each brand gets its own script.
AYRSHARE_API_KEY = os.environ.get("AYRSHARE_LAKELANDFINDS_KEY", "E8C18282-ED4F4FB3-AD1EF40B-76D7872A")
PLATFORMS = ["facebook", "instagram"]  # LakelandFinds accounts ONLY
BASE_URL = "https://www.lakelandfinds.com"  # DO NOT change
BRAND = "LakelandFinds"  # Safety check — used in runtime guard

social = SocialPost(AYRSHARE_API_KEY)


def _brand_guard():
    """Safety check — abort if this script is accidentally modified for another brand."""
    if BRAND != "LakelandFinds" or "lakelandfinds" not in BASE_URL:
        raise RuntimeError(
            "⛔ BRAND MISMATCH! This script is ONLY for LakelandFinds.com. "
            "Create a separate script for other brands. DO NOT reuse this one."
        )


# ─── Content Library ───
# Each post has: text, time_offset (hours from start), link (optional)
POSTS = [
    # === DAY 1: Launch ===
    {
        "text": "🎉 LakelandFinds is LIVE!\n\nDiscover 5,700+ local businesses right here in Lakeland, FL — all in one place.\n\n🔍 Search by category\n⭐ Compare real Google ratings\n📍 Get directions instantly\n\nWhether you need a plumber at midnight, the best tacos downtown, or a trusted mechanic — LakelandFinds has you covered.\n\n100% free. Built for Lakeland, by Lakeland.\n\n👉 www.lakelandfinds.com\n\n#LakelandFL #LakelandFinds #SupportLocal #ShopLocal #LakelandFlorida #PolkCounty",
        "day": 0, "hour": 11,
    },
    {
        "text": "Did you know there are 5,700+ businesses in Lakeland? 🤯\n\nWe listed ALL of them on one free, searchable directory. Restaurants, plumbers, dentists, auto shops — everything.\n\nStop scrolling through pages of Google results. Find what you need in seconds.\n\n🔗 www.lakelandfinds.com\n\n#LakelandFL #SupportLocalLakeland #PolkCounty #ShopLocal863",
        "day": 0, "hour": 15,
    },
    {
        "text": "🏠 New to Lakeland? Moving to the area?\n\nHere's the ONLY directory you need. 5,700+ businesses with real ratings, phone numbers, and directions.\n\nSave this link — you'll thank us later 👇\nwww.lakelandfinds.com\n\n#MovingToLakeland #LakelandFL #PolkCounty #CentralFlorida #FloridaLiving",
        "day": 0, "hour": 19,
    },

    # === DAY 2: Restaurants ===
    {
        "text": "🍽️ Looking for the BEST restaurants in Lakeland?\n\nWe just dropped our 2026 guide — from hidden gems to local legends.\n\nOver 200 restaurants rated 4+ stars. Browse by cuisine, check ratings, and find your next favorite spot.\n\n📖 www.lakelandfinds.com/blog/best-restaurants-lakeland-fl\n\nWhat's YOUR go-to restaurant in Lakeland? Drop it below! 👇\n\n#LakelandEats #LakelandRestaurants #LakelandFL #FoodieFinds #PolkCountyFood",
        "day": 1, "hour": 11,
    },
    {
        "text": "Friday night dinner plans? 🍕\n\nDon't waste 20 minutes deciding where to eat. LakelandFinds shows you every restaurant in Lakeland sorted by rating.\n\nFilter by cuisine. Check reviews. Pick a winner.\n\n🔗 www.lakelandfinds.com/search?category=Restaurant\n\n#LakelandDining #FridayNightOut #LakelandFL #DateNightLakeland",
        "day": 1, "hour": 16,
    },

    # === DAY 3: Home Services ===
    {
        "text": "Need a plumber? HVAC tech? Roofer? 🏠\n\nFinding reliable home service pros in Lakeland just got easier.\n\nLakelandFinds lists 100+ trusted home service companies with real ratings from your neighbors.\n\n✅ Plumbing ✅ HVAC & AC ✅ Roofing ✅ Electrical ✅ Landscaping ✅ Pest Control\n\n👉 www.lakelandfinds.com/blog/top-home-services-lakeland\n\n#LakelandFL #HomeServices #LakelandPlumber #LakelandRoofer #PolkCounty",
        "day": 2, "hour": 10,
    },
    {
        "text": "🌡️ Is your AC struggling in this Florida heat?\n\nDon't wait until it dies. Find a top-rated HVAC company in Lakeland right now.\n\nAll rated by real customers. All with phone numbers ready to call.\n\n❄️ www.lakelandfinds.com/search?category=HVAC\n\n#LakelandHVAC #FloridaHeat #ACRepair #LakelandFL #CentralFlorida",
        "day": 2, "hour": 14,
    },
    {
        "text": "PSA for Lakeland homeowners 🏡\n\nFlorida's termite season is coming. If you don't have regular pest control, now's the time.\n\nWe found every pest control company in Lakeland and sorted them by rating 👇\n\n🪲 www.lakelandfinds.com/search?category=Pest+Control\n\n#PestControl #LakelandFL #FloridaHome #TermiteSeason #PolkCounty",
        "day": 2, "hour": 18,
    },

    # === DAY 4: Things To Do ===
    {
        "text": "Think Lakeland is \"just a small town\"? Think again. 🌺\n\nFrom Hollis Garden to Frank Lloyd Wright architecture, craft breweries to Circle B Bar Reserve — Lakeland is full of hidden gems.\n\nWe put together the ultimate guide 👇\n\n🔗 www.lakelandfinds.com/blog/things-to-do-lakeland-florida\n\nTag someone who needs to explore Lakeland more! 🏷️\n\n#LakelandFL #ThingsToDoLakeland #ExploreFL #VisitLakeland #CentralFlorida",
        "day": 3, "hour": 11,
    },
    {
        "text": "Weekend plans in Lakeland? Here are 5 ideas 🌴\n\n1️⃣ Walk Hollis Garden at sunset\n2️⃣ Hike Circle B Bar Reserve\n3️⃣ Try a new restaurant downtown\n4️⃣ Visit Frank Lloyd Wright buildings at FSC\n5️⃣ Hit up a local craft brewery\n\nFind directions to all of these on LakelandFinds 📍\n\n#WeekendInLakeland #LakelandFL #ThingsToDoFL #PolkCounty",
        "day": 3, "hour": 17,
    },

    # === DAY 5: Business CTA ===
    {
        "text": "🏪 Are you a business owner in Lakeland?\n\nYour business is already listed on LakelandFinds — with ratings, address, and contact info.\n\nClaim your listing for FREE:\n✨ Update your info\n📸 Add photos\n⭐ Highlight reviews\n🚀 Boost your AI search visibility\n\n👉 www.lakelandfinds.com/claim\n\n#LakelandBusiness #SmallBusiness #LakelandFL #ShopLocalLakeland",
        "day": 4, "hour": 10,
    },
    {
        "text": "💡 Fun fact: Google's AI now recommends businesses to people BEFORE they even search.\n\nIt's called AI Overviews. And if your business isn't optimized for it, you're invisible to a growing number of customers.\n\nStep 1: Make sure you're on LakelandFinds ✅\nStep 2: Claim your listing\nStep 3: Get found by AI\n\n🔗 www.lakelandfinds.com/claim\n\n#AISearch #LocalSEO #LakelandFL #SmallBusinessTips #DigitalMarketing",
        "day": 4, "hour": 15,
    },

    # === DAY 6: Category Spotlights ===
    {
        "text": "🚗 Looking for an honest mechanic in Lakeland?\n\nWe get it — finding a trustworthy auto shop is tough. That's why we listed every auto repair business in Lakeland with real Google ratings.\n\nNo sponsored results. No ads. Just real reviews.\n\n🔧 www.lakelandfinds.com/search?category=Auto+Repair\n\n#LakelandAutoRepair #MechanicLakeland #CarRepair #LakelandFL",
        "day": 5, "hour": 11,
    },
    {
        "text": "💇 Need a haircut? New stylist? Color refresh?\n\nLakeland has dozens of amazing hair salons — but which one is right for you?\n\nBrowse all of them sorted by rating on LakelandFinds ✂️\n\nwww.lakelandfinds.com/search?category=Hair+Salon\n\n#LakelandHairSalon #LakelandBeauty #HairStylist #PolkCounty",
        "day": 5, "hour": 16,
    },
    {
        "text": "🐾 Pet parents of Lakeland!\n\nVets, groomers, pet stores, dog walkers — we've got them ALL listed.\n\nFind the perfect care for your fur baby 🐕\n\nwww.lakelandfinds.com/search?category=Pet+Services\n\n#LakelandPets #DogMomLakeland #PetServicesFL #LakelandFL #PolkCounty",
        "day": 5, "hour": 19,
    },

    # === DAY 7: Engagement ===
    {
        "text": "📊 This week's LakelandFinds stats:\n\n🏢 5,700+ businesses listed\n🔍 30+ categories\n⭐ Hundreds of 5-star businesses\n📱 100% free to use\n\nWhat category should we spotlight next? Comment below! 👇\n\n#LakelandFL #SupportLocal #LakelandCommunity #PolkCounty",
        "day": 6, "hour": 10,
    },
    {
        "text": "🗳️ POLL: What's the hardest service to find in Lakeland?\n\nA) A good electrician\nB) A reliable plumber\nC) An affordable dentist\nD) A trustworthy mechanic\n\nComment your answer! We'll spotlight the winning category 🔍\n\n#LakelandFL #HomeServices #LakelandCommunity #PolkCounty",
        "day": 6, "hour": 15,
    },

    # === DAY 8: Tips ===
    {
        "text": "🔑 3 things to check before hiring ANY home service company in Lakeland:\n\n1️⃣ Check their rating on LakelandFinds\n2️⃣ Verify they're licensed in Florida\n3️⃣ Get at least 2 quotes before committing\n\nSave this for later! Bookmark LakelandFinds 📌\n\nwww.lakelandfinds.com\n\n#HomeServiceTips #LakelandFL #FloridaHomeowner #PolkCounty",
        "day": 7, "hour": 11,
    },
    {
        "text": "☕ Lakeland coffee lovers — where do YOU get your morning fix?\n\nWe've mapped out every coffee shop in town. Rate drops, cozy vibes, strong espresso — you choose.\n\nBrowse them all 👇\nwww.lakelandfinds.com/search?category=Coffee+Shop\n\n#LakelandCoffee #CoffeeLovers #LakelandFL #LocalCoffee",
        "day": 7, "hour": 17,
    },

    # === DAY 9: Health ===
    {
        "text": "🏥 Finding a good dentist in Lakeland shouldn't be stressful.\n\nWe listed every dental practice in the area with real patient ratings. Compare, choose, and book with confidence.\n\n🦷 www.lakelandfinds.com/search?category=Dentist\n\n#LakelandDentist #DentalCare #LakelandFL #PolkCountyHealth",
        "day": 8, "hour": 10,
    },
    {
        "text": "🧹 Spring cleaning? These Lakeland cleaning services are top-rated by your neighbors 🏠\n\nFrom deep cleans to regular maintenance — find your match:\n\n✨ www.lakelandfinds.com/search?category=Cleaning+Services\n\n#CleaningServices #LakelandFL #HomeCleaningLakeland #PolkCounty",
        "day": 8, "hour": 16,
    },

    # === DAY 10: Mixed ===
    {
        "text": "🔒 Locked out? Need a locksmith in Lakeland FAST?\n\nWe've got every locksmith in the city listed with phone numbers and ratings. No Googling around in a panic.\n\nSave this link — you'll need it someday 🔑\n\nwww.lakelandfinds.com/search?category=Locksmith\n\n#LakelandLocksmith #EmergencyLocksmith #LakelandFL #LockedOut",
        "day": 9, "hour": 11,
    },
    {
        "text": "🌿 Your Lakeland lawn needs love too!\n\nWhether you need weekly mowing or a complete landscape overhaul, find the top-rated landscapers in town:\n\nwww.lakelandfinds.com/search?category=Landscaping\n\n#LakelandLandscaping #LawnCare #FloridaYard #LakelandFL #PolkCounty",
        "day": 9, "hour": 15,
    },
    {
        "text": "💪 New Year's resolution still going? 🏋️\n\nFind every gym, fitness studio, and yoga class in Lakeland — all in one place, all rated by real members.\n\nwww.lakelandfinds.com/search?category=Gym\n\n#LakelandGym #FitnessLakeland #WorkoutFL #LakelandFL #FloridaFitness",
        "day": 9, "hour": 19,
    },
]


def schedule_all_posts(start_date=None):
    """Schedule all posts starting from tomorrow (or a specific date)."""
    if start_date is None:
        # Start tomorrow at midnight ET
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    print(f"📅 Scheduling {len(POSTS)} posts starting {start_date.strftime('%Y-%m-%d')}")
    print(f"📱 Platforms: {', '.join(PLATFORMS)}")
    print("=" * 60)

    results = []
    for i, post in enumerate(POSTS):
        # Calculate scheduled time (ET → UTC, add 5 hours)
        post_time = start_date + timedelta(days=post["day"], hours=post["hour"] + 5)
        schedule_iso = post_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Truncate display text
        preview = post["text"][:80].replace("\n", " ") + "..."

        print(f"\n[{i+1}/{len(POSTS)}] Day {post['day']+1} @ {post['hour']}:00 ET")
        print(f"  📝 {preview}")
        print(f"  🕐 Scheduled: {schedule_iso}")

        try:
            response = social.post({
                "post": post["text"],
                "platforms": PLATFORMS,
                "scheduleDate": schedule_iso,
            })

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
    print(f"🔄 After Day 10, re-run this script to schedule the next batch")

    return results


def post_now(index=0):
    """Post a single post immediately (for testing)."""
    post = POSTS[index]
    print(f"📤 Posting NOW: {post['text'][:80]}...")

    response = social.post({
        "post": post["text"],
        "platforms": PLATFORMS,
    })

    print(f"Response: {json.dumps(response, indent=2)}")
    return response


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        # Post immediately (for testing): python ayrshare_poster.py --now
        post_now(0)
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Dry run — just show the schedule
        start = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
        for i, post in enumerate(POSTS):
            post_time = start + timedelta(days=post["day"], hours=post["hour"])
            preview = post["text"][:60].replace("\n", " ")
            print(f"Day {post['day']+1} @ {post['hour']:02d}:00 | {preview}...")
    else:
        # Schedule everything
        schedule_all_posts()
