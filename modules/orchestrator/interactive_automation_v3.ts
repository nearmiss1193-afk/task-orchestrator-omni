
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import puppeteer from 'puppeteer';

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function run() {
    console.log("=== VERBOSE AUTOMATION v3 ===");
    console.log("Searching for session token across all possible GHL keys...");

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: null,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    try {
        const page = (await browser.pages())[0];
        await page.goto('https://app.aiserviceco.com/', { waitUntil: 'domcontentloaded' });

        const dumpSession = async () => {
            return await page.evaluate(() => {
                const results: any = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key && (key.includes('token') || key.includes('user') || key.includes('location'))) {
                        results[key] = localStorage.getItem(key);
                    }
                }
                return {
                    ls: results,
                    url: window.location.href,
                    cookies: document.cookie
                };
            });
        };

        let found = false;
        for (let i = 0; i < 300; i++) {
            const data = await dumpSession();
            // Look for anything that looks like a JWT or GHL token
            const token = data.ls['token'] || data.ls['ghl_token'] || data.ls['app_token'];

            if (token && data.url.includes('location')) {
                console.log("\n[SUCCESS] Token found in " + (data.url.includes('aiserviceco') ? 'WL Domain' : 'GHL Domain'));
                const sessionFile = {
                    token: token,
                    locationId: data.ls['location'] || data.url.split('location/')[1]?.split('/')[0],
                    all: data.ls
                };
                fs.writeFileSync('ghl_session_token.json', JSON.stringify(sessionFile, null, 2));
                console.log("Captured Token:", token.substring(0, 20) + "...");
                found = true;
                break;
            }
            if (i % 5 === 0) process.stdout.write(".");
            await new Promise(r => setTimeout(r, 2000));
        }

        if (found) {
            console.log("\nStarting Navigation to Funnels...");
            const session = JSON.parse(fs.readFileSync('ghl_session_token.json', 'utf8'));
            const locId = session.locationId;
            // Go directly to Funnels
            await page.goto(`https://app.aiserviceco.com/v2/location/${locId}/settings/funnels`, { waitUntil: 'networkidle2' });
            await page.screenshot({ path: 'funnels_page_v3.png' });
            console.log("Reached Funnels. Identifying buttons...");

            // Try to find the button more robustly
            const btnFound = await page.evaluate(() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const newFunnel = btns.find(b => b.textContent?.includes('New Funnel'));
                if (newFunnel) {
                    (newFunnel as HTMLElement).click();
                    return true;
                }
                return false;
            });

            if (btnFound) {
                console.log("Clicked New Funnel! Waiting for modal...");
                await new Promise(r => setTimeout(r, 3000));
                await page.screenshot({ path: 'new_funnel_modal_v3.png' });
            } else {
                console.log("New Funnel button NOT found. Listing all buttons for debug...");
                const buttonTexts = await page.evaluate(() => Array.from(document.querySelectorAll('button')).map(b => b.textContent));
                fs.writeFileSync('available_buttons.json', JSON.stringify(buttonTexts, null, 2));
            }
        }

    } catch (e) {
        console.error("Error:", e);
    } finally {
        console.log("Browser will stay open for 60s for you to see.");
        await new Promise(r => setTimeout(r, 60000));
        await browser.close();
    }
}

run();
