
import glob
import os

PRICE_TEXT = "Get Started ($497/mo)"

def update_pricing():
    files = glob.glob("apps/portal/public/landing/*.html")
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Update any "Get Started..." button to standard
        # Heuristic: Replace "Get Started" inside <a> tags
        # Or specifically look for the button class
        
        if PRICE_TEXT in content:
            print(f"✅ {file} already has correct pricing.")
            continue
            
        # Try to find common patterns
        # 1. <a href="#" class="btn">Get Started</a> -> <a href="#" class="btn">Get Started ($497/mo)</a>
        # 2. <a href="#" class="cta-button">Start Free Trial</a> -> ...
        
        new_content = content.replace(">Get Started<", f">{PRICE_TEXT}<")
        new_content = new_content.replace(">Star Free Trial<", f">{PRICE_TEXT}<") # Typo in some templates?
        new_content = new_content.replace(">Start Free Trial<", f">{PRICE_TEXT}<")

        if new_content != content:
            with open(file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"🛠️ Updated Pricing in {file}")
        else:
            print(f"⚠️ Could not auto-update pricing in {file} (Pattern not found)")

if __name__ == "__main__":
    update_pricing()
