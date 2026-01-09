"""
Check Email Inbox for Prospect Replies
Uses Gmail API with existing credentials to check for replies to outreach emails.
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Gmail API configuration (simplified check using Resend webhooks pattern)
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "owner@aiserviceco.com")
GHL_EMAIL = os.getenv("GHL_EMAIL", "nearmiss1193@gmail.com")


def check_resend_replies() -> dict:
    """
    Check Resend for email activity.
    Note: Resend doesn't store replies - they go to your inbox.
    This checks for delivery status and opens.
    """
    resend_key = os.getenv("RESEND_API_KEY")
    if not resend_key:
        return {"error": "RESEND_API_KEY not configured"}
    
    try:
        # Get recent emails sent
        response = requests.get(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_key}"}
        )
        
        if response.status_code == 200:
            emails = response.json().get("data", [])
            
            # Summarize
            summary = {
                "total_sent": len(emails),
                "recent_7_days": 0,
                "by_status": {},
                "recent_emails": []
            }
            
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            
            for email in emails[:50]:
                status = email.get("status", "unknown")
                summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
                
                if email.get("created_at", "") > week_ago:
                    summary["recent_7_days"] += 1
                    summary["recent_emails"].append({
                        "to": email.get("to", ["?"])[0] if isinstance(email.get("to"), list) else email.get("to"),
                        "subject": email.get("subject", ""),
                        "status": status,
                        "created": email.get("created_at", "")[:16]
                    })
            
            return summary
        else:
            return {"error": f"API error: {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}


def check_gmail_inbox() -> dict:
    """
    Placeholder for Gmail API integration.
    Requires OAuth flow which needs user interaction.
    
    For now, returns manual check instructions.
    """
    return {
        "message": "Gmail API requires OAuth setup",
        "manual_check": [
            f"1. Open Gmail for {GHL_EMAIL}",
            "2. Search: 'from:*@* subject:(HVAC OR AI OR phone) newer_than:7d'",
            "3. Look for replies to your outreach emails",
            "4. Check spam folder too!"
        ],
        "alternative": "Set up email forwarding to catch replies automatically"
    }


def get_email_summary() -> dict:
    """Get summary of email activity"""
    print("="*60)
    print("EMAIL ACTIVITY SUMMARY")
    print("="*60)
    
    # Check Resend
    print("\n📧 RESEND (Outbound Emails):")
    resend_data = check_resend_replies()
    
    if "error" in resend_data:
        print(f"  Error: {resend_data['error']}")
    else:
        print(f"  Total sent: {resend_data.get('total_sent', 0)}")
        print(f"  Last 7 days: {resend_data.get('recent_7_days', 0)}")
        print(f"  By status:")
        for status, count in resend_data.get("by_status", {}).items():
            print(f"    {status}: {count}")
    
    # Gmail instructions
    print("\n📥 TO CHECK REPLIES:")
    gmail_info = check_gmail_inbox()
    for instruction in gmail_info.get("manual_check", []):
        print(f"  {instruction}")
    
    print("\n" + "="*60)
    
    return {
        "resend": resend_data,
        "gmail": gmail_info
    }


if __name__ == "__main__":
    get_email_summary()
