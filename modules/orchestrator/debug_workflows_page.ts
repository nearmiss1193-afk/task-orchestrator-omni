
import { GHLBrowserConnector } from './lib/connectors/ghl-browser';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import puppeteer from 'puppeteer';

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

// Monkey-patching to expose internal page since it's private in the class but I need raw access
// Actually, I'll extend the class or just use the class methods if I can.
// I'll modify the `audit_account` or just create a fresh puppeteer instance here for debug speed? 
// No, use the connector to handle auth. I'll add a 'debug_page' action or similar?
// Or just copy the auth logic. Using the connector's existing 'audit_account' gets me to the page if I modify it?
// Let's just create a raw script re-using the logic for now to be fast.

async function run() {
    const email = process.env.GHL_EMAIL;
    const password = process.env.GHL_PASSWORD;
    const locationId = process.env.GHL_LOCATION_ID;

    console.log("Launching Debug Browser...");
    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: null,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800'],
        userDataDir: path.join(require('os').tmpdir(), `ghl_debug_workflows_${Date.now()}`)
    });

    const page = (await browser.pages())[0];

    // Login
    await page.goto('https://app.gohighlevel.com/', { waitUntil: 'networkidle2' });
    if (page.url().includes('location')) {
        console.log("Already logged in (unlikely with new profile)");
    } else {
        console.log("Logging in...");
        await page.type('input[type="email"]', email!);
        await page.type('input[type="password"]', password!);
        await page.click('button[type="submit"]');
        await page.waitForNavigation({ waitUntil: 'networkidle2' });
    }

    // Go to Workflows
    console.log("Navigating to Workflows...");
    const workflowsUrl = `https://app.gohighlevel.com/v2/location/${locationId}/automation/workflows`;
    await page.goto(workflowsUrl, { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 5000));

    // Screenshot
    await page.screenshot({ path: 'debug_workflows.png' });

    // Dump Buttons
    console.log("Dumping Buttons...");
    const buttons = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('button, a')).map(b => ({
            text: b.textContent?.trim(),
            class: b.className,
            href: (b as HTMLAnchorElement).href
        }));
    });

    fs.writeFileSync('debug_workflows_buttons.json', JSON.stringify(buttons, null, 2));
    console.log("Done. Check debug_workflows.png and debug_workflows_buttons.json");

    // Keep open for a bit
    await new Promise(r => setTimeout(r, 5000));
    await browser.close();
}

run();
