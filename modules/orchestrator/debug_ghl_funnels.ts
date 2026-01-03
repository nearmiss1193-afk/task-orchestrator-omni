
import { GHLBrowserConnector } from './lib/connectors/ghl-browser';
import * as dotenv from 'dotenv';
import * as path from 'path';
import * as fs from 'fs';

// Load env
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function run() {
    console.log("Starting Debug of GHL Funnels Page...");
    const browser = new GHLBrowserConnector();

    // Quick access to private page
    await browser['ensureBrowser']();
    await browser['ensureAuthenticated']();
    const page = browser['page']!;

    try {
        const baseUrl = page.url().startsWith('http') ? new URL(page.url()).origin : "https://app.gohighlevel.com";
        const envLocationId = process.env.GHL_LOCATION_ID;
        const targetUrl = `${baseUrl}/v2/location/${envLocationId}/funnels/funnel`;

        console.log(`Navigating to: ${targetUrl}`);
        await page.goto(targetUrl, { waitUntil: 'networkidle2' });
        await new Promise(r => setTimeout(r, 5000));

        // 1. Screenshot
        await page.screenshot({ path: 'debug_funnels_page.png' });
        console.log("Saved debug_funnels_page.png");

        // 2. Dump Buttons
        const buttonTexts = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button, a'));
            return buttons.map(b => ({
                tag: b.tagName,
                text: b.textContent?.trim() || '',
                id: b.id,
                class: b.className,
                href: (b as HTMLAnchorElement).href || ''
            }));
        });

        fs.writeFileSync('debug_buttons.json', JSON.stringify(buttonTexts, null, 2));
        console.log("Saved debug_buttons.json");

        // 3. Search for "New Funnel" candidate
        const candidates = buttonTexts.filter(b =>
            b.text.toLowerCase().includes('funnel') ||
            b.text.toLowerCase().includes('create') ||
            b.text.toLowerCase().includes('new')
        );
        console.log("Potential Candidates:", JSON.stringify(candidates, null, 2));

    } catch (e) {
        console.error("Debug failed:", e);
    } finally {
        console.log("Done.");
        process.exit(0);
    }
}

run().catch(console.error);
