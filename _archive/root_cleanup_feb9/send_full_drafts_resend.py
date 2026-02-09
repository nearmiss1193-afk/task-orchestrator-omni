"""
Send FULL email drafts via Resend (confirmed working)
Per operational_memory.md: GHL not delivering, use Resend
"""
import sys
sys.path.insert(0, '.')
from reliable_email import send_email

html = """
<html>
<body style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; line-height: 1.6;">
    <h1 style="background: #2563eb; color: white; padding: 20px;">📧 FULL EMAIL DRAFTS - YOUR APPROVAL NEEDED</h1>
    
    <div style="background: #dcfce7; border: 2px solid #16a34a; padding: 20px; margin: 20px 0;">
        <h2>Reply with: APPROVE / REVISE / REJECT</h2>
    </div>

    <hr style="border: 2px solid #2563eb;">
    
    <!-- BATCH 1: 6 EMAILS -->
    <h1 style="background: #1e40af; color: white; padding: 15px;">BATCH 1 - 6 EMAILS</h1>

    <!-- EMAIL 1 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 1: Tony Agnello - Lakeland AC (info@thelakelandac.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Tony,</p>
            <p>I just completed a technical audit of Lakeland Air Conditioning's website.</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: ATTENTION NEEDED</strong> - 63/100 score</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong> - Missing 24/7 emergency call capture</li>
            </ul>
            <p>I help Lakeland service businesses capture more emergency calls with AI phone systems that never sleep.</p>
            <p><strong>What I'm offering:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call me at 352-936-8152.</p>
            <p>Best regards,<br>Daniel Coffman<br>Owner, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 2 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 2: Nathane Trimm - Trimm Roofing (support@trimmroofing.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Nathane,</p>
            <p><strong>KEY FINDINGS:</strong></p>
            <ul>
                <li><strong>Mobile Speed: CRITICAL</strong> - 52/100 score, 5.1 second load time</li>
                <li><strong>After-Hours Leads: OPPORTUNITY</strong></li>
            </ul>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 3 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 3: Chris Shills - Curry Plumbing (chrisshills@curryplumbing.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Chris,</p>
            <p><strong>KEY FINDINGS:</strong> Mobile Speed: 70/100 | After-Hours: OPPORTUNITY</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 4 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 4: Marshall Andress - Andress Electric (info@andresselectric.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Marshall,</p>
            <p><strong>KEY FINDINGS:</strong> Mobile Speed: 53/100 CRITICAL | After-Hours: OPPORTUNITY</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 5 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 5: Bill Lerch - Hunter Plumbing (hunterplumbing@hunterplumbinginc.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Bill,</p>
            <p><strong>KEY FINDINGS:</strong> Mobile Speed: 80/100 GOOD | After-Hours: OPPORTUNITY</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 6 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 6: David Smith - Original Pro (proplumbing1@originalplumber.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear David,</p>
            <p><strong>KEY FINDINGS:</strong> Mobile Speed: 66/100 WARNING | After-Hours: OPPORTUNITY</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <hr style="border: 3px solid #2563eb;">

    <!-- BATCH 2: 10 EMAILS -->
    <h1 style="background: #1e40af; color: white; padding: 15px;">BATCH 2 - 10 EMAILS</h1>

    <!-- EMAIL 7 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 7: Stuart Baldick III - Stuart's Plumbing (stuart3@stuartsplumbing.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Stuart, With 25+ years serving Lakeland, your expertise deserves 24/7 lead capture.</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 8 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 8: Mike Ashmead - On-Deck Plumbing (Billing@ondeckplumbing.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Mike, With 25 years of expertise, you deserve a system that works as hard as you do.</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 9 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 9: Ben Derrick - High Tower Roofing (ben@hightowerroofing.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Ben, High Tower's stress-free promise should extend to after-hours lead capture.</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 10 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 10: Josh Thorpe - Thorpe AC (support@thorpeac.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Josh, Florida HVAC emergencies don't follow business hours. When the AC dies at midnight, who's capturing that call?</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 11 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 11: Jason Fortson - Aveco Electrical (service@avecoinc.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Jason, Electrical emergencies don't wait for 8 AM. Power outages happen 24/7.</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 12 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 12: Derek Springer - Springer Bros AC (derek@springerbrosac.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Derek, With 30+ years of family expertise, your reputation deserves 24/7 lead capture.</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 13 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 13: Henry Forrest - Forrest & Son (forrest27@me.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Henry, Four generations of roofing expertise - your family legacy deserves round-the-clock lead capture.</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 14 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 14: Chris McConnell - Complete Plumbing (completeplumbingfl@gmail.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Chris, As a 3rd generation plumber (your grandfather started in 1973), your family tradition deserves 24/7 lead capture.</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 15 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 15: Billy Bishop - Top Flight Electric (topflightelectricllc210@gmail.com)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear Billy, As Founder/CEO, you know every missed call is lost revenue. Electrical emergencies don't wait.</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
        </div>
    </div>

    <!-- EMAIL 16 -->
    <div style="border: 2px solid #333; margin: 20px 0; padding: 20px;">
        <h3>Email 16: James Curtis - R.I.G. Roofing (via BBB contact form)</h3>
        <div style="background: #fafafa; padding: 15px; border-left: 4px solid #2563eb;">
            <p>Dear James, As CEO, you know capturing every lead matters. When storms hit at night, homeowners need roofing help immediately.</p>
            <p><strong>Offer:</strong> ✓ Free consultation ✓ 14-day AI trial ✓ No setup costs</p>
            <p>Reply today or call 352-936-8152. - Daniel Coffman, AI Service Co</p>
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

if __name__ == "__main__":
    print("Sending FULL email drafts via Resend...")
    result = send_email('nearmiss1193@gmail.com', 'FULL EMAIL DRAFTS - 16 Emails for Your Approval', html)
    print(f"Result: {result}")
