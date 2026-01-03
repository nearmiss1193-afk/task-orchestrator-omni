
import argparse
import datetime
import os
import asyncio
from playwright.async_api import async_playwright

async def audit_sites(targets_file, scan_types, output_file):
    print(f"🕵️ STARTED WEBSITE REPAIR AUDIT (v43.1)")
    print(f"Targets from: {targets_file}")
    
    with open(targets_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
        
    report = f"# WEBSITE REPAIR AUDIT ({datetime.datetime.now().strftime('%Y-%m-%d')})\n\n"
    report += "| URL | Status | Widget | Contact Info | CTA Health | Speed |\n"
    report += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    issue_list = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for url in urls:
            print(f"  -> Scanning: {url}")
            try:
                # 1. Performance Check
                start_time = datetime.datetime.now()
                page = await browser.new_page()
                try:
                    response = await page.goto(url, timeout=15000, wait_until='domcontentloaded')
                    status = response.status
                except:
                    status = "ERR"
                
                load_time = (datetime.datetime.now() - start_time).total_seconds()
                speed_grade = "🟢 Fast" if load_time < 3 else "🔴 Slow"
                
                if status == "ERR":
                    report += f"| {url} | 🔴 ERR | N/A | N/A | N/A | N/A |\n"
                    issue_list.append(f"- **{url}**: Site Connection Failed.")
                    await page.close()
                    continue

                # 2. Widget Check
                # Look for GHL chat widget, Intercom, etc.
                widget_found = False
                if await page.query_selector("chat-widget") or await page.query_selector("iframe#chat-widget") or "leadconnector" in await page.content():
                    widget_found = True
                
                widget_status = "✅ OK" if widget_found else "❌ MISSING"
                if not widget_found: issue_list.append(f"- **{url}**: Chat Widget Missing.")

                # 3. Contact Info (Email/Phone)
                # content = await page.content() # Too big for some checks, use text
                text = await page.inner_text("body")
                has_phone = any(c.isdigit() for c in text) and ("555" not in text) # Rough heuristic
                has_email = "@" in text
                contact_status = "✅ Found" if (has_phone or has_email) else "⚠️ Missing"
                
                # 4. CTA Health (Link Check)
                links = await page.query_selector_all("a")
                broken_links = 0
                for link in links[:10]: # Check first 10
                    href = await link.get_attribute("href")
                    if not href or href == "#": broken_links += 1
                
                cta_status = "✅ Healthy" if broken_links == 0 else f"⚠️ {broken_links} Broken"
                if broken_links > 0: issue_list.append(f"- **{url}**: {broken_links} Empty/Broken Links found.")

                report += f"| {url} | {status} | {widget_status} | {contact_status} | {cta_status} | {speed_grade} ({round(load_time,1)}s) |\n"
                
                await page.close()
                
            except Exception as e:
                report += f"| {url} | 🔴 CRASH | {str(e)[:20]}... | | | |\n"
                issue_list.append(f"- **{url}**: Audit Crashed: {e}")

        await browser.close()
        
    report += "\n## 🛠️ REPAIR CHECKLIST\n"
    if issue_list:
        for issue in issue_list:
            report += f"{issue}\n"
    else:
        report += "✅ ALL SYSTEMS NORMAL.\n"
        
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"✅ Audit Complete: {output_file}")


def run_audit_wrapper():
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", required=True)
    parser.add_argument("--scan", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    asyncio.run(audit_sites(args.targets, args.scan, args.output))

if __name__ == "__main__":
    import argparse
    run_audit_wrapper()
