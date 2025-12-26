
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import puppeteer from 'puppeteer';

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function run() {
    console.log("=== PROBE SESSION V2 ===");
    const email = process.env.GHL_EMAIL;
    const password = process.env.GHL_PASSWORD;
    const locationId = process.env.GHL_LOCATION_ID;

    if (!email || !password) {
        console.error("Missing credentials in .env.local");
        process.exit(1);
    }

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: null,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800', '--start-maximized']
    });

    try {
        const page = (await browser.pages())[0];
        console.log("Navigating to GHL Login...");

        // Go to login page
        await page.goto('https://app.gohighlevel.com/', { waitUntil: 'networkidle2', timeout: 60000 });

        // Check if we are redirected to login or already in dashboard (if generic profile was reused, unlikely here but good practice)
        if (page.url().includes('location')) {
            console.log("Already logged in!");
        } else {
            // Handle Login
            console.log("Waiting for email input...");
            try {
                await page.waitForSelector('input[type="email"]', { timeout: 10000 });
                await page.type('input[type="email"]', email);
                await page.type('input[type="password"]', password);

                console.log("Submitting login...");
                await page.click('button[type="submit"]'); // Generic selector, might need adjustment if generic fails
                // Or press Enter
                // await page.keyboard.press('Enter');

                await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 60000 });
            } catch (e) {
                console.log("Login form not found or interaction failed. Checking if we are already in...");
            }
        }

        // Force navigate to a clean dashboard URL to ensure state
        if (locationId) {
            console.log(`Navigating to specific location dashboard: ${locationId}`);
            await page.goto(`https://app.gohighlevel.com/v2/location/${locationId}/dashboard`, { waitUntil: 'networkidle2', timeout: 60000 });
        }

        // Wait a bit for local storage to populate
        await new Promise(r => setTimeout(r, 5000));

        console.log("Extracting tokens...");
        const sessionData = await page.evaluate(() => {
            return {
                token: localStorage.getItem('token'),
                locationId: localStorage.getItem('location'),
                user: localStorage.getItem('user')
            };
        });

        console.log("Session Data found:", sessionData.token ? "YES" : "NO");

        if (sessionData.token) {
            fs.writeFileSync('ghl_session_token.json', JSON.stringify(sessionData, null, 2));
            console.log("Token saved to ghl_session_token.json");
        } else {
            console.error("Failed to retrieve token. Page content dump:");
            console.log(await page.content()); // heavy log but needed if fail
        }

    } catch (e) {
        console.error("Probe failed:", e);
    } finally {
        console.log("Closing browser...");
        await browser.close();
    }
}

run();
