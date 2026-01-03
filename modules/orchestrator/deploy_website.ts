
import { GHLBrowserConnector } from './lib/connectors/ghl-browser';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load env
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function run() {
    console.log("Starting Website Deployment...");

    if (!process.env.GHL_LOCATION_ID) {
        console.error("Error: GHL_LOCATION_ID not found in .env.local");
        process.exit(1);
    }
    console.log(`Target Location: ${process.env.GHL_LOCATION_ID}`);

    const browser = new GHLBrowserConnector();

    try {
        console.log("\n=== Creating Funnel and Landing Page ===");
        const result = await browser.execute('create_funnel_page', {
            name: "AI Service Co - Website",
            businessType: "Service" // Optional/Legacy param
        });

        console.log("\n✅ Website Container Deployed Successfully!");
        console.log("Result:", JSON.stringify(result, null, 2));

        console.log("\n⚠️  MANUAL ACTION REQUIRED ⚠️");
        console.log("1. Open the newly created funnel 'AI Service Co - Website' in GHL.");
        console.log("2. Edit the 'Landing Page' step.");
        console.log("3. Add a 'Custom HTML' element.");
        console.log("4. Paste the content of 'AI_SERVICE_CO_WEBSITE_COMPLETE.html' into the element.");
        console.log("5. Save and Preview.");

    } catch (error) {
        console.error("\n❌ Deployment Failed:", error);
    } finally {
        console.log("Exiting...");
        process.exit(0);
    }
}

run().catch(console.error);
