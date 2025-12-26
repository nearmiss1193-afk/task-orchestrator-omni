
require('dotenv').config({ path: '.env.local' });
const { GoogleGenerativeAI } = require('@google/generative-ai');

async function listModels() {
    const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
    try {
        // The SDK doesn't have a direct listModels but we can use the REST API via fetch if needed
        // However, let's try some common variations first or use the v1 API
        console.log("Listing models via Fetch...");
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${process.env.GOOGLE_API_KEY}`);
        const data = await response.json();
        console.log(JSON.stringify(data, null, 2));
    } catch (e) {
        console.error("Error:", e);
    }
}

listModels();
