import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        print("Navigating to OpenGov portal...")
        
        # OpenGov uses heavy SPAs, networkidle can hang. Use domcontentloaded and explicit waits.
        await page.goto('https://procurement.opengov.com/portal/lakelandgov', wait_until='domcontentloaded')
        
        print("Waiting for bid titles to load...")
        try:
            # Wait for at least one bid title class to appear
            await page.wait_for_selector('h4', timeout=15000) 
            # Note: inspecting typical OpenGov portals, project names might be in h4 or specific classes. 
            print("Page Title:", await page.title())
            
            # Scrape all text
            content = await page.content()
            if 'project-name' in content:
                print("Found project-name class")
            else:
                print("project-name class not found in raw HTML. We might need a different selector.")
                
            # Let's extract links to see what exists
            links = await page.eval_on_selector_all('a', 'elements => elements.map(e => e.innerText + " | " + e.href)')
            bids = [lnk for lnk in links if '/projects/' in lnk]
            
            print(f"Found {len(bids)} project links.")
            for i, bid in enumerate(bids[:5]):
                print(f"{i+1}. {bid}")
                
        except Exception as e:
            print("Error waiting for selector:", e)
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
