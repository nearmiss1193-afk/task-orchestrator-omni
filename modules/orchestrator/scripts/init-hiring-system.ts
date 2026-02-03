import { GHLBrowserConnector } from '../lib/connectors/ghl-browser';
import * as dotenv from 'dotenv';
dotenv.config();

/**
 * MISSION: INITIALIZE HIRING INFRASTRUCTURE
 * This script ensures GHL is ready for Nick Saraev's Auto-Hiring System.
 */
async function main() {
    const ghl = new GHLBrowserConnector();
    console.log("🚀 Initializing Hiring Infrastructure in GHL...");

    try {
        // 1. Ensure Tags Exist
        console.log("-> Ensuring 'candidate' and 'hiring' tags exist...");
        await ghl.execute('create_tags', {
            tags: ['candidate', 'hiring', 'trial-sent', 'trial-passed']
        });

        // 2. Ensure Recruitment Pipeline Exists
        console.log("-> Ensuring 'Hiring & Recruitment' pipeline exists...");
        await ghl.execute('create_pipeline', {
            name: 'Elite Talent Pipeline',
            stages: [
                'Applied',
                'Trial Task Sent',
                'Trial Passed',
                'Interview Scheduled',
                'Hired/Onboarded',
                'Rejected'
            ]
        });

        console.log("✅ Hiring Infrastructure Ready.");
        process.exit(0);
    } catch (error) {
        console.error("❌ Setup Failed:", error);
        process.exit(1);
    }
}

main();
