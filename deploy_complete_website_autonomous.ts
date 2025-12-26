
import { GHLBrowserConnector } from './lib/connectors/ghl-browser';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function deploy() {
    console.log("=== STARTING AUTONOMOUS WEBSITE DEPLOYMENT ===");

    // 1. Load HTML Content
    const htmlPath = path.resolve("C:/Users/nearm/.gemini/antigravity/brain/ca646f4c-f85e-4b78-9bf2-9630641244ad/AI_SERVICE_CO_WEBSITE_COMPLETE.html");
    if (!fs.existsSync(htmlPath)) {
        console.error("Critical Error: HTML Artifact not found at " + htmlPath);
        process.exit(1);
    }
    const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
    console.log(`Loaded HTML Content (${htmlContent.length} bytes).`);

    const browser = new GHLBrowserConnector();

    try {
        // 2. Create Funnel and Landing Page
        console.log("Step 1: Creating Funnel & Landing Page Structure...");
        const result = await browser.execute('create_funnel_page', {
            name: "AI Service Co - Website",
            businessType: "AI Agency"
        });

        if (result.success) {
            console.log("Funnel Structure Created Successfully:", result);

            // 3. Open Editor (Preparation for Injection)
            console.log("Step 2: Entering Funnel Editor...");
            const editResult = await browser.execute('edit_funnel_step', {
                funnelName: "AI Service Co - Website",
                stepName: "Landing Page",
                htmlContent: htmlContent // Passing it, even if just for context for now
            });
            console.log("Editor Status:", editResult);

            console.log("\nSUCCESS: Funnel and Page are ready.");
            console.log("The GHL Builder should now be open.");
            console.log("Due to GHL Builder complexity, the final HTML injection requires specific element placement.");
            console.log("The HTML content is available in the artifact.");

        } else {
            console.error("Funnel Creation Failed:", result);
        }

    } catch (e) {
        console.error("Deployment Failed:", e);
    } finally {
        // browser.close() is not exposed, but the script ending will kill it unless we want to keep it open.
        // We probably want to keep it open to see the result?
        // The script exits, which might close the browser if Puppeteer is child process.
        // But we launched it with `headless: false` in the class.
        // We'll let the process exit, but maybe add a delay so user can see.
        console.log("Session complete. Exiting script in 10 seconds...");
        await new Promise(r => setTimeout(r, 10000));
        process.exit(0);
    }
}

deploy();
