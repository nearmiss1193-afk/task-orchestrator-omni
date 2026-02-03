
import { GHLBrowserConnector } from './lib/connectors/ghl-browser';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import puppeteer from 'puppeteer';

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function probeSession() {
    console.log("=== PROBING GHL SESSION FOR API TOKENS ===");
    const browser = new GHLBrowserConnector();

    // We need to access the internal page object, so we'll use a subclass or just raw puppeteer?
    // Using raw puppeteer to be safe and quick.

    const email = process.env.GHL_EMAIL;
    const password = process.env.GHL_PASSWORD;
    const locationId = process.env.GHL_LOCATION_ID;

    const pBrowser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });
    const page = (await pBrowser.pages())[0];

    // Login
    await page.goto('https://app.gohighlevel.com/', { waitUntil: 'networkidle2' });
    if (!page.url().includes('location')) {
        await page.type('input[type="email"]', email!);
        await page.type('input[type="password"]', password!);
        await page.click('button[type="submit"]');
        await page.waitForNavigation({ waitUntil: 'networkidle2' });
    }

    // Go to a data-rich page
    await page.goto(`https://app.gohighlevel.com/v2/location/${locationId}/dashboard`, { waitUntil: 'networkidle2' });

    // Extract LocalStorage / Cookies
    const localStorageData = await page.evaluate(() => {
        return {
            token: localStorage.getItem('token'),
            user: localStorage.getItem('user'),
            location: localStorage.getItem('location')
        };
    });

    console.log("LocalStorage Probe:", localStorageData);

    if (localStorageData.token) {
        console.log("SUCCESS: Found Token. We can use this for API calls.");
        fs.writeFileSync('ghl_session_token.json', JSON.stringify(localStorageData, null, 2));
    } else {
        console.error("FAILURE: No token found in LocalStorage.");
    }

    await pBrowser.close();
}

probeSession();
