import os
import re

# Google tag snippet to add
GOOGLE_TAG = '''
    <!-- Google tag (gtag.js) for Google Ads Conversion Tracking -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-8080RNWHVV"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-8080RNWHVV');
        gtag('config', 'AW-17858959033');
    </script>
'''

# Files to update (excluding index.html and thank-you.html which are already done)
files_to_update = [
    'audit.html',
    'booking.html',
    'checkout.html',
    'features.html',
    'intake.html',
    'media.html',
    'payment.html',
    'privacy.html',
    'sov_8k2_cmd.html',
    'terms.html',
    'test_drive.html',
    'vanguard_waitlist.html',
    'voice_board.html'
]

public_dir = r'c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\public'

for filename in files_to_update:
    filepath = os.path.join(public_dir, filename)
    if not os.path.exists(filepath):
        print(f'SKIP: {filename} not found')
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has the Google Ads tag
    if 'AW-17858959033' in content:
        print(f'SKIP: {filename} already has Google Ads tag')
        continue
    
    # Check if already has G-8080RNWHVV
    if 'G-8080RNWHVV' in content:
        # Just add the config line
        content = content.replace(
            "gtag('config', 'G-8080RNWHVV');",
            "gtag('config', 'G-8080RNWHVV');\n        gtag('config', 'AW-17858959033');"
        )
        print(f'UPDATED: {filename} - added AW config')
    else:
        # Insert after <head> or <meta charset>
        if '<head>' in content:
            # Find </head> and insert before it
            content = content.replace('<head>', '<head>' + GOOGLE_TAG)
            print(f'ADDED: {filename} - full Google tag')
        else:
            print(f'WARN: {filename} - no <head> tag found')
            continue
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('\nDone updating files!')
