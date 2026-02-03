import { IntelPredator } from '../lib/intel-predator';
import { IntelConnector } from '../lib/connectors/intel';
import * as dotenv from 'dotenv';
import * as path from 'path';
import * as fs from 'fs';

dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

async function runDossierMission() {
    const subject = "Seacost ALF";
    const company = "Seacost ALF Tampa";
    const context = "Elderly Care, Assisted Living Facility, Tampa Florida";

    console.log(`🚀 DEPLOYING INTEL PREDATOR: ${subject} @ ${company}`);

    const connector = new IntelConnector();
    const agent = new IntelPredator();

    // 1. Gather Data
    const researchData = await connector.execute('research_person', {
        name: subject,
        company: company,
        context: context
    });

    // 2. Synthesize
    console.log("🧠 Analyzing digital footprint...");
    const dossier = await agent.generateDossier({ name: subject, company: company }, researchData);

    // 3. Save to Brain
    const reportPath = 'C:\\Users\\nearm\\.gemini\\antigravity\\brain\\2627b6af-5a0d-436f-8c44-6df330e53044\\seacost_alf_dossier.md';
    fs.writeFileSync(reportPath, dossier);

    console.log(`\n🏆 MISSION COMPLETE. Dossier saved to: ${reportPath}`);
    console.log("\n------------------------------------------");
    console.log(dossier);
    console.log("------------------------------------------");
}

runDossierMission().catch(console.error);
