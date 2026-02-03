
import { GHLBrowserConnector } from './lib/connectors/ghl-browser';
import * as dotenv from 'dotenv';
import * as path from 'path';

dotenv.config({ path: path.resolve(__dirname, '.env.local') });

async function run() {
    const browser = new GHLBrowserConnector();
    console.log("Verifying Foundation...");
    try {
        const result = await browser.execute('audit_account', {});
        console.log("Audit Result:", JSON.stringify(result, null, 2));
    } catch (e) {
        console.error("Verification Exec Failed:", e);
    }
    process.exit(0);
}
run();
