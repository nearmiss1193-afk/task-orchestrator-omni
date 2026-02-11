"""Generate Week 1 social media posts and save to file for publishing."""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'workers')
from social_content import generate_weekly_content

def generate_and_save():
    print("=" * 60)
    print("  SOCIAL MEDIA — Week 1 Content")
    print("=" * 60)
    
    posts = generate_weekly_content(week_number=1)
    
    # Save as ready-to-post text files
    for i, p in enumerate(posts):
        filename = f"scripts/social_post_w1_{i+1}_{p['day'].lower()}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"PLATFORM: {p['platform'].upper()}\n")
            f.write(f"DAY: {p['day']}\n")
            f.write(f"CATEGORY: {p['category']}\n")
            f.write(f"NICHE FOCUS: {p['niche_focus']}\n")
            f.write(f"{'=' * 50}\n\n")
            f.write(p['body'])
        
        print(f"\n{'─' * 50}")
        print(f"📅 {p['day']} | 📱 {p['platform'].upper()} | 🏷️ {p['category']}")
        print(f"📌 {p['title']}")
        preview = p['body'][:150].replace('\n', ' ') + "..."
        print(f"   {preview}")
        print(f"   📄 Saved to: {filename}")
    
    print(f"\n{'=' * 60}")
    print(f"  {len(posts)} posts generated and saved!")
    print(f"  Ready for manual posting to LinkedIn/Facebook")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    generate_and_save()
