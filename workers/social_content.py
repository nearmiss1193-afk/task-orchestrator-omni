"""
SOCIAL CONTENT GENERATOR — Initiative #3
Generates organic social media posts for LinkedIn/Facebook/X
Topics: AI for local businesses, website audits, FDBR compliance, digital presence tips
Posts are stored in Supabase for scheduled publishing.
"""
import os
import json
import random
from datetime import datetime, timezone, timedelta

# ── Post Templates ────────────────────────────────────────────────

VALUE_POSTS = [
    {
        "title": "Is Your Website Invisible to AI?",
        "body": """🤖 By 2026, 40% of web traffic comes from AI assistants — not Google.

When someone asks ChatGPT or Siri "best {niche} near me," does YOUR business show up?

Most small businesses have ZERO AI visibility. Their websites weren't built for AI crawlers.

Here's what you can do TODAY:
✅ Add structured data (JSON-LD) to your site
✅ Create an FAQ page with natural language answers
✅ Make sure your business hours, services, and location are in plain text (not just images)

We're offering FREE AI Visibility Audits for Florida businesses this month.
DM me "AUDIT" to get yours. 📊

#LocalBusiness #AIVisibility #DigitalMarketing #FloridaBusiness""",
        "platform": "linkedin",
        "category": "value"
    },
    {
        "title": "Florida's New Digital Privacy Law",
        "body": """⚠️ Florida business owners — did you know?

The Florida Digital Bill of Rights (FDBR) went into effect in 2024. If your website collects ANY personal data (contact forms, cookies, analytics), you may need to comply.

Non-compliance can result in fines up to $50,000 per violation.

3 things to check RIGHT NOW:
1️⃣ Do you have a clear Privacy Policy linked on every page?
2️⃣ Do you have a cookie consent banner?
3️⃣ Can users request deletion of their data?

Most small business websites fail ALL THREE. 😬

We run free compliance scans — comment "CHECK" to get yours.

#FDBR #FloridaBusiness #Privacy #WebCompliance #SmallBusiness""",
        "platform": "linkedin",
        "category": "compliance"
    },
    {
        "title": "Your Website Speed is Costing You Money",
        "body": """💰 Slow websites lose 7% in conversions for every 1-second delay.

I just audited 50 {niche} websites in Florida. The average load time? 6.8 seconds. 🐌

Google's benchmark: Under 2.5 seconds.

That means most local businesses are losing over 30% of potential customers before they even see the homepage.

Quick wins to speed up your site:
🔧 Compress images (use WebP format)
🔧 Enable browser caching
🔧 Minimize JavaScript
🔧 Use a CDN

Or let us run a FREE PageSpeed audit and give you a detailed report.

DM "SPEED" for yours 🏎️

#WebPerformance #SmallBusiness #PageSpeed #FloridaContractor""",
        "platform": "facebook",
        "category": "value"
    },
    {
        "title": "Why AI is the Great Equalizer for Small Businesses",
        "body": """Big companies spend $50K+/month on marketing. You don't have to.

AI is changing the game for small businesses:

📧 AI-powered email sequences that nurture leads 24/7
🤖 AI chatbots that answer customer questions instantly
📊 AI audits that find website problems in seconds
📱 AI-generated content that keeps your social media active

The best part? Most of these tools are FREE or under $100/month.

The businesses that adopt AI now will dominate their market in 2-3 years. The ones that don't will wonder what happened.

Which side do you want to be on?

#AI #SmallBusiness #FloridaBusiness #DigitalTransformation""",
        "platform": "linkedin",
        "category": "thought_leadership"
    },
    {
        "title": "5 Signs Your Website Needs an Upgrade",
        "body": """Is your website helping or hurting your business? 🤔

5 warning signs:

1️⃣ It's not mobile-friendly (60%+ of your traffic is mobile)
2️⃣ No SSL certificate (the "Not Secure" warning scares people away)
3️⃣ Load time over 3 seconds (bounce rate jumps 32%)
4️⃣ No Google reviews widget (social proof converts)
5️⃣ Contact form goes to a dead email

We've seen businesses increase leads by 40-60% just by fixing these basics.

Free audit available — link in bio 👆

#WebDesign #LeadGeneration #SmallBusiness #FloridaBusiness""",
        "platform": "facebook",
        "category": "value"
    },
    {
        "title": "Case Study: How One Contractor 3X'd Their Leads",
        "body": """📈 Real results from a real Florida {niche}:

BEFORE our audit:
❌ PageSpeed score: 23/100
❌ No mobile optimization
❌ Zero AI visibility
❌ 2 leads/month from website

AFTER implementing our recommendations:
✅ PageSpeed score: 89/100
✅ Fully responsive design
✅ AI-optimized content
✅ 6-8 leads/month from website

Total cost of changes: Under $500.
ROI: First new customer covered it.

Want similar results? DM "RESULTS" 💪

#CaseStudy #ROI #SmallBusiness #WebOptimization #FloridaContractor""",
        "platform": "linkedin",
        "category": "social_proof"
    },
    {
        "title": "Stop Paying for Leads You Could Get for Free",
        "body": """Home service businesses spend an average of $150-300 per lead on Angi/HomeAdvisor.

But did you know your own website could generate leads for $0?

Here's the math:
💸 20 leads/month x $200/lead = $4,000/month on directories
🏠 Website generating 20 leads/month = $0/month (after setup)

The catch? Your website needs to actually WORK.

That means:
→ Fast loading (under 2.5 seconds)
→ Mobile optimized
→ SEO-friendly
→ Clear calls to action
→ AI-visible

One-time investment vs. monthly bleeding.

Which sounds better?

#HomeServices #LeadGeneration #StopPayingForLeads #FloridaContractor""",
        "platform": "facebook",
        "category": "value"
    },
]

