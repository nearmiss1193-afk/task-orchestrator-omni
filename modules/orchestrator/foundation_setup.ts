
import { GHLBrowserConnector } from './lib/connectors/ghl-browser';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load env
dotenv.config({ path: path.resolve(__dirname, '.env.local') });

async function run() {
    console.log("Starting Foundation Setup...");

    if (!process.env.GHL_LOCATION_ID) {
        console.error("Error: GHL_LOCATION_ID not found in .env.local");
        process.exit(1);
    }
    console.log(`Target Location: ${process.env.GHL_LOCATION_ID}`);

    const browser = new GHLBrowserConnector();

    try {
        // 1. Create Pipeline
        console.log("\n=== 1. Creating Pipeline ===");
        await browser.execute('create_pipeline', {
            name: "AI Service Co - Sales Pipeline",
            stages: [
                "New Lead",
                "Contacted",
                "Demo Scheduled",
                "Demo Completed",
                "Proposal Sent",
                "Negotiation",
                "Won - Customer",
                "Lost",
                "Nurture"
            ]
        });

        // 2. Create Tags
        console.log("\n=== 2. Creating Tags ===");
        const tags = [
            "ai-service-lead", "cold-outreach", "engaged", "engaged-sms", "hot-lead", "warm-lead", "cold-lead",
            "welcome-sent", "7-day-nurture-complete", "30-day-nurture-complete", "60-day-nurture-complete", "90-day-nurture-complete",
            "cold-sequence-complete", "proposal-sent", "proposal-stalled",
            "demo-booked", "demo-completed", "no-show",
            "customer", "active-customer", "onboarding", "30-day-customer",
            "do-not-sms", "opted-out", "do-not-call"
        ];

        await browser.execute('create_tags', { tags });

        console.log("\n✅ Foundation Setup Complete!");

    } catch (error) {
        console.error("\n❌ Setup Failed:", error);
    } finally {
        // We might want to close the browser explicitly here if the connector exposed it, but 
        // the connector manages it. The process exit will kill it.
        console.log("Exiting...");
        process.exit(0);
    }
}

run().catch(console.error);
