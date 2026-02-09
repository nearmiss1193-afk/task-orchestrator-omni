
import os
import re

files_to_fix = [
    "index.html", "hvac.html", "plumbing.html", "roofer.html", 
    "electrician.html", "pest.html", "landscaping.html", 
    "autodetail.html", "cleaning.html", "solar.html", 
    "plumber.html", "restoration.html", "intake.html"
]

target_dir = "public"

human_block = """
            <div class="style-fix-30" data-style-migrated="true" style="margin-top: 20px; padding: 15px; background: rgba(212, 175, 55, 0.1); border-radius: 12px; border: 1px solid rgba(212, 175, 55, 0.3);">
                <div style="margin-bottom: 8px;"><strong>👨‍💼 Talk to Dan (Human/Owner):</strong> <a href="tel:+13529368152" style="color: #d4af37; font-weight: bold; text-decoration: none;">+1 (352) 936-8152</a></div>
            </div>
"""

for filename in files_to_fix:
    filepath = os.path.join(target_dir, filename)
    if not os.path.exists(filepath):
        continue
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Clean up double quotes from previous failed script
    content = content.replace('""style-fix-30""', '"style-fix-30"')
    content = content.replace('""true""', '"true"')
    content = content.replace('""margin-top: 20px; padding: 15px; background: rgba(212, 175, 55, 0.1); border-radius: 12px; border: 1px solid rgba(212, 175, 55, 0.3);""', '"margin-top: 20px; padding: 15px; background: rgba(212, 175, 55, 0.1); border-radius: 12px; border: 1px solid rgba(212, 175, 55, 0.3);"')
    content = content.replace('""margin-bottom: 8px;""', '"margin-bottom: 8px;"')
    content = content.replace('""tel:+13529368152""', '"tel:+13529368152"')
    content = content.replace('""color: #d4af37; font-weight: bold; text-decoration: none;""', '"color: #d4af37; font-weight: bold; text-decoration: none;"')
    
    # Ensure human contact block exists and is correct
    if "352-936-8152" not in content:
        if "</h1>" in content:
            content = content.replace("</h1>", f"</h1>\n{human_block}")
    
    # Fix the secondary contact line if it exists (the one with Sarah numbers)
    # Target: "Call Sarah (Voice AI): +1 (863) 213-2505 | Text Sarah: +1 (863) 213-2505"
    # To: "Call Sarah (Voice AI): +1 (863) 213-2505 | Text Sarah: +1 (352) 758-5336 | Human: +1 (352) 936-8152"
    
    # Pattern seen in screenshot: Call Sarah (Voice AI): +1 (863) 213-2505 | Text Sarah: +1 (863) 213-2505
    content = re.sub(r'Text Sarah: \+1 \(863\) 213-2505', 'Text Sarah: +1 (352) 758-5336', content)
    
    # Platform Link Fix: dashboard.html -> #contact (Live Site doesn't have a local dashboard)
    content = content.replace('dashboard.html', '#contact')
    content = content.replace('http://localhost:3000', '#contact')

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Finished fixing HTML files.")