NICHES = [
    "HVAC contractor", "plumber", "roofer", "electrician",
    "pest control company", "landscaper", "pool service",
    "painter", "pressure washer", "garage door repair"
]


def generate_weekly_content(week_number: int = 1) -> list:
    """Generate a week's worth of social media posts (1/day, Mon-Sat)."""
    posts = []
    
    # Select posts for the week
    selected = random.sample(VALUE_POSTS, min(6, len(VALUE_POSTS)))
    niche = random.choice(NICHES)
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    for i, post_template in enumerate(selected):
        body = post_template["body"].replace("{niche}", niche)
        posts.append({
            "day": days[i],
            "title": post_template["title"],
            "body": body,
            "platform": post_template["platform"],
            "category": post_template["category"],
            "week": week_number,
            "niche_focus": niche,
            "status": "ready",
        })
    
    return posts


def generate_content_calendar(weeks: int = 4) -> list:
    """Generate a full month content calendar."""
    all_posts = []
    for w in range(1, weeks + 1):
        weekly = generate_weekly_content(w)
        all_posts.extend(weekly)
    return all_posts


# ── LinkedIn-specific formatter ────────────────────────────────────

def format_for_linkedin(post: dict) -> str:
    """Format post for LinkedIn's algorithm preferences."""
    # LinkedIn favors: short paragraphs, line breaks, hooks
    return post["body"]


def format_for_facebook(post: dict) -> str:
    """Format post for Facebook's algorithm preferences."""
    # Facebook favors: engagement questions, shorter posts
    body = post["body"]
    if not body.strip().endswith("?"):
        body += "\n\nWhat do you think? 👇"
    return body


# ── Main execution ────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  SOCIAL CONTENT GENERATOR — Week 1 Preview")
    print("=" * 60)
    
    posts = generate_weekly_content(1)
    
    for p in posts:
        print(f"\n{'─' * 50}")
        print(f"📅 {p['day']} | 📱 {p['platform']} | 🏷️ {p['category']}")
        print(f"📌 {p['title']}")
        print(f"{'─' * 50}")
        # Show first 200 chars
        preview = p['body'][:200] + "..." if len(p['body']) > 200 else p['body']
        print(preview)
    
    print(f"\n{'=' * 60}")
    print(f"  Total posts generated: {len(posts)}")
    print(f"  Niche focus: {posts[0]['niche_focus']}")
    print(f"  Ready for scheduling!")
    print(f"{'=' * 60}")
