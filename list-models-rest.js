
require('dotenv').config({ path: '.env.local' });
const axios = require('axios');

async function listModelsRest() {
    const apiKey = process.env.GOOGLE_API_KEY;
    const url = `https://generativelanguage.googleapis.com/v1/models?key=${apiKey}`;

    try {
        console.log("Fetching models from REST API...");
        const res = await axios.get(url);
        console.log("Models found:");
        res.data.models.forEach(m => console.log(`- ${m.name} (${m.supportedGenerationMethods})`));
    } catch (e) {
        console.error("REST Fetch failed:", e.message);
        if (e.response) console.log(JSON.stringify(e.response.data));
    }
}

listModelsRest();
