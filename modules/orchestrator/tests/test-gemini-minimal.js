
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config({ path: '.env.local' });

async function testSimple() {
    console.log("Testing with API Key:", process.env.GOOGLE_API_KEY ? "EXISTS" : "MISSING");
    const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

    const models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"];

    for (const modelName of models) {
        try {
            console.log(`--- Testing ${modelName} ---`);
            const model = genAI.getGenerativeModel({ model: modelName });
            const result = await model.generateContent("Say hello");
            console.log(`${modelName} Success:`, result.response.text());
        } catch (e) {
            console.error(`${modelName} Failed:`, e.message);
        }
    }
}

testSimple();
