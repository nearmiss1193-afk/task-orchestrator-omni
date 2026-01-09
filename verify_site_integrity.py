
import os
import re
import glob
from pathlib import Path
from bs4 import BeautifulSoup

# Configuration
TARGET_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\public"
ALLOWED_PHONES = ["+1 (352) 758-5336", "+13527585336", "352-758-5336", "1-352-758-5336"]
LEGACY_PHONES = ["863-213-2505", "863.213.2505", "(863) 213-2505", "+18632132505", "863-260-5336", "(863) 260-5336"]
PHONE_REGEX = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"

def verify_file(file_path):
    print(f"Checking {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    
    issues = []

    # 1. Phone Number Check
    phones_found = re.findall(PHONE_REGEX, text)
    for phone in phones_found:
        # Normalize simple check
        norm_phone = re.sub(r'\D', '', phone)
        # Check if it looks like a legacy number (starts with 863)
        if phone.startswith("(863)") or phone.startswith("863"):
             issues.append(f"Legacy number found: {phone}")
        
    # 2. Check specific strings
    for leg in LEGACY_PHONES:
         if leg in content:
             issues.append(f"Hardcoded legacy string found: {leg}")

    # 3. Link Check (Basic) - Looking for tel: links
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('tel:'):
            # 863 check
            if '863' in href:
                 issues.append(f"Legacy tel link found: {href}")

    return issues

def main():
    print("=== SITE INTEGRITY AGENT ===")
    print(f"Target Directory: {TARGET_DIR}")
    
    if not os.path.exists(TARGET_DIR):
        print(f"Error: Target directory {TARGET_DIR} does not exist.")
        return

    html_files = glob.glob(os.path.join(TARGET_DIR, "*.html"))
    if not html_files:
        print("No HTML files found.")
        return

    all_issues = {}
    
    for file in html_files:
        file_issues = verify_file(file)
        if file_issues:
            all_issues[file] = file_issues

    print("\n=== REPORT ===")
    if not all_issues:
        print("✅ No issues found. Site is clean.")
    else:
        print(f"❌ Issues found in {len(all_issues)} files:")
        for f, errs in all_issues.items():
            print(f"\n📄 {os.path.basename(f)}:")
            for e in errs:
                print(f"  - {e}")
                
if __name__ == "__main__":
    main()
