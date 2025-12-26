
import axios from 'axios';
import * as path from 'path';
import * as dotenv from 'dotenv';
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function run() {
    const token = process.env.GHL_PRIVATE_KEY;
    const locationId = process.env.GHL_LOCATION_ID;

    if (!token || !locationId) {
        console.error("Missing credentials.");
        process.exit(1);
    }

    console.log("=== CREATING FUNNEL VIA API ===");
    console.log("Location:", locationId);

    // Try creating a funnel
    // Endpoint: https://services.leadconnectorhq.com/funnels/funnel/
    // This is a guess based on V2, usually /funnels/

    // Actually, official V2 might not support creating funnels programmatically effectively.
    // I will try to LIST funnels first to check access.

    try {
        const listRes = await axios.get('https://services.leadconnectorhq.com/funnels/funnel/', {
            params: { locationId },
            headers: {
                'Authorization': `Bearer ${token}`,
                'Version': '2021-07-28'
            }
        });

        console.log("Existing Funnels:", listRes.data.funnels?.length || 0);

        // If list works, try Create
        // Payload might be { name, locationId }
        const createPayload = {
            name: "AI Service Co - Website",
            locationId: locationId
        };

        console.log("Attempting creation...");
        const createRes = await axios.post('https://services.leadconnectorhq.com/funnels/funnel/', createPayload, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Version': '2021-07-28'
            }
        });

        console.log("Success! Funnel ID:", createRes.data.funnel?.id || createRes.data.id);

    } catch (e: any) {
        console.error("API Error:", e.message);
        if (e.response) {
            console.error("Status:", e.response.status);
            console.error("Data:", JSON.stringify(e.response.data));
        }
    }
}

run();
