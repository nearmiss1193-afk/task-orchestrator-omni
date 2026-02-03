
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
    console.log("🔍 Starting GHL Verification...");
    const userDataDir = path.join(process.cwd(), '.ghl_browser_data_' + Date.now());

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: null,
        args: [
            '--no-sandbox',
            '--window-size=1280,800',
            '--disable-blink-features=AutomationControlled'
        ],
        userDataDir: userDataDir
    });

    const page = await browser.newPage();
    const envLocationId = 'RnK4OjX0oDcqtWw0VyLr'; // Hardcoded from .env for verify

    try {
        console.log("Navigating to Dashboard...");
        await page.goto('https://app.gohighlevel.com/', { waitUntil: 'domcontentloaded' });
        await new Promise(r => setTimeout(r, 5000));

        console.log(`Current URL: ${page.url()}`);
        await page.screenshot({ path: 'ghl_verify_dashboard.png' });

        console.log("Navigating to Funnels...");
        // Try the explicit URL we used
        await page.goto(`https://app.gohighlevel.com/v2/location/${envLocationId}/funnels/page`, { waitUntil: 'domcontentloaded' });
        // funnels/page is the list? Or just funnels? trying likely targets

        await new Promise(r => setTimeout(r, 5000));
        console.log(`Funnels URL: ${page.url()}`);
        await page.screenshot({ path: 'ghl_verify_funnels.png' });

        // List funnel names if possible
        const funnelNames = await page.evaluate(() => {
            return Array.from(document.querySelectorAll('.funnel-card-name, .table-row-name, h5, span'))
                .map(e => e.innerText)
                .filter(t => t.length > 5 && t.length < 50)
                .slice(0, 10);
        });
        console.log("Visible Text Elements (Potential Funnels):", funnelNames);

    } catch (e) {
        console.error("Verification Error:", e);
        await page.screenshot({ path: 'ghl_verify_error.png' });
    } finally {
        await browser.close();
    }
})();
