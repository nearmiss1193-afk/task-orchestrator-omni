"""Add GA4 tag to all public HTML pages"""
import os, glob

GA_TAG = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XZK2Z9K3TW"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XZK2Z9K3TW');
</script>'''

public_dir = os.path.join(os.path.dirname(__file__), '..', 'public')
html_files = glob.glob(os.path.join(public_dir, '*.html'))

for filepath in sorted(html_files):
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already has GA4
    if 'G-XZK2Z9K3TW' in content:
        print(f'SKIP (already has GA4): {filename}')
        continue
    
    # Insert after <head> tag
    if '<head>' in content:
        content = content.replace('<head>', f'<head>\n{GA_TAG}', 1)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'ADDED GA4: {filename}')
    elif '<HEAD>' in content:
        content = content.replace('<HEAD>', f'<HEAD>\n{GA_TAG}', 1)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'ADDED GA4: {filename}')
    else:
        print(f'WARNING - no <head> tag found: {filename}')

print(f'\nDone. Processed {len(html_files)} files.')
