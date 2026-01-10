import os
import re

CSS_FILE = "public/css/autofix.css"
HTML_DIR = "public"

def extract_styles():
    print("🎨 Starting CSS Autofix...")
    
    style_map = {} # style_string -> class_name
    class_counter = 1
    
    # Ensure css dir exists
    os.makedirs(os.path.dirname(CSS_FILE), exist_ok=True)
    
    # Load existing if needed? No, fresh start for autofix.
    css_content = "/* Auto-generated styles to remove inline technical debt */\n"

    for root, dirs, files in os.walk(HTML_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                modified = False
                
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Regex for style="..." OR style='...'
                def replace_style(match):
                    nonlocal class_counter, css_content, modified
                    
                    # Group 2 is double quoted content, Group 3 is single quoted
                    style_body = match.group(2) or match.group(3)
                    if not style_body: 
                         return match.group(0)
                    
                    style_body = style_body.strip()
                    
                    if style_body not in style_map:
                        cls_name = f"style-fix-{class_counter}"
                        style_map[style_body] = cls_name
                        css_content += f".{cls_name} {{ {style_body} }}\n"
                        class_counter += 1
                    
                    cls_name = style_map[style_body]
                    modified = True
                    
                    return f'class="{cls_name}" data-style-migrated="true"'

                # Regex updated to handle both " and '
                new_content = re.sub(r'(style=(["\'])(.*?)\2)', replace_style, content)
                
                # Inject CSS link if modified
                if modified:
                    if "autofix.css" not in new_content:
                         new_content = new_content.replace("</head>", f'    <link rel="stylesheet" href="css/autofix.css">\n</head>')
                    
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"  ✅ Fixed {file}")

    with open(CSS_FILE, "w", encoding="utf-8") as f:
        f.write(css_content)
    
    print(f"✨ Extracted {len(style_map)} unique styles to {CSS_FILE}")

if __name__ == "__main__":
    extract_styles()
