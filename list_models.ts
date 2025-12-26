const { GoogleGenerativeAI } = require("@google/generative-ai");

async function listModels() {
    const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY || "");
    const models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"];

    for (const name of models) {
        try {
            const model = genAI.getGenerativeModel({ model: name });
            const result = await model.generateContent("hi");
            console.log(`OK: ${name}`);
        } catch (e) {
            console.log(`ERR: ${name} - ${e.message.substring(0, 50)}`);
        }
    }
}
listModels();
