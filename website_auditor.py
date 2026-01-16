"""
Real Website Audit Analyzer
Performs actual website analysis like Manus does:
- Page load speed
- Mobile-friendliness check
- SSL certificate check
- Contact info extraction
- Chat widget detection
- Booking system detection
"""
import requests
from bs4 import BeautifulSoup
import time
import ssl
import socket
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def check_ssl(domain):
    """Check if website has valid SSL certificate"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                return True
    except:
        return False

def check_mobile_friendly(soup):
    """Check for viewport meta tag (basic mobile check)"""
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    return viewport is not None

def check_page_speed(url):
    """Measure page load time"""
    try:
        start = time.time()
        resp = requests.get(url, headers=HEADERS, timeout=15)
        load_time = time.time() - start
        page_size = len(resp.content) / 1024  # KB
        return {
            "load_time": round(load_time, 2),
            "page_size_kb": round(page_size, 0),
            "status_code": resp.status_code
        }
    except Exception as e:
        return {"error": str(e)}

def check_chat_widget(soup, html_text):
    """Check for common chat widgets"""
    chat_indicators = [
        'drift', 'intercom', 'zendesk', 'livechat', 'tawk.to', 'crisp',
        'hubspot', 'olark', 'freshchat', 'tidio', 'chat-widget',
        'live-chat', 'messenger', 'whatsapp'
    ]
    html_lower = html_text.lower()
    for indicator in chat_indicators:
        if indicator in html_lower:
            return True
    return False

def check_booking_system(soup, html_text):
    """Check for online booking/scheduling"""
    booking_indicators = [
        'calendly', 'acuity', 'schedule', 'book online', 'book now',
        'schedule appointment', 'book appointment', 'housecall',
        'servicetitan', 'jobber', 'scheduling', 'booker'
    ]
    html_lower = html_text.lower()
    for indicator in booking_indicators:
        if indicator in html_lower:
            return True
    return False

def extract_contact_info(soup, html_text):
    """Extract phone and email from website"""
    import re
    
    # Phone patterns
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, html_text)
    
    # Email pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, html_text)
    
    # Filter out common non-business emails
    exclude = ['example', 'email.com', 'domain', 'your']
    emails = [e for e in emails if not any(ex in e.lower() for ex in exclude)]
    
    return {
        "phones_found": len(phones),
        "emails_found": len(emails),
        "phone": phones[0] if phones else None,
        "email": emails[0] if emails else None
    }

def check_social_media(soup):
    """Check for social media links"""
    social = {
        "facebook": False,
        "instagram": False,
        "twitter": False,
        "linkedin": False,
        "youtube": False
    }
    
    for link in soup.find_all('a', href=True):
        href = link.get('href', '').lower()
        if 'facebook.com' in href:
            social['facebook'] = True
        if 'instagram.com' in href:
            social['instagram'] = True
        if 'twitter.com' in href or 'x.com' in href:
            social['twitter'] = True
        if 'linkedin.com' in href:
            social['linkedin'] = True
        if 'youtube.com' in href:
            social['youtube'] = True
    
    return social

def analyze_website(url):
    """
    Perform full website audit
    Returns audit_data dict for premium_audit_generator
    """
    print(f"\n[AUDIT] Analyzing: {url}")
    results = {
        "website": url,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Parse domain
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path.split('/')[0]
    if not domain.startswith('www.'):
        domain = 'www.' + domain if '.' in domain else domain
    
    # 1. Check SSL
    print("  Checking SSL...")
    results["has_ssl"] = check_ssl(domain.replace('www.', ''))
    
    # 2. Check page speed
    print("  Checking page speed...")
    speed_data = check_page_speed(url)
    results.update(speed_data)
    
    # 3. Fetch and analyze page content
    print("  Fetching page content...")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        html_text = resp.text
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # 4. Mobile friendly
        results["mobile_friendly"] = check_mobile_friendly(soup)
        
        # 5. Chat widget
        results["has_chat"] = check_chat_widget(soup, html_text)
        
        # 6. Booking system
        results["has_booking"] = check_booking_system(soup, html_text)
        
        # 7. Contact info
        contact = extract_contact_info(soup, html_text)
        results.update(contact)
        
        # 8. Social media
        results["social_media"] = check_social_media(soup)
        
        # 9. Get page title
        title = soup.find('title')
        results["page_title"] = title.get_text(strip=True) if title else None
        
    except Exception as e:
        results["error"] = str(e)
    
    # Calculate scores
    results["online_score"] = calculate_online_score(results)
    results["seo_score"] = calculate_seo_score(results)
    results["automation_score"] = calculate_automation_score(results)
    
    return results

def calculate_online_score(data):
    """Calculate online presence score (0-100)"""
    score = 0
    if data.get("has_ssl"):
        score += 20
    if data.get("mobile_friendly"):
        score += 20
    if data.get("load_time", 10) < 3:
        score += 20
    social = data.get("social_media", {})
    if social.get("facebook"):
        score += 10
    if social.get("instagram"):
        score += 10
    if any(social.values()):
        score += 10
    if data.get("phones_found", 0) > 0:
        score += 10
    return min(score, 100)

def calculate_seo_score(data):
    """Calculate SEO score (0-100)"""
    score = 30  # Base score
    if data.get("page_title"):
        score += 20
    if data.get("has_ssl"):
        score += 15
    if data.get("mobile_friendly"):
        score += 15
    if data.get("load_time", 10) < 2:
        score += 20
    elif data.get("load_time", 10) < 4:
        score += 10
    return min(score, 100)

def calculate_automation_score(data):
    """Calculate automation score (0-100)"""
    score = 0
    if data.get("has_chat"):
        score += 40
    if data.get("has_booking"):
        score += 40
    if data.get("emails_found", 0) > 0:
        score += 10
    if data.get("phones_found", 0) > 0:
        score += 10
    return min(score, 100)

def format_for_premium_audit(audit_results, company_name):
    """
    Convert audit results to format expected by premium_audit_generator
    """
    return {
        "company_name": company_name,
        "website_url": audit_results.get("website"),
        "has_chat": audit_results.get("has_chat", False),
        "has_booking": audit_results.get("has_booking", False),
        "has_reviews": True,  # Assume they have some reviews
        "review_score": 4.2,  # Default - would need Places API for real
        "review_count": 47,
        "load_time": audit_results.get("load_time", 3.5),
        "mobile_score": 85 if audit_results.get("mobile_friendly") else 45,
        "seo_score": audit_results.get("seo_score", 50),
        "online_score": audit_results.get("online_score", 50),
        "automation_score": audit_results.get("automation_score", 30),
        "missed_calls_weekly": 12,  # Industry average estimate
        "avg_job_value": 450,
        "conversion_rate": 0.35
    }

if __name__ == "__main__":
    # Test with a real HVAC website
    test_urls = [
        "https://www.comforttemp.com",  # Real HVAC company
        "https://www.acprosfl.com"       # Another HVAC company
    ]
    
    for url in test_urls:
        results = analyze_website(url)
        print("\n--- AUDIT RESULTS ---")
        for key, value in results.items():
            print(f"  {key}: {value}")
        
        print("\n--- PREMIUM AUDIT FORMAT ---")
        premium = format_for_premium_audit(results, "Test HVAC Company")
        for key, value in premium.items():
            print(f"  {key}: {value}")
