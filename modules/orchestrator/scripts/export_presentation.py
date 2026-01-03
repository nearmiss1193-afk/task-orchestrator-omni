import os

def export_to_html_simple(md_path, html_path, title="Presentation"):
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    processed_lines = []
    in_list = False

    for line in lines:
        line_content = line.strip()
        
        # Handle list state
        if line_content.startswith("- "):
            if not in_list:
                processed_lines.append("<ul>")
                in_list = True
            processed_lines.append(f"<li>{line_content[2:]}</li>")
            continue
        else:
            if in_list:
                processed_lines.append("</ul>")
                in_list = False

        # Regular element handling
        if not line_content:
            continue
        elif line_content.startswith("# "):
            processed_lines.append(f"<h1>{line_content[2:]}</h1>")
        elif line_content.startswith("## "):
            processed_lines.append(f"<h2>{line_content[3:]}</h2>")
        elif line_content.startswith("### "):
            processed_lines.append(f"<h3>{line_content[4:]}</h3>")
        elif line_content.startswith("!["):
            try:
                alt = line_content[line_content.find("[")+1:line_content.find("]")]
                path = line_content[line_content.find("(")+1:line_content.find(")")]
                processed_lines.append(f'<img src="{path}" alt="{alt}">')
            except:
                processed_lines.append(line_content)
        elif line_content.startswith("> "):
            processed_lines.append(f"<blockquote>{line_content[2:]}</blockquote>")
        elif line_content == "---":
            processed_lines.append("<div class='slide-separator'></div>")
        else:
            processed_lines.append(f"<p>{line_content}</p>")

    if in_list:
        processed_lines.append("</ul>")

    # Basic Styling
    style = """
    <style>
        body { font-family: 'Inter', -apple-system, sans-serif; line-height: 1.6; color: #1a1a1a; max-width: 900px; margin: 40px auto; padding: 20px; background: #fff; }
        h1, h2, h3 { color: #000; border-bottom: 2px solid #eaeaea; padding-bottom: 10px; margin-top: 40px; }
        img { max-width: 100%; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin: 20px 10px; display: block; }
        code { background: #f4f4f4; padding: 2px 5px; border-radius: 4px; font-family: monospace; }
        pre { background: #2d2d2d; color: #ccc; padding: 20px; border-radius: 8px; overflow-x: auto; }
        blockquote { border-left: 5px solid #000; padding-left: 20px; font-style: italic; color: #555; }
        ul { margin-bottom: 20px; }
        li { margin-bottom: 8px; }
        .slide-separator { border-top: 3px solid #000; margin: 80px 0; }
        .portable-tag { background: #000; color: #fff; padding: 5px 10px; border-radius: 4px; font-size: 12px; display: inline-block; margin-bottom: 20px; }
    </style>
    """

    content_html = "\n".join(processed_lines)
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset='UTF-8'>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {style}
</head>
<body>
    <div class='portable-tag'>VORTEX PORTABLE DOSSIER</div>
    {content_html}
</body></html>"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"Successfully exported to: {html_path}")

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"Successfully exported to: {html_path}")

if __name__ == "__main__":
    BASE_DIR = r"C:\Users\nearm\.gemini\antigravity\brain\d91de16e-14b7-4513-a02b-aee6e62b91d0"
    
    # 1. Export Executive Dossier
    export_to_html_simple(
        os.path.join(BASE_DIR, "executive_system_dossier.md"),
        os.path.join(BASE_DIR, "Vortex_Executive_Dossier_Portable.html"),
        "Vortex Executive Dossier"
    )
    
    # 2. Export Master Slides
    export_to_html_simple(
        os.path.join(BASE_DIR, "master_system_presentation.md"),
        os.path.join(BASE_DIR, "Vortex_Master_Slides_Portable.html"),
        "Vortex Master Presentation"
    )

    # 3. Export Seacoast Presentation (For Kristina)
    export_to_html_simple(
        os.path.join(BASE_DIR, "silver_shield_presentation.md"),
        os.path.join(BASE_DIR, "Seacoast_Silver_Shield_Dossier_Kristina.html"),
        "Mission: Silver Shield (Kristine Hamilton)"
    )
