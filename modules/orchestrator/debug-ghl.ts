
require('dotenv').config({ path: '.env.local' });
const axios = require('axios');

async function debug() {
    console.log("Debugging GHL API...");
    const token = process.env.GHL_PRIVATE_KEY || process.env.GHL_AGENCY_API_KEY;
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Version': '2021-07-28',
        'Content-Type': 'application/json'
    };

    const email = process.env.ADMIN_EMAIL || "test@test.com";
    console.log(`Target: ${email}`);

    // 1. Test Lookup
    try {
        console.log("1. Testing Lookup...");
        const res = await axios.get(`https://services.leadconnectorhq.com/contacts/search`, {
            params: { query: email, locationId: process.env.GHL_LOCATION_ID },
            headers
        });
        console.log("Lookup Success:", res.data);
    } catch (e: any) {
        console.error("Lookup Failed:", e.message);
        if (e.response) console.error("Lookup Response:", JSON.stringify(e.response.data));
    }

    // 2. Test Create (if lookup failed or just to test payload)
    try {
        console.log("2. Testing Create...");
        const payload = {
            locationId: process.env.GHL_LOCATION_ID,
            email: email,
            name: "Debug User",
            firstName: "Debug",
            lastName: "User",
            phone: "+15555555555" // GHL often requires phone
        };
        const res = await axios.post(`https://services.leadconnectorhq.com/contacts/`, payload, { headers });
        console.log("Create Success:", res.data);
    } catch (e: any) {
        console.error("Create Failed:", e.message);
        if (e.response) console.error("Create Response:", JSON.stringify(e.response.data));
    }

    // 3. Test Send Email
    try {
        console.log("3. Testing Send Email...");
        // Use ID from lookup or create if available, else hardcode one from log if possible
        // For automation, re-lookup
        const lookup = await axios.get(`https://services.leadconnectorhq.com/contacts/search?query=${email}&locationId=${process.env.GHL_LOCATION_ID}`, { headers });
        const contactId = lookup.data.contacts[0].id;
        console.log(`Using Contact ID: ${contactId}`);

        const msgPayload = {
            type: 'Email',
            contactId: contactId,
            message: "Test body from Debug Script",
            subject: "Debug Subject",
            html: "<p>Test body</p>"
        };
        const res = await axios.post(`https://services.leadconnectorhq.com/conversations/messages`, msgPayload, { headers });
        console.log("Send Email Success:", res.data);
    } catch (e: any) {
        console.error("Send Email Failed:", e.message);
        if (e.response) console.error("Send Email Response:", JSON.stringify(e.response.data));
    }
}

debug();
