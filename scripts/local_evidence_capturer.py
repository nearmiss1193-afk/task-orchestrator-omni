
import os
import time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

# Simple local script, no Modal
OUTPUT_DIR = "evidence"

def capture_evidence(url: str, missing_item: str = "Privacy Policy"):
    print(f"🕵️ Scanning {url} for evidence (LOCAL)...")
    
    screenshot_path = os.path.join(OUTPUT_DIR, f"temp_{int(time.time())}.png")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 1. Navigate
            page.goto(url, timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(3000)
            
            # 2. Force Scroll to Bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000) 
            
            # 3. Capture Bottom Viewport (Standardized 1280x800)
            page.set_viewport_size({"width": 1280, "height": 800})
            
            # Ensure we are at bottom again after resize
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            print("📸 Capturing bottom viewport...")
            page.screenshot(path=screenshot_path)
            browser.close()
            
            return screenshot_path
            
    except Exception as e:
        print(f"❌ Playwright Capture Failed: {e}")
        return None

def annotate_evidence(screenshot_path, missing_item):
    if not screenshot_path or not os.path.exists(screenshot_path):
        return None
        
    try:
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
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text = f"🛑 MISSING: {missing_item} (Required by FL Law)"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_x = (width - text_w) / 2
        text_y = height - 65
        
        draw.text((text_x, text_y), text, fill=arrow_color, font=font)
        
        # Save over original
        img.save(screenshot_path)
        print(f"✅ Annotated: {screenshot_path}")
        return screenshot_path
        
    except Exception as e:
        print(f"❌ Annotation Failed: {e}")
        return None

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    targets = [
        {
            "name": "Brilliant Smiles Lakeland",
            "url": "https://yourlakelanddentist.com",
            "missing": "Terms of Use"  # Updated Finding
        }
    ]

    for t in targets:
        # Capture
        temp_path = capture_evidence(t['url'])
        if temp_path:
            # Annotate with SPECIFIC missing item
            annotate_evidence(temp_path, missing_item=t.get("missing", "Privacy Policy"))
            
            # Rename to final
            safe_name = t['name'].replace(" ", "_")
            final_path = os.path.join(OUTPUT_DIR, f"evidence_{safe_name}.png")
            
            if os.path.exists(final_path):
                os.remove(final_path)
                
            os.rename(temp_path, final_path)
            print(f"✅ Final Evidence Saved: {final_path}")
            
            # Verify Size
            size = os.path.getsize(final_path)
            print(f"📊 File Size: {size} bytes")
        else:
            print("❌ Failed completely.")

if __name__ == "__main__":
    main()
