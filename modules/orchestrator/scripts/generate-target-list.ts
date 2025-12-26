
import { IntelPredator } from '../lib/intel-predator';
import * as fs from 'fs';
import * as path from 'path';
import * as dotenv from 'dotenv';

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function generateComprehensiveTargetList() {
    console.log("🕵️ Generating 100-Target Empire List...");

    const predator = new IntelPredator();
    const cities = ["Tampa", "Austin", "Miami", "Houston", "Dallas"];
    const niches = ["Locksmith", "Plumber", "HVAC", "Towing", "Electrician"];

    const fullList: any[] = [];

    for (const city of cities) {
        for (const niche of niches) {
            // Generate 4 targets per niche per city = 100
            for (let i = 1; i <= 4; i++) {
                const companyName = `${city} ${niche} Pros #${i}`;
                const website = `https://${companyName.toLowerCase().replace(/ /g, '')}.com`;
                const ownerName = `Elite Owner ${i}`;

                console.log(`🔍 Researching ${companyName}...`);

                // Using the predator to simulate/generate a dossier for the proposal
                const dossier = await predator.generateDossier(
                    { name: ownerName, company: companyName },
                    { website, city, niche, strategy: "Missed Call ROI" }
                );

                fullList.push({
                    id: fullList.length + 1,
                    city,
                    niche,
                    companyName,
                    website,
                    ownerName,
                    dossier
                });
            }
        }
    }

    const outputPath = path.resolve(process.cwd(), 'empire_target_batch_100.json');
    fs.writeFileSync(outputPath, JSON.stringify(fullList, null, 2));
    console.log(`✅ Master List Generated: ${outputPath}`);
}

generateComprehensiveTargetList().catch(console.error);
