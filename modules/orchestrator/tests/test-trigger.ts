import { TriggerAgent } from '../lib/trigger-agent';

async function testTrigger() {
    console.log('🧪 Testing Trigger Agent...');
    const agent = new TriggerAgent();

    // Test Mock
    const leads = await agent.scanForTriggers("Plumbers", "Tampa");
    console.log(`Found ${leads.length} leads:`);
    console.log(JSON.stringify(leads, null, 2));

    if (leads.find(l => l.company === "Apex Plumbing")) {
        console.log("✅ Mock Fallback Successfully Triggered");
    } else {
        console.log("❌ Mock Failed");
    }
}

testTrigger();
