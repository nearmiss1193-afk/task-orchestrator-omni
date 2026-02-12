"""
Email scraper for Lakeland businesses.
Visits each business website, extracts email addresses from the page.
Saves results to lakeland_emails.csv
"""
import csv, re, json, time, os, random
import requests
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

# Email regex pattern
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')

# Common false-positive patterns to exclude
EXCLUDE_EMAILS = {
    'example.com', 'domain.com', 'email.com', 'yoursite.com', 
    'sample.com', 'test.com', 'sentry.io', 'wixpress.com',
    'googleapis.com', 'schema.org', 'w3.org', 'wordpress.org',
    'wordpress.com', 'gravatar.com', 'google.com', 'facebook.com',
    'squarespace.com', 'godaddy.com', 'wix.com', 'weebly.com',
    'cloudflare.com', 'jsdelivr.net', 'jquery.com', 'bootstrap.com',
}

def is_valid_email(email):
    """Filter out false positives"""
    email = email.lower().strip()
    # Skip images and common non-email patterns
    if any(email.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js']):
        return False
    domain = email.split('@')[1] if '@' in email else ''
    if domain in EXCLUDE_EMAILS:
        return False
    if len(email) > 60 or len(email) < 5:
        return False
    return True

def scrape_emails_from_url(url, timeout=8):
    """Try to find email addresses on a webpage"""
    emails = set()
    try:
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Try main page
        r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            found = EMAIL_RE.findall(r.text)
            for e in found:
                if is_valid_email(e):
                    emails.add(e.lower())
        
        # Try /contact page if no emails found
        if not emails:
            parsed = urlparse(r.url)
            for path in ['/contact', '/contact-us', '/about', '/about-us']:
                try:
                    contact_url = f"{parsed.scheme}://{parsed.netloc}{path}"
                    r2 = requests.get(contact_url, headers=headers, timeout=timeout, allow_redirects=True)
                    if r2.status_code == 200:
                        found = EMAIL_RE.findall(r2.text)
                        for e in found:
                            if is_valid_email(e):
                                emails.add(e.lower())
                    if emails:
                        break
                except:
                    continue
    except Exception as e:
        pass  # Skip failed URLs silently
    
    return list(emails)

def process_business(row, idx):
    """Process a single business"""
    name = row.get('name', 'Unknown')
    website = row.get('website', '')
    
    if not website:
        return {'idx': idx, 'name': name, 'website': '', 'emails': [], 'status': 'no_website'}
    
    emails = scrape_emails_from_url(website)
    status = 'found' if emails else 'no_email'
    
    return {
        'idx': idx, 
        'name': name, 
        'website': website, 
        'emails': emails,
        'status': status
    }

def main():
    # Load expanded CSV
    csv_path = r'c:\Users\nearm\.gemini\antigravity\scratch\lakeland-local-prod\scripts\lakeland_businesses_expanded.csv'
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        businesses = list(reader)
    
    print(f"Loaded {len(businesses)} businesses")
    print(f"With websites: {sum(1 for b in businesses if b.get('website'))}")
    
    # Filter to those with websites
    with_websites = [b for b in businesses if b.get('website')]
    
    results = []
    found_count = 0
    processed = 0
    
    # Use thread pool for parallel scraping (10 threads)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(process_business, biz, i): i 
            for i, biz in enumerate(with_websites)
        }
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            processed += 1
            
            if result['status'] == 'found':
                found_count += 1
            
            # Progress update every 100
            if processed % 100 == 0:
                print(f"  Processed {processed}/{len(with_websites)} | Found emails: {found_count}")
    
    # Sort by original index
    results.sort(key=lambda x: x['idx'])
    
    # Save results
    output_path = r'c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\scripts\lakeland_emails.csv'
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'website', 'email', 'all_emails'])
        
        for r in results:
            if r['emails']:
                primary = r['emails'][0]
                all_emails = ';'.join(r['emails'])
            else:
                primary = ''
                all_emails = ''
            writer.writerow([r['name'], r['website'], primary, all_emails])
    
    # Also save the enriched full dataset
    enriched_path = r'c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\scripts\lakeland_businesses_enriched.csv'
    with open(enriched_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'address', 'category', 'phone', 'website', 'email', 'rating', 'total_ratings', 'place_id'])
        
        email_map = {r['name']: r['emails'] for r in results if r['emails']}
        
        for biz in businesses:
            name = biz.get('name', '')
            emails = email_map.get(name, [])
            email = emails[0] if emails else ''
            writer.writerow([
                name,
                biz.get('address', ''),
                biz.get('category', ''),
                biz.get('phone', ''),
                biz.get('website', ''),
                email,
                biz.get('rating', ''),
                biz.get('total_ratings', ''),
                biz.get('place_id', '')
            ])
    
    print(f"\n=== RESULTS ===")
    print(f"Total businesses: {len(businesses)}")
    print(f"With websites: {len(with_websites)}")
    print(f"Emails found: {found_count}")
    print(f"Hit rate: {found_count/len(with_websites)*100:.1f}%")
    print(f"\nSaved to: {output_path}")
    print(f"Enriched CSV: {enriched_path}")

if __name__ == '__main__':
    main()
