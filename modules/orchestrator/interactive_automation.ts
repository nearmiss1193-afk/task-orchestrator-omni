
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import puppeteer from 'puppeteer';

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function run() {
    console.log("=== INTERACTIVE AUTOMATION - STAGE 1: SESSION SNATCH ===");
    console.log("1. Browser will open on YOUR white-label domain.");
    console.log("2. PLEASE LOG IN. I will wait until you reach a dashboard.");
    console.log("3. Once I grab the token, STAGE 2 will automatically begin creation.");

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: null,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800', '--start-maximized']
    });

    try {
        const page = (await browser.pages())[0];
        await page.goto('https://app.aiserviceco.com/', { waitUntil: 'domcontentloaded' });

        const snatchToken = async () => {
            return await page.evaluate(() => {
                return {
                    token: localStorage.getItem('token'),
                    locationId: localStorage.getItem('location')
                };
            });
        };

        let captured = false;
        for (let i = 0; i < 300; i++) { // 10 minutes
            const data = await snatchToken();
            if (data.token) {
                console.log("\n[STAGE 1] TOKEN CAPTURED!");
                fs.writeFileSync('ghl_session_token.json', JSON.stringify(data, null, 2));
                captured = true;
                break;
            }
            if (i % 10 === 0) process.stdout.write(".");
            await new Promise(r => setTimeout(r, 2000));
        }

        if (!captured) {
            console.error("Timeout waiting for token.");
            await browser.close();
            process.exit(1);
        }

        console.log("\n=== STAGE 2: AUTONOMOUS CREATION ===");
        // We stay in the SAME browser/page to reuse the session
        // Navigate to Funnels
        const locationId = JSON.parse(fs.readFileSync('ghl_session_token.json', 'utf8')).locationId || process.env.GHL_LOCATION_ID;
        console.log(`Navigating to Funnels for ${locationId}...`);
        await page.goto(`https://app.aiserviceco.com/v2/location/${locationId}/settings/funnels`, { waitUntil: 'networkidle2' });

        // Take a screenshot to show state
        await page.screenshot({ path: 'automation_status_funnels.png' });
        console.log("Screenshot saved: automation_status_funnels.png");

        // Attempt to find 'New Funnel' button
        // Need to be very careful with selectors here.
        // Often it's button with text "New Funnel"

        console.log("Searching for 'New Funnel' button...");
        try {
            await page.waitForSelector('button', { timeout: 10000 });
            const buttons = await page.$$('button');
            let clicked = false;
            for (const btn of buttons) {
                const text = await page.evaluate(el => el.textContent, btn);
                if (text?.includes('New Funnel')) {
                    console.log("Found New Funnel button! Clicking...");
                    await btn.click();
                    clicked = true;
                    break;
                }
            }

            if (!clicked) {
                console.log("New Funnel button NOT FOUND by text. Trying fallback selector...");
                // fallback?
                await page.screenshot({ path: 'missing_button.png' });
            } else {
                // Wait for modal
                console.log("Waiting for Create Funnel Modal...");
                await new Promise(r => setTimeout(r, 2000));
                await page.screenshot({ path: 'modal_reached.png' });
            }

        } catch (e: any) {
            console.error("Interaction failed:", e.message);
        }

    } catch (e) {
        console.error("Browser error:", e);
    } finally {
        // We leave it open for a bit so the user can "teach" if stuck
        console.log("Automation paused. Check screenshots or window.");
        await new Promise(r => setTimeout(r, 30000));
    }
}

run();
