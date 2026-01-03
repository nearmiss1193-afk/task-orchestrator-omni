
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';
import puppeteer from 'puppeteer';

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function run() {
    console.log("=== VERBOSE AUTOMATION v4 ===");
    console.log("1. Browser will open.");
    console.log("2. PLEASE LOG IN and navigate to the SUB-ACCOUNT.");
    console.log("3. I am looking for your Session Token (JWT).");

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: null,
        userDataDir: path.resolve(process.cwd(), '.ghl_temp_profile_' + Date.now()),
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });

    try {
        const page = (await browser.pages())[0];

        // Use the white label URL
        await page.goto('https://app.aiserviceco.com/', { waitUntil: 'domcontentloaded' });

        const dumpSessionData = async () => {
            return await page.evaluate(() => {
                const ls: any = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key) ls[key] = localStorage.getItem(key);
                }
                return {
                    ls: ls,
                    cookies: document.cookie,
                    url: window.location.href,
                    keys: Object.keys(ls)
                };
            });
        };

        let foundToken = null;
        let foundLoc = null;

        console.log("Monitoring Storage...");
        for (let i = 0; i < 600; i++) { // 20 minutes
            const data = await dumpSessionData();

            if (i % 5 === 0) {
                console.log(`\n[HEARTBEAT] URL: ${data.url}`);
                console.log(`[HEARTBEAT] LS Keys: ${data.keys.slice(0, 20).join(", ")}`);
                // Check if token exists in any key
                const tokenKey = data.keys.find(k => k.toLowerCase().includes('token'));
                if (tokenKey) console.log(`[HEARTBEAT] Potential Token Key Found: ${tokenKey}`);
            }

            // Exhaustive search for token
            const allStorage = { ...data.ls };
            let token = allStorage['token'] || allStorage['ghl_token'] || allStorage['app_token'] || allStorage['auth_token'] || allStorage['accessToken'];

            if (!token) {
                for (const key in allStorage) {
                    const val = allStorage[key];
                    if (typeof val === 'string' && val.startsWith('eyJ') && val.split('.').length === 3) {
                        token = val;
                        console.log(`[HEARTBEAT] Snapped JWT from key: ${key}`);
                        break;
                    }
                }
            }

            if (token && (data.url.includes('location') || allStorage['location'])) {
                foundToken = token;
                foundLoc = allStorage['location'] || data.url.split('location/')[1]?.split('/')[0];

                if (foundToken && foundLoc) {
                    console.log("\n[SUCCESS] Captured Token and Location ID.");
                    fs.writeFileSync('ghl_session_token.json', JSON.stringify({
                        token: foundToken,
                        locationId: foundLoc,
                        url: data.url
                    }, null, 2));
                    break;
                }
            }

            if (i % 10 === 0) process.stdout.write(".");
            await new Promise(r => setTimeout(r, 2000));
        }

        if (foundToken && foundLoc) {
            console.log("\n=== STAGE 2: NAVIGATING TO SITES ===");
            // Move to Funnels
            await page.goto(`https://app.aiserviceco.com/v2/location/${foundLoc}/settings/funnels`, { waitUntil: 'networkidle2' });
            await new Promise(r => setTimeout(r, 5000));
            await page.screenshot({ path: 'auto_v4_funnels.png' });

            console.log("Attempting to click 'New Funnel' button...");
            const clicked = await page.evaluate(() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const target = btns.find(b => b.textContent?.toLowerCase().includes('new funnel'));
                if (target) {
                    (target as HTMLElement).click();
                    return true;
                }
                return false;
            });

            if (clicked) {
                console.log("Clicked! Waiting for name input...");
                await new Promise(r => setTimeout(r, 3000));
                await page.screenshot({ path: 'auto_v4_modal.png' });

                // Type name
                await page.type('input[placeholder="Funnel Name"]', "AI Service Co - Website");
                await new Promise(r => setTimeout(r, 1000));

                // Click 'Create'
                await page.evaluate(() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const create = btns.find(b => b.textContent?.toLowerCase().includes('create'));
                    if (create) (create as HTMLElement).click();
                });

                console.log("Funnel created. Pausing for 30s for verification.");
            } else {
                console.log("Button not found. Check auto_v4_funnels.png");
            }
        }

    } catch (e) {
        console.error("Error:", e);
    } finally {
        console.log("Keeping browser open for 60s...");
        await new Promise(r => setTimeout(r, 60000));
        await browser.close();
    }
}

run();
