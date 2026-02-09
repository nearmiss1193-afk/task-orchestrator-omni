"""
Send FULL email drafts to Dan for approval via GHL webhook (Priority 1)
Per operational_memory.md: GHL first, Gmail second, Resend last
"""
import requests

GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/uKaqY2KaULkCeMHM7wmt"

html = """
<html>
<body style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; line-height: 1.6;">
    <h1 style="background: #2563eb; color: white; padding: 20px;">📧 FULL EMAIL DRAFTS - YOUR APPROVAL NEEDED</h1>
    
    <div style="background: #dcfce7; border: 2px solid #16a34a; padding: 20px; margin: 20px 0;">
        <h2>Reply with: APPROVE / REVISE / REJECT</h2>
        <p>Board Status: <strong>4/4 UNANIMOUS</strong> ✅</p>
    </div>

    <hr style="border: 2px solid #2563eb;">
    
    <!-- BATCH 1: 6 EMAILS -->
    <h1 style="background: #1e40af; color: white; padding: 15px;">BATCH 1 - 6 EMAILS</h1>

    <!-- EMAIL 1 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 1: Tony Agnello - Lakeland AC</h3>
        <p><strong>To:</strong> info@thelakelandac.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Tony,</p>
            <p>I just completed a technical audit of Lakeland Air Conditioning's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: ATTENTION NEEDED</strong> - 63/100 score, 4.2 second load time. This slow loading speed is likely causing you to lose potential customers who are searching for AC repair on their phones, especially during peak heatwaves.</li>
                <li><strong>Desktop Performance: GOOD</strong> - 85/100 score.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Missing 24/7 emergency call capture.</li>
            </ul>
            <p>The bottom line: Emergency AC customers may abandon your site before calling.</p>
            <p>I help Lakeland service businesses capture more emergency calls with AI phone systems that never sleep.</p>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p><strong>Ready to stop losing after-hours calls?</strong><br>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 2 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 2: Nathane Trimm - Trimm Roofing</h3>
        <p><strong>To:</strong> support@trimmroofing.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Nathane,</p>
            <p>I just completed a technical audit of Trimm Roofing's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: CRITICAL</strong> - 52/100 score, 5.1 second load time. With almost half of roofing searches on mobile, you're losing leads to faster competitors.</li>
                <li><strong>Desktop Performance: GOOD</strong> - 88/100 score.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Missing 24/7 emergency call capture.</li>
            </ul>
            <p>I help Lakeland service businesses capture more emergency calls with AI phone systems that never sleep.</p>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 3 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 3: Chris Shills - Curry Plumbing</h3>
        <p><strong>To:</strong> chrisshills@curryplumbing.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Chris,</p>
            <p>I just completed a technical audit of Curry Plumbing's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: WARNING</strong> - 70/100 score. Still slow enough to cause conversions to drop.</li>
                <li><strong>Desktop Performance: GOOD</strong> - 92/100 score.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Missing 24/7 emergency call capture.</li>
            </ul>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 4 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 4: Marshall Andress - Andress Electric</h3>
        <p><strong>To:</strong> info@andresselectric.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Marshall,</p>
            <p>I just completed a technical audit of Andress Electric's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: CRITICAL</strong> - 53/100 score. Customers seeking electrical help won't wait.</li>
                <li><strong>Desktop Performance: GOOD</strong> - 87/100 score.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Missing 24/7 emergency call capture.</li>
            </ul>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 5 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 5: Bill Lerch - Hunter Plumbing</h3>
        <p><strong>To:</strong> hunterplumbing@hunterplumbinginc.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Bill,</p>
            <p>I just completed a technical audit of Hunter Plumbing's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: GOOD</strong> - 80/100 score. Your site performs well!</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - The main opportunity is capturing emergency calls when your team isn't available.</li>
            </ul>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 6 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 6: David Smith - Original Pro</h3>
        <p><strong>To:</strong> proplumbing1@originalplumber.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear David,</p>
            <p>I just completed a technical audit of Original Pro's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: WARNING</strong> - 66/100 score. Not as competitive as it could be.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Missing 24/7 emergency call capture.</li>
            </ul>
            <p><strong>What I'm offering:</strong></p>
            <ul>
                <li>✓ Free performance consultation</li>
                <li>✓ 14-day AI intake system trial</li>
                <li>✓ No setup costs during trial</li>
            </ul>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <hr style="border: 3px solid #2563eb;">

    <!-- BATCH 2: 10 EMAILS -->
    <h1 style="background: #1e40af; color: white; padding: 15px;">BATCH 2 - 10 EMAILS</h1>

    <!-- EMAIL 7 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 7: Stuart Baldick III - Stuart's Plumbing</h3>
        <p><strong>To:</strong> stuart3@stuartsplumbing.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Stuart,</p>
            <p>I just completed a technical audit of Stuart's Plumbing's website and found something important.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: REVIEW NEEDED</strong> - Many local service sites underperform on mobile.</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Are you capturing 24/7 emergency calls?</li>
            </ul>
            <p>I help Lakeland service businesses capture more emergency calls with AI phone systems that never sleep.</p>
            <p><strong>What I'm offering:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 8 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 8: Mike Ashmead - On-Deck Plumbing</h3>
        <p><strong>To:</strong> Billing@ondeckplumbing.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Mike,</p>
            <p>With 25 years of expertise, you deserve a system that works as hard as you do - even at night.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - When emergencies happen at 2 AM, is someone capturing those calls?</li>
            </ul>
            <p><strong>What I'm offering:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 9 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 9: Ben Derrick - High Tower Roofing</h3>
        <p><strong>To:</strong> ben@hightowerroofing.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Ben,</p>
            <p>High Tower's stress-free roofing promise should extend to after-hours lead capture too.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - When a tree hits a roof at night, who's answering?</li>
            </ul>
            <p><strong>What I'm offering:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 10 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 10: Josh Thorpe - Thorpe Heating & Cooling</h3>
        <p><strong>To:</strong> support@thorpeac.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Josh,</p>
            <p>Florida HVAC emergencies don't follow business hours. When the AC dies at midnight in July, who's capturing that call?</p>
            <p><strong>What I'm offering:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 11 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 11: Jason Fortson - Aveco Electrical</h3>
        <p><strong>To:</strong> service@avecoinc.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Jason,</p>
            <p>Electrical emergencies don't wait for 8 AM. Power outages happen 24/7.</p>
            <p><strong>What I'm offering:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 12 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 12: Derek Springer - Springer Bros AC</h3>
        <p><strong>To:</strong> derek@springerbrosac.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Derek,</p>
            <p>With 30+ years of family expertise, your reputation deserves 24/7 lead capture that matches your service quality.</p>
            <p><strong>What I'm offering:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 13 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 13: Henry Forrest - Forrest & Son Roofing</h3>
        <p><strong>To:</strong> forrest27@me.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Henry,</p>
            <p>Four generations of roofing expertise - your family legacy deserves round-the-clock lead capture.</p>
            <p><strong>What I'm offering:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 14 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 14: Chris McConnell - Complete Plumbing & Drain</h3>
        <p><strong>To:</strong> completeplumbingfl@gmail.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Chris,</p>
            <p>As a 3rd generation plumber (your grandfather started in 1973), your family tradition deserves 24/7 lead capture.</p>
            <p><strong>What I'm offering:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 15 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 15: Billy Bishop - Top Flight Electric</h3>
        <p><strong>To:</strong> topflightelectricllc210@gmail.com</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Billy,</p>
            <p>As Founder/CEO, you know every missed call is lost revenue. Electrical emergencies don't wait for business hours.</p>
            <p><strong>What I'm offering:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 16 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3 style="background: #f3f4f6; padding: 10px;">Email 16: James Curtis - R.I.G. Roofing</h3>
        <p><strong>To:</strong> (via BBB contact form)</p>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear James,</p>
            <p>As CEO, you know capturing every lead matters. When storms hit at night, homeowners need roofing help immediately.</p>
            <p><strong>What I'm offering:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <hr style="border: 3px solid #2563eb;">

    <div style="background: #fef3c7; padding: 20px; margin: 20px 0; text-align: center;">
        <h2>YOUR APPROVAL NEEDED</h2>
        <p style="font-size: 18px;"><strong>Reply with: APPROVE / REVISE / REJECT</strong></p>
    </div>

</body>
</html>
"""

payload = {
    "email": "nearmiss1193@gmail.com",
    "from_name": "AI Service Co System",
    "from_email": "owner@aiserviceco.com",
    "subject": "FULL EMAIL DRAFTS - 16 Emails for Your Approval",
    "html_body": html
}

print("Sending via GHL webhook (Priority 1)...")
r = requests.post(GHL_EMAIL_WEBHOOK, json=payload, timeout=30)
print(f"GHL Response: {r.status_code}")
print(f"Result: {r.text[:200] if r.text else 'OK'}")
