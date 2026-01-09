import os

# Configuration
TARGET_DIR = "public"
GTAG_SNIPPET = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-8080RNWHVV">
</script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-8080RNWHVV');
</script>
"""

def inject_tag():
    count = 0
    skipped = 0
    
    # Walk through the directory
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check if already injected
                if "G-8080RNWHVV" in content:
                    print(f"⏩ Skipping {file} (Tag already present)")
                    skipped += 1
                    continue
                
                # Inject before </head>
                if "</head>" in content:
                    new_content = content.replace("</head>", f"{GTAG_SNIPPET}</head>")
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    
                    print(f"✅ Injected tag into {file}")
                    count += 1
                else:
                    print(f"⚠️ Could not find </head> in {file}")
                    skipped += 1

    print(f"\nSummary: Injected {count} files. Skipped {skipped} files.")

if __name__ == "__main__":
    inject_tag()
