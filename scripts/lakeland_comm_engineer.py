import sys
import os
import requests
import json

# Add root directory to sys.path for module discovery
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.vault import SovereignVault

class CommEngineer:
    def __init__(self, business_name, industry, audit_findings):
        self.business_name = business_name
        self.industry = industry
        self.audit_findings = audit_findings # Dictionary of {check: status}
        self.local_name = "Dan" 
        self.vault = SovereignVault()

    def trigger_handshake(self):
        """Verify connection to the Bridge."""
        print(f"📡 Testing Sovereign Handshake with Bridge: {self.vault.BRIDGE_URL}...")
        url = f"{self.vault.BRIDGE_URL}/performance" # Using performance as a GET check
        headers = {"X-Sovereign-Token": self.vault.TOKEN}
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                print("✅ HANDSHAKE SUCCESSFUL: Bridge Connection Established.")
                return True
            else:
                print(f"❌ HANDSHAKE FAILED: HTTP {r.status_code} - {r.text}")
                return False
        except Exception as e:
            print(f"❌ HANDSHAKE ERROR: {e}")
            return False

    def generate_email(self):
        subject = f"[Urgent] Technical Health Audit for {self.business_name}"
        
        opening = f"Hi there,\n\nI’m a local developer here in Lakeland. I ran a quick health check on your website today to see how {self.business_name} looks to your customers."
        
        # ROI Insight Hook (National Competitor)
        competitor_hook = ""
        if "Pedro's" in self.business_name:
            competitor_hook = "\n\n**The ROI Leak:** Your site takes about 7 seconds to load. A national competitor like Tecta America takes only 3 seconds. Google says that 40% of people will leave your site if it takes longer than 3 seconds to load. You are losing customers to national firms every day."
        elif "Musick" in self.business_name:
            competitor_hook = "\n\n**The ROI Leak:** You are missing a valid Privacy Policy and your Lead Capture is failing. National competitors use automated systems to grab these leads while your site is leaking them."

        # The Table
        table_header = "Here is what I found (Status Check):"
        table_rows = []
        for check, status in self.audit_findings.items():
            emoji = "🔴" if status == "fail" else "🟡" if status == "warning" else "🟢"
            desc = self.get_readable_desc(check)
            table_rows.append(f"{emoji} {check}: {desc}")
            
        table_text = "\n".join(table_rows)
        
        so_what = "\n\n**What this means:** If you see any Red (🔴) dots, it means you are losing money right now because customers can't use your site properly."
        
        closing = f"\n\nI have a 10-minute fix ready for your {self.industry} site. I’ll call in an hour to see if you want it.\n\nBest,\n\n{self.local_name}\nLakeland, FL"
        
        full_body = f"{opening}{competitor_hook}\n\n{table_header}\n{table_text}{so_what}{closing}"
        
        return {"subject": subject, "body": full_body}

    def get_readable_desc(self, check):
        # 5th grade level explanations - NO JARGON
        jargon_map = {
            "Speed": "How fast your page loads so people don't leave.",
            "Security": "Keeping your site safe so it says 'Secure'.",
            "Lead Capture": "The form or button people use to talk to you.",
            "Broken Form": "The 'Contact Us' button is broken and not sending you emails.",
            "Privacy Policy": "The legal 'Trust' page required by Google and leads."
        }
        return jargon_map.get(check, "Status check.")

    def execute_outreach(self):
        """Draft the email and provide verification copy."""
        email = self.generate_email()
        print("\n" + "="*60)
        print("SOVEREIGN OUTREACH VERIFICATION COPY")
        print("="*60)
        print(f"TARGET: {self.business_name} ({self.industry})")
        print(f"SUBJECT: {email['subject']}")
        print("-" * 60)
        print(email['body'])
        print("="*60)
        
        # In a real scenario, this would POST to Bridge to trigger the actual email sending service
        # For this verification, we report the draft.
        return email

if __name__ == "__main__":
    # DIRECTIVE: Execute outreach for Pedro's Roofing and Musick Roofing
    leads = [
        {
            "name": "Pedro's Roofing",
            "industry": "Roofing",
            "findings": {
                "Speed": "fail",
                "Security": "pass",
                "Lead Capture": "fail"
            }
        },
        {
            "name": "Musick Roofing",
            "industry": "Roofing",
            "findings": {
                "Privacy Policy": "fail",
                "Speed": "fail",
                "Lead Capture": "warning"
            }
        }
    ]
    
    for lead_data in leads:
        engineer = CommEngineer(lead_data["name"], lead_data["industry"], lead_data["findings"])
        
        # 1. Verification Handshake
        if engineer.trigger_handshake():
            # 2. Generate and Report Verification Copy
            engineer.execute_outreach()
        else:
            print(f"❌ ABORTING for {lead_data['name']}: Cannot proceed without a valid Bridge Handshake.")
