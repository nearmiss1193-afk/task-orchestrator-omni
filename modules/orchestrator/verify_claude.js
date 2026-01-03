require('dotenv').config({ path: '.env.local' });
const Anthropic = require('@anthropic-ai/sdk');

async function testClaude() {
    console.log("TESTING CLAUDE (Anthropic)...");
    const key = process.env.ANTHROPIC_API_KEY;
    if (!key) { console.log("NO CLAUDE KEY"); return; }

    try {
        const anthropic = new Anthropic({ apiKey: key });
        const msg = await anthropic.messages.create({
            model: "claude-3-5-sonnet-20240620",
            max_tokens: 10,
            messages: [{ role: "user", content: "Hello" }]
        });
        console.log(`RESULT: ${msg.content[0].text}`);
        console.log("✅ CLAUDE IS ONLINE");
    } catch (e) {
        console.log(`ERROR: ${e.message}`);
    }
}
testClaude();
