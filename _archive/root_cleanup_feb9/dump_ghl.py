
import asyncio
import os
from playwright.async_api import async_playwright

async def dump_dom():
    user_data_dir = os.path.join(os.getcwd(), ".ghl_browser_data")
    workflow_id = "44e67279-2ad5-491c-82f0-f8eaadea085c"
    location_id = "RnK4OjX0oDcqtWw0VyLr"
    workflow_url = f"https://app.gohighlevel.com/v2/location/{location_id}/automation/workflow/{workflow_id}"
    
    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = await context.new_page()
            await page.goto(workflow_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(15) 
            
            content = f"URL: {page.url}\n\n"
            content += "MAIN FRAME CONTENT:\n"
            content += await page.content()
            
            for i, frame in enumerate(page.frames):
                if frame == page.main_frame: continue
                try:
                    frame_content = await frame.content()
                    content += f"\n\nFRAME {i} ({frame.url}):\n{frame_content}"
                except:
                    content += f"\n\nFRAME {i} ({frame.url}): [BLOCKED/FAILED]"
            
            with open("ghl_dom.txt", "w", encoding="utf-8") as f:
                f.write(content)
            
            print("[DUMPER] DOM dumped to ghl_dom.txt")
            await context.close()
        except Exception as e:
            print(f"[DUMPER] ❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(dump_dom())
