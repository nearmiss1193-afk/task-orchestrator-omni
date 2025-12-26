
import { MarketingAgent } from '../lib/marketing-agent';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

async function testMarketing() {
    console.log("🧪 Starting Marketing Agent Test...");
    const agent = new MarketingAgent();

    // 1. Manually trigger a Social Loop run
    console.log("\n--- Testing Social Loop ---");
    // @ts-ignore (Accessing private for test)
    await agent.runSocialLoop();

    // 2. Mock a lead and trigger enrichment (Content Loop logic)
    console.log("\n--- Testing Content/Asset Loop ---");
    const mockLead = {
        id: 'test_lead_id',
        full_name: 'Near Miss Test',
        email: 'nearmiss1193+test@gmail.com',
        website_url: 'https://www.aiserviceco.com',
        ghl_contact_id: 'ghl_test_123'
    };

    // @ts-ignore
    await agent.enrichContact(mockLead);

    console.log("\n✅ Test sequence complete.");
}

testMarketing().catch(console.error);
