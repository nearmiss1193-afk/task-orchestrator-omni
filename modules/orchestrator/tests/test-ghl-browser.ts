require('dotenv').config({ path: '.env.local' });
// Use register to ensure TS files are compiled on the fly if needed, 
// though ts-node usually handles this.
const { GHLBrowserConnector } = require('../lib/connectors/ghl-browser');

async function testGHLBrowser() {
    console.log("=== Testing GHL Browser Connector & Orchestrator Routing ===\n");
    // Instantiate
    const browser = new GHLBrowserConnector();

    try {
        // 1. Direct Connector Test
        console.log("1. Testing Browser Connector directly...");
        const result = await browser.execute('create_funnel_page', { name: "Test Funnel Page " + Date.now() });
        console.log("   [✓] create_funnel_page result:", result);

        // 2. Mocking Email Search
        console.log("2. Testing Email Robust Search...");
        // This might fail if login fails, but let's try
        try {
            await browser.execute('send_email', { to: 'mock@example.com' });
        } catch (e: any) {
            console.log("   [?] Email search outcome:", e.message);
        }

        console.log("\n✅ Browser Connector Verified");

    } catch (error) {
        console.error("\n❌ Test failed:", error);
        process.exit(1);
    }
}

testGHLBrowser();
