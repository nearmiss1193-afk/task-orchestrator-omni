"""
Teaser Worker: Headless Mobile Capture
=====================================
Board Approved: Feb 16, 2026

Captures 10s mobile view scrolls of lead websites using Playwright.
Injects a "SECURITY AUDIT" status overlay for pattern interrupt.
"""

import os
import time
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def capture_mobile_teaser(url: str, company_name: str, output_path: str = "/tmp/teaser.webm"):
    """
    Captures a 10s mobile scroll of a website with a security watermark.
    """
    if not url.startswith("http"):
        url = f"https://{url}"

    async with async_playwright() as p:
        # 1. Launch Mobile Browser
        browser = await p.chromium.launch(headless=True)
        device = p.devices['iPhone 13']
        
        # 2. Setup Context with Video Recording
        video_dir = "/tmp/videos/"
        os.makedirs(video_dir, exist_ok=True)
        print(f"🎬 Initialized video directory: {video_dir}")
        
        context = await browser.new_context(
            **device,
            record_video_dir=video_dir,
            record_video_size={"width": 390, "height": 844}
        )
        
        page = await context.new_page()
        
        try:
            # 3. Navigate & Trace
            print(f"🎬 Recording teaser for {url}...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 4. Inject "Security Audit" Watermark
            await page.add_style_tag(content="""
                body::after {
                    content: 'LIVE SECURITY AUDIT - aiserviceco.com';
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(220, 53, 69, 0.9);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-family: 'Inter', sans-serif;
                    font-weight: bold;
                    font-size: 14px;
                    z-index: 999999;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { opacity: 0.8; }
                    50% { opacity: 1; transform: scale(1.05); }
                    100% { opacity: 0.8; }
                }
            """)
            
            # 5. Smooth Scroll (The Teaser)
            for i in range(5):
                await page.mouse.wheel(0, 400)
                await asyncio.sleep(1.5)
            
            # 6. Final State
            await asyncio.sleep(2)
            
            # 7. Close and Get Video Path
            await context.close()
            video = await page.video.path()
            
            # Move to final output
            if os.path.exists(video):
                import shutil
                shutil.move(video, output_path)
                print(f"✅ Teaser saved to {output_path}")
                return output_path
            
        except Exception as e:
            print(f"❌ Playwright Capture Failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()
            
    return None

def upload_teaser_to_supabase(file_path: str, lead_id: str) -> str:
    """
    Uploads the video teaser to Supabase Storage and returns the public URL.
    """
    import os
    from modules.database.supabase_client import get_supabase
    
    if not file_path or not os.path.exists(file_path):
        return None
        
    try:
        supabase = get_supabase()
        bucket_name = "teasers"
        remote_path = f"{lead_id}/audit_teaser.webm"
        
        with open(file_path, "rb") as f:
            supabase.storage.from_(bucket_name).upload(
                remote_path,
                f,
                {"content-type": "video/webm", "x-upsert": "true"}
            )
            
        public_url = supabase.storage.from_(bucket_name).get_public_url(remote_path)
        print(f"☁️ Uploaded teaser: {public_url}")
        return public_url
    except Exception as e:
        print(f"❌ Supabase Upload Failed: {e}")
        return None

if __name__ == "__main__":
    # Test Run
    asyncio.run(capture_mobile_teaser("https://lakelanddentists.com", "Lakeland Dentists"))
