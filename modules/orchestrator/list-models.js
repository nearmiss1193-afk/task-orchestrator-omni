
require('dotenv').config({ path: '.env.local' });
const { GoogleGenerativeAI } = require('@google/generative-ai');

async function listModels() {
    const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
    try {
        console.log("Listing models...");
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
        const result = await model.generateContent("Hello");
        console.log("Flash response:", result.response.text());
        console.log("gemini-1.5-flash is AVAILABLE");
    } catch (e) {
        console.error("Flash failed:", e.message);
    }

    try {
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro" });
        const result = await model.generateContent("Hello");
        console.log("Pro response:", result.response.text());
        console.log("gemini-1.5-pro is AVAILABLE");
    } catch (e) {
        console.error("Pro failed:", e.message);
    }
}

listModels();
