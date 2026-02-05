"""Send approval email to Dan using reliable_email"""
import sys
sys.path.insert(0, '.')
from reliable_email import send_email

html = """
<html>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
    <h1>APPROVAL REQUESTED: 16 Email Drafts</h1>
    
    <div style="background: #dcfce7; border: 1px solid #16a34a; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <strong>BOARD STATUS:</strong><br>
        Batch 1 (6 emails): 4/4 APPROVED<br>
        Batch 2 (10 emails): Review complete
    </div>
    
    <h2>Your Decision</h2>
    <p>Reply with: <strong>APPROVE</strong> / <strong>REVISE</strong> / <strong>REJECT</strong></p>
    
    <hr>
    
    <h2>BATCH 1 - 6 Emails</h2>
    <table border="1" cellpadding="10" style="border-collapse: collapse;">
        <tr><th>Owner</th><th>Company</th><th>Email</th></tr>
        <tr><td>Tony Agnello</td><td>Lakeland AC</td><td>info@thelakelandac.com</td></tr>
        <tr><td>Nathane Trimm</td><td>Trimm Roofing</td><td>support@trimmroofing.com</td></tr>
        <tr><td>Chris Shills</td><td>Curry Plumbing</td><td>chrisshills@curryplumbing.com</td></tr>
        <tr><td>Marshall Andress</td><td>Andress Electric</td><td>info@andresselectric.com</td></tr>
        <tr><td>Bill Lerch</td><td>Hunter Plumbing</td><td>hunterplumbing@hunterplumbinginc.com</td></tr>
        <tr><td>David Smith</td><td>Original Pro</td><td>proplumbing1@originalplumber.com</td></tr>
    </table>
    
    <h2>BATCH 2 - 10 Emails</h2>
    <table border="1" cellpadding="10" style="border-collapse: collapse;">
        <tr><th>Owner</th><th>Company</th><th>Email</th></tr>
        <tr><td>Stuart Baldick III</td><td>Stuart's Plumbing</td><td>stuart3@stuartsplumbing.com</td></tr>
        <tr><td>Mike Ashmead</td><td>On-Deck Plumbing</td><td>Billing@ondeckplumbing.com</td></tr>
        <tr><td>Ben Derrick</td><td>High Tower Roofing</td><td>ben@hightowerroofing.com</td></tr>
        <tr><td>Josh Thorpe</td><td>Thorpe AC</td><td>support@thorpeac.com</td></tr>
        <tr><td>Jason Fortson</td><td>Aveco Electrical</td><td>service@avecoinc.com</td></tr>
        <tr><td>Derek Springer</td><td>Springer Bros AC</td><td>derek@springerbrosac.com</td></tr>
        <tr><td>Henry Forrest</td><td>Forrest and Son</td><td>forrest27@me.com</td></tr>
        <tr><td>Chris McConnell</td><td>Complete Plumbing</td><td>completeplumbingfl@gmail.com</td></tr>
        <tr><td>Billy Bishop</td><td>Top Flight Electric</td><td>topflightelectricllc210@gmail.com</td></tr>
        <tr><td>James Curtis</td><td>R.I.G. Roofing</td><td>(via BBB form)</td></tr>
    </table>
    
    <hr>
    
    <p style="background: #fef3c7; padding: 15px; border-radius: 5px;">
        <strong>Reply to this email with: APPROVE / REVISE / REJECT</strong>
    </p>
    
    <p style="color: #666;">
        Full drafts in artifacts directory<br>
        Sent via Antigravity
    </p>
</body>
</html>
"""

if __name__ == "__main__":
    print("Sending approval email to Dan...")
    result = send_email('nearmiss1193@gmail.com', 'APPROVAL REQUESTED: 16 Email Drafts (Batch 1 + 2)', html)
    print(f"Result: {result}")
