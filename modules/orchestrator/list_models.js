
const { GoogleGenerativeAI } = require("@google/generative-ai");
require('dotenv').config({ path: '.env.local' });

async function listModels() {
    const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY || "");

    // We try to use a model that is typically available.
    const modelsToTry = ["gemini-pro", "gemini-1.5-flash", "models/gemini-1.5-flash", "models/gemini-pro"];

    console.log("Checking API Key: " + (process.env.GOOGLE_API_KEY ? "Present" : "Missing"));

    for (const modelName of modelsToTry) {
        console.log(`Testing model: ${modelName}...`);
        try {
            const model = genAI.getGenerativeModel({ model: modelName });
            const result = await model.generateContent("Hello");
            const response = await result.response;
            console.log(`✅ SUCCESS: ${modelName} works!`);
            return;
        } catch (error) {
            console.log(`❌ FAILED: ${modelName}. Error: ${error.message}`);
        }
    }
}

listModels();
