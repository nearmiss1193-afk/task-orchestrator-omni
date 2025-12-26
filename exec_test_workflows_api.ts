
import axios from 'axios';
import * as path from 'path';
import * as dotenv from 'dotenv';
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function run() {
    console.log("=== TESTING WORKFLOW API ===");
    const token = process.env.GHL_PRIVATE_KEY || process.env.GHL_API_TOKEN;
    const locationId = process.env.GHL_LOCATION_ID;

    if (!token || !locationId) {
        console.error("Missing credentials.");
        process.exit(1);
    }

    // 1. LIST Workflows (to verify scope)
    try {
        const listRes = await axios.get('https://services.leadconnectorhq.com/workflows/', {
            params: { locationId },
            headers: {
                'Authorization': `Bearer ${token}`,
                'Version': '2021-07-28'
            }
        });
        console.log(`[SUCCESS] Found ${listRes.data.workflows?.length || 0} workflows.`);

        // 2. Try CREATE Workflow (Experimental / documented but often limited)
        // Endpoint: POST /workflows/ (Sometimes this just creates a folder or basic shell)
        // Note: The public API for *defining* steps is mostly read-only or trigger-only.

        /* 
           Official V2 Spec often doesn't have POST /workflows with steps.
           But we will try a minimal payload.
        */

    } catch (e: any) {
        console.error(`[FAIL] List Workflows: ${e.message}`);
        if (e.response) {
            console.error("Status:", e.response.status);
            console.error("Data:", JSON.stringify(e.response.data));
        }
    }
}

run();
