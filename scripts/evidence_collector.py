import os
import time
import modal
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

# Define Modal App
image = modal.Image.debian_slim().pip_install("playwright", "pillow").run_commands("playwright install chromium")
app = modal.App("evidence-collector", image=image)

OUTPUT_DIR = "evidence"

@app.function(image=image, timeout=120)
def capture_evidence(url: str, missing_item: str = "Privacy Policy"):
    """
    Captures a screenshot of the page footer/bottom and annotates it.
    """
    print(f"🕵️ Scanning {url} for evidence...")
    
    screenshot_path = f"/tmp/evidence_{int(time.time())}.png"
    annotated_path = f"/tmp/annotated_{int(time.time())}.png"

    capture_success = False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 1. Navigate
            page.goto(url, timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(3000) # Settle
            
            # 2. Force Scroll to Bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000) 
            
            # 3. Capture Bottom Viewport (Standardized 1280x800)
            # This ensures we don't get a 10000px high skinny strip
            page.set_viewport_size({"width": 1280, "height": 800})
            
            # Ensure we are at bottom again after resize
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            print("📸 Capturing bottom viewport...")
            page.screenshot(path=screenshot_path)
            browser.close()
            capture_success = True
            
    except Exception as e:
        print(f"❌ Playwright Capture Failed: {e}")
        return None

    if capture_success and os.path.exists(screenshot_path):
        try:
            # 4. Annotate with Pillow
            img = Image.open(screenshot_path)
            draw = ImageDraw.Draw(img)
            width, height = img.size
            
            arrow_color = "#FF0000" # Bright Red
            
            # Draw "MISSING: {Item}" Box at bottom
            draw.rectangle(
                [(20, height - 80), (width - 20, height - 20)],
                fill="#FFEBEB",
                outline=arrow_color,
                width=4
            )
            
            font_size = 30
            try:
                # Try to load a bold font if available, else default
                font = ImageFont.truetype("arialbd.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            text = f"🛑 MISSING: {missing_item} (Required by FL Law)"
            # Center text roughly
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_x = (width - text_w) / 2
            text_y = height - 65
            
            draw.text((text_x, text_y), text, fill=arrow_color, font=font)
            
            img.save(annotated_path)
            
            with open(annotated_path, "rb") as f:
                return f.read()
                
        except Exception as e:
            print(f"❌ Annotation Failed: {e}")
            # Fallback to raw screenshot if annotation fails
            with open(screenshot_path, "rb") as f:
                return f.read()
    
    return None

@app.local_entrypoint()
def main():
    # Batch 3 Targets (Only those with privacy="missing")
    targets = [
        {
            "name": "Brilliant Smiles Lakeland",
            "url": "https://yourlakelanddentist.com"
        }
    ]

    # Ensure evidence directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for t in targets:
        print(f"📸 Capturing evidence for {t['name']} ({t['url']})...")
        image_bytes = capture_evidence.remote(t['url'])
        
        if image_bytes:
            # Filename format must match generate_batch3_pdfs.py expectation:
            # evidence_{business_name}.png (spaces -> underscores)
            safe_name = t['name'].replace(" ", "_")
            filename = f"evidence_{safe_name}.png"
            output_path = os.path.join(OUTPUT_DIR, filename)
            
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            print(f"✅ Saved: {output_path}")
        else:
            print(f"❌ Failed to capture: {t['name']}")
