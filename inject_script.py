
import os
import glob

TARGET_DIR = "apps/portal/public/landing"
SCRIPT_TAG = '<script src="/landing/lead-capture.js"></script>'

def inject():
    files = glob.glob(os.path.join(TARGET_DIR, "*.html"))
    print(f"Found {len(files)} HTML files.")

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "lead-capture.js" in content:
            print(f"✅ Already injected: {os.path.basename(file_path)}")
            continue
        
        # Inject before </head>
        if "</head>" in content:
            new_content = content.replace("</head>", f"{SCRIPT_TAG}\n</head>")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"💉 Injected into: {os.path.basename(file_path)}")
        else:
            print(f"⚠️ No </head> found in: {os.path.basename(file_path)}")

if __name__ == "__main__":
    inject()
