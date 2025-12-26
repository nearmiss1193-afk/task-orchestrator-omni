
const { MarketingAgent } = require('../lib/marketing-agent');
const dotenv = require('dotenv');

dotenv.config({ path: '.env.local' });

async function testMarketing() {
    console.log("🧪 Starting Marketing Agent Test (JS Version)...");
    const agent = new MarketingAgent();

    // 1. Manually trigger a Social Loop run
    console.log("\n--- Testing Social Loop ---");
    try {
        await agent.runSocialLoop();
    } catch (e) {
        console.error("Social Loop failed:", e.message);
    }

    // 2. Mock a lead and trigger enrichment
    console.log("\n--- Testing Content/Asset Loop ---");
    const mockLead = {
        id: 'test_lead_id_js',
        full_name: 'Near Miss JS Test',
        email: 'nearmiss1193+jstest@gmail.com',
        website_url: 'https://www.aiserviceco.com',
        ghl_contact_id: 'ghl_test_123_js'
    };

    try {
        await agent.enrichContact(mockLead);
    } catch (e) {
        console.error("Enrichment failed:", e.message);
    }

    console.log("\n✅ Test sequence complete.");
}

testMarketing().catch(console.error);
