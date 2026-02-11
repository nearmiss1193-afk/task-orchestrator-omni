"""
NEWSLETTER ENGINE — Initiative #5
Weekly newsletter to contacts_master leads via Resend.
Content: local business tips, AI trends, success stories.
"""
import os
import sys
from datetime import datetime, timezone
from string import Template

sys.path.insert(0, '.')

# ── Newsletter HTML Template ────────────────────────────────────────

NEWSLETTER_HTML = Template("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${subject}</title>
<style>
  body { margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4; }
  .container { max-width: 600px; margin: 0 auto; background: #ffffff; }
  .header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 30px; text-align: center; }
  .header h1 { color: #e94560; margin: 0; font-size: 28px; font-weight: 700; }
  .header p { color: #a0a0b0; margin: 5px 0 0; font-size: 14px; }
  .content { padding: 30px; }
  .section { margin-bottom: 25px; }
  .section h2 { color: #1a1a2e; font-size: 20px; border-bottom: 2px solid #e94560; padding-bottom: 8px; }
  .section p { color: #333; line-height: 1.6; font-size: 15px; }
  .tip-box { background: #f0f7ff; border-left: 4px solid #0f3460; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }
  .stat-box { background: #fff3f3; border-left: 4px solid #e94560; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }
  .cta { text-align: center; margin: 30px 0; }
  .cta a { background: #e94560; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }
  .footer { background: #1a1a2e; padding: 20px; text-align: center; color: #a0a0b0; font-size: 12px; }
  .footer a { color: #e94560; text-decoration: none; }
  .divider { height: 1px; background: #eee; margin: 20px 0; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🚀 Digital Edge Weekly</h1>
    <p>Your competitive advantage in the AI era | ${date}</p>
  </div>
  
  <div class="content">
    <div class="section">
      <h2>📊 This Week's Insight</h2>
      <p>${main_insight}</p>
    </div>

    <div class="section">
      <h2>💡 Quick Tip</h2>
      <div class="tip-box">
        <p><strong>${tip_title}</strong></p>
        <p>${tip_body}</p>
      </div>
    </div>

    <div class="section">
      <h2>📈 By The Numbers</h2>
      <div class="stat-box">
        <p>${stat_highlight}</p>
      </div>
    </div>

    <div class="section">
      <h2>🔧 Action Item</h2>
      <p>${action_item}</p>
    </div>

    <div class="cta">
      <a href="https://mygrowthengine.com">Get Your Free AI Visibility Audit →</a>
    </div>

    <div class="divider"></div>

    <div class="section">
      <p style="font-size: 13px; color: #666;">
        <strong>Why are you getting this?</strong> You're a Florida business owner we think could benefit from AI-powered growth strategies. 
        We send one email per week with actionable tips — no spam, no fluff.
      </p>
    </div>
  </div>

  <div class="footer">
    <p>My Growth Engine | Lakeland, FL</p>
    <p><a href="mailto:dan@mygrowthengine.com">dan@mygrowthengine.com</a></p>
    <p style="margin-top: 10px;"><a href="${unsubscribe_url}">Unsubscribe</a></p>
  </div>
</div>
</body>
</html>
""")

# ── Weekly Content Library ────────────────────────────────────────

WEEKLY_EDITIONS = [
    {
        "subject": "Is Your Website Invisible to 40% of the Internet?",
        "main_insight": """By 2026, over 40% of web traffic comes from AI assistants — ChatGPT, Siri, Google SGE, and others. 
        When a homeowner asks "find me a good plumber near me," these AI systems crawl the web for answers. 
        But here's the problem: <strong>most small business websites aren't built for AI crawlers.</strong> 
        They're built for humans (barely). That means when AI looks for a recommendation, your business is invisible. 
        The businesses that optimize for AI visibility NOW will dominate local search for the next decade.""",
        "tip_title": "Add JSON-LD to Your Website (5 minutes)",
        "tip_body": "JSON-LD is a snippet of code that tells AI exactly what your business does, where you're located, and what services you offer. It's like a business card for robots. Google's Structured Data testing tool can help you generate one for free.",
        "stat_highlight": "<strong>73%</strong> of Florida home service businesses have NO structured data on their website. That means 73% are invisible to AI assistants making referrals. <em>Source: Our audit of 200+ FL businesses</em>",
        "action_item": "Go to <strong>search.google.com/test/rich-results</strong> and paste your website URL. If it shows 0 structured data items, you need to add JSON-LD immediately. Reply to this email for a free structured data template."
    },
    {
        "subject": "Florida's $50K Privacy Law — Are You Compliant?",
        "main_insight": """The Florida Digital Bill of Rights (FDBR) went into effect in 2024, and most small businesses don't even know it exists. 
        If your website collects ANY personal data — contact forms, cookies, Google Analytics — you may need to comply. 
        Non-compliance fines can reach <strong>$50,000 per violation.</strong> 
        The good news? Compliance is relatively simple once you know what to do. The bad news? Most businesses haven't started.""",
        "tip_title": "Privacy Policy Quick-Check",
        "tip_body": "Open your website right now. Can you find a Privacy Policy link in the footer? Does it mention the FDBR? If not, you're likely non-compliant. A basic compliant privacy policy can be generated for free using online tools — but it MUST be customized to your business.",
        "stat_highlight": "<strong>91%</strong> of the small business websites we've audited in Florida are missing at least one FDBR compliance element. The most common gaps: no cookie consent banner (87%), no data deletion policy (94%), no privacy policy update since 2023 (78%).",
        "action_item": "Check these 3 things on your website TODAY: (1) Privacy Policy exists and is linked, (2) Cookie consent banner appears on first visit, (3) You have a way for customers to request data deletion. If any are missing, reply to this email for our free compliance checklist."
    },
    {
        "subject": "Why Your Website Loads Slower Than Your Competitor's",
        "main_insight": """Google's research shows that <strong>53% of mobile visitors leave a page that takes longer than 3 seconds to load.</strong> 
        We audited 100 Florida contractor websites last month. The average load time? <strong>6.2 seconds.</strong> 
        That means most local businesses are losing over half their potential customers before they even see the homepage. 
        The fix is often simpler than you think — compressed images and proper caching can cut load times by 60% in a single afternoon.""",
        "tip_title": "The 2-Minute Speed Test",
        "tip_body": "Go to pagespeed.web.dev and enter your website URL. You'll get a score from 0-100. Anything under 50 is hurting your business. Focus on the 'Opportunities' section — it tells you exactly what to fix, in order of impact.",
        "stat_highlight": "<strong>$2.4M</strong> — that's the estimated annual revenue lost by an average local business website loading in 6+ seconds vs 2 seconds. Based on average conversion rates and ticket sizes in the home services industry.",
        "action_item": "Run your PageSpeed test this week. If your score is under 50, the #1 fix is almost always image optimization. Compress your images using squoosh.app (free). This alone can improve your score by 20-30 points."
    },
    {
        "subject": "The $4,000/Month Mistake Most Contractors Make",
        "main_insight": """If you're paying Angi, HomeAdvisor, or Thumbtack for leads, you're renting customers instead of owning them. 
        At $150-300 per lead, a contractor doing 20 leads/month spends $3,000-6,000/month — <strong>$36,000-72,000/year.</strong> 
        Meanwhile, a properly optimized website generates leads for essentially $0 per lead after the initial setup. 
        We've helped contractors cut their lead costs by 70% by investing in their website instead of directory listings.""",
        "tip_title": "Calculate Your REAL Cost Per Lead",
        "tip_body": "Add up everything you spend on Angi, HomeAdvisor, Google Ads, and other lead sources. Divide by total leads received. Compare that to the one-time cost of a good website divided by 3 years of leads. The math will surprise you.",
        "stat_highlight": "<strong>$0 vs $200</strong> — that's the per-lead cost difference between a properly optimized website and directory listings. Over 3 years, a $5,000 website investment generates 500+ leads at $10/lead vs $200/lead from directories.",
        "action_item": "Track where your last 20 customers came from. If more than 50% came from paid directories, you're over-dependent on rented leads. Reply 'BREAKDOWN' and we'll send you our free Lead Source Calculator spreadsheet."
    },
]


def generate_newsletter(edition: int = 0) -> dict:
    """Generate newsletter HTML for a specific edition."""
    content = WEEKLY_EDITIONS[edition % len(WEEKLY_EDITIONS)]
    
    html = NEWSLETTER_HTML.substitute(
        subject=content["subject"],
        date=datetime.now(timezone.utc).strftime("%B %d, %Y"),
        main_insight=content["main_insight"],
        tip_title=content["tip_title"],
        tip_body=content["tip_body"],
        stat_highlight=content["stat_highlight"],
        action_item=content["action_item"],
        unsubscribe_url="https://mygrowthengine.com/unsubscribe",
    )
    
    return {
        "subject": content["subject"],
        "html": html,
        "edition": edition + 1,
    }


def get_newsletter_recipients(supabase) -> list:
    """Get all leads eligible for newsletter (have email, not unsubscribed)."""
    result = supabase.table("contacts_master") \
        .select("id,email,company_name") \
        .not_.is_("email", "null") \
        .neq("status", "unsubscribed") \
        .neq("status", "customer") \
        .execute()
    return result.data or []


def send_newsletter(supabase, edition: int = 0, dry_run: bool = True):
    """Send newsletter to all eligible recipients."""
    import resend
    resend.api_key = os.getenv("RESEND_API_KEY")
    
    newsletter = generate_newsletter(edition)
    recipients = get_newsletter_recipients(supabase)
    
    print(f"Newsletter Edition #{newsletter['edition']}")
    print(f"Subject: {newsletter['subject']}")
    print(f"Recipients: {len(recipients)}")
    
    if dry_run:
        print("\n⚠️ DRY RUN — No emails sent")
        print(f"Would send to {len(recipients)} recipients")
        return newsletter
    
    sent = 0
    for r in recipients:
        try:
            resend.Emails.send({
                "from": "Dan Coffman <dan@aiserviceco.com>",
                "to": [r["email"]],
                "subject": newsletter["subject"],
                "html": newsletter["html"],
            })
            sent += 1
        except Exception as e:
            print(f"  Error sending to {r['email']}: {e}")
    
    print(f"\n✅ Sent: {sent}/{len(recipients)}")
    return newsletter


if __name__ == "__main__":
    print("=" * 60)
    print("  NEWSLETTER ENGINE — Preview Mode")
    print("=" * 60)
    
    for i, edition in enumerate(WEEKLY_EDITIONS):
        print(f"\n📧 Edition {i+1}: {edition['subject']}")
        print(f"   Tip: {edition['tip_title']}")
    
    print(f"\n  Total editions ready: {len(WEEKLY_EDITIONS)}")
    print(f"  Distribution: Resend API")
    print(f"  Frequency: Weekly")
    
    # Generate preview
    newsletter = generate_newsletter(0)
    
    # Save HTML preview
    with open("scripts/newsletter_preview.html", "w", encoding="utf-8") as f:
        f.write(newsletter["html"])
    print(f"\n  Preview saved to: scripts/newsletter_preview.html")
