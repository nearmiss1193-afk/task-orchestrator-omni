
import json
import os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

FACTS_FILE = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\audit_reports\facts.json"
OUTPUT_DIR = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\audit_screenshots"

class AnnotatedProofGenerator:
    def __init__(self):
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    def draw_annotation(self, image_path, text, color="red", shape="arrow"):
        """
        Draws professional annotations on the existing screenshot.
        """
        try:
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            width, height = img.size
            
            # Font
            try:
                font = ImageFont.truetype("arialbd.ttf", 40)
            except:
                font = ImageFont.load_default()

            # Coordinates (Bottom Center for simplicity, or specific if elements found)
            # A strict "Arrow pointing to something missing" usually points to the empty space (Footer or Form)
            
            x = width // 2
            y = height - 100
            
            if shape == "arrow":
                # Draw Box
                draw.rectangle([(20, height - 120), (width - 20, height - 20)], outline=color, width=5, fill="#FFF0F0")
                # Text
                draw.text((50, height - 100), text, fill=color, font=font)
                
            img.save(image_path)
            print(f"   🎨 Annotated: {os.path.basename(image_path)}")
            
        except Exception as e:
            print(f"   ❌ Annotation Error: {e}")

    def generate_proofs(self, url):
        if not os.path.exists(FACTS_FILE):
            print("❌ facts.json not found. Run scan first.")
            return

        with open(FACTS_FILE, "r") as f:
            facts = json.load(f)

        print("📸 RUNNING PROMPT 3: generating evidence based on flags...")

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            
            # 1. Terms Missing -> Footer Screenshot
            if "terms-conditions" not in facts["footer_links"]:
                path = os.path.join(OUTPUT_DIR, "screenshot_terms_missing.png")
                page.goto(url, wait_until="networkidle")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)") # Scroll to footer
                page.screenshot(path=path)
                self.draw_annotation(path, "MISSING – Legal Risk (No Terms Found)", color="red")

            # 2. Form No Checkbox -> Contact Page Screenshot
            if not facts["contact_form"]["consent_checkbox"]:
                path = os.path.join(OUTPUT_DIR, "screenshot_form_no_checkbox.png")
                # Navigate to contact page if we aren't there
                if "/contact" not in page.url and facts["forms_loading"]:
                     try: 
                         page.goto(url.rstrip('/') + "/contact", timeout=5000)
                     except: 
                         pass # Stay on home if fail
                
                # Locate form if possible to center screenshot
                form = page.locator("form").first
                if form.count() > 0:
                    form.scroll_into_view_if_needed()
                
                page.screenshot(path=path)
                self.draw_annotation(path, "NO CONSENT – TCPA Risk (Missing Checkbox)", color="red")

            # 3. Slow Load -> Hero Screenshot
            if facts["page_speed"] < 90:
                path = os.path.join(OUTPUT_DIR, "screenshot_slow_load.png")
                page.goto(url) # Back to top
                page.screenshot(path=path)
                self.draw_annotation(path, f"Delays = Lost Sales (PageSpeed: {facts['page_speed']})", color="#FFAA00") # Yellow/Orange

            browser.close()

if __name__ == "__main__":
    gen = AnnotatedProofGenerator()
    gen.generate_proofs("https://yourlakelanddentist.com")
