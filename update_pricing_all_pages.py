"""
update_pricing_all_pages.py
============================
Updates all landing pages to match the Golden Standard pricing:
- Starter: $297/mo
- Growth: $497/mo
- Scale: $997/mo
- Trial Period: 14 days (not 7)

This script performs bulk find/replace across all HTML files in public/.
"""

import os
import re
from pathlib import Path

PUBLIC_DIR = Path(__file__).parent / "public"

# Patterns to replace
REPLACEMENTS = [
    # Trial period
    ("7-Day Trial", "14-Day Trial"),
    ("7-Day Free Trial", "14-Day Free Trial"),
    ("7 Day Trial", "14-Day Trial"),
    
    # Starter pricing (was $99, now $297)
    (r'\$99<span', r'$297<span'),
    (r'\$99</span>', r'$297</span>'),
    (r'>$99<', '>$297<'),
    (r'"$99"', '"$297"'),
    (r"'$99'", "'$297'"),
    (r'$99/mo', '$297/mo'),
    
    # Lite/Middle pricing (was $199, now $497)
    (r'\$199<span', r'$497<span'),
    (r'\$199</span>', r'$497</span>'),
    (r'>$199<', '>$497<'),
    (r'"$199"', '"$497"'),
    (r"'$199'", "'$497'"),
    (r'$199/mo', '$497/mo'),
   
    # Growth pricing (was $297, now $997  - the old "growth" at $297 was actually what we now call scale)
    # WAIT - Brain says: Starter $297, Growth $497, Scale $997
    # So if page shows $99/$199/$297, that maps to:
    # $99 -> $297 (Starter)
    # $199 -> $497 (Growth) 
    # $297 -> $997 (Scale)
    (r'\$297/mo</span>', r'$997/mo</span>'),
    
    # Old strikethrough prices need updating too
    (r'<span class="original">$199</span>', r'<span class="original">$594</span>'),  # "was" price
    (r'<span class="original">$399</span>', r'<span class="original">$994</span>'),  # "was" price
    (r'<span class="original">$597</span>', r'<span class="original">$1994</span>'),  # "was" price
]

def update_file(filepath):
    """Update a single file with the new pricing."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = 0
    
    for old, new in REPLACEMENTS:
        if old in content:
            content = content.replace(old, new)
            changes += content.count(new) - original.count(new)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🔄 Updating All Landing Pages to Golden Standard Pricing")
    print("=" * 60)
    print("Target Pricing:")
    print("  - Starter: $297/mo")
    print("  - Growth: $497/mo")
    print("  - Scale: $997/mo")
    print("  - Trial: 14 Days")
    print("=" * 60)
    
    updated = []
    for filepath in PUBLIC_DIR.glob("*.html"):
        if update_file(filepath):
            updated.append(filepath.name)
            print(f"✅ Updated: {filepath.name}")
    
    if updated:
        print(f"\n📝 {len(updated)} files updated:")
        for f in updated:
            print(f"   - {f}")
        print("\n🚀 Run 'npx vercel --prod' to deploy changes.")
    else:
        print("❌ No files needed updates.")

if __name__ == "__main__":
    main()
