import { IntelPredator } from '../lib/intel-predator';
import { IntelConnector } from '../lib/connectors/intel';
import * as dotenv from 'dotenv';
import * as path from 'path';

dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

async function testIntelPredator() {
    console.log("🚀 Testing Intel Predator Agent...");

    const connector = new IntelConnector();
    const agent = new IntelPredator();

    const personInfo = {
        name: "John Doe",
        company: "Acme Corp"
    };

    console.log(`🕵️ Subject: ${personInfo.name} (${personInfo.company})`);

    // 1. Gather Data via Connector
    const researchData = await connector.execute('research_person', {
        name: personInfo.name,
        company: personInfo.company,
        context: "CEO"
    });

    console.log("✅ Research Data Gathered.");

    // 2. Synthesize Dossier via Agent
    console.log("🧠 Synthesizing Dossier...");
    const dossier = await agent.generateDossier(personInfo, researchData);

    console.log("\n🏆 FINAL DOSSIER:");
    console.log("------------------------------------------");
    console.log(dossier);
    console.log("------------------------------------------");

    const fs = require('fs');
    fs.writeFileSync('dossier_output.txt', dossier);
    console.log("✅ Dossier saved to dossier_output.txt");
}

testIntelPredator().catch(err => {
    console.error("❌ Test Failed:", err);
});
