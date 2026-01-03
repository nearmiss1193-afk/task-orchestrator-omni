import * as dotenv from 'dotenv';
import * as path from 'path';
import { ResearchAgent } from '../lib/research-agent';

// Load environment variables from .env.local
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function testAgent() {
    console.log('=== TESTING RESEARCH AGENT ===');
    const agent = new ResearchAgent();

    // Use a public tech/business website for testing
    const testUrl = 'https://www.openai.com';
    console.log(`Testing with URL: ${testUrl}`);

    try {
        // 1. Test Scraping
        const text = await agent.scrapeWebsite(testUrl);
        if (text) {
            console.log('\n[SCRAPE SUCCESS]');
            console.log('Text Content Sample:', text.substring(0, 500) + '...');
        } else {
            console.error('\n[SCRAPE FAILED] Check internet connection or site availability.');
            return;
        }

        // 2. Test Proposal Generation
        console.log('\nGenerating AI Proposal...');
        const proposal = await agent.generateProposal(text);
        console.log('\n[PROPOSAL GENERATED]');
        console.log('----------------------------');
        console.log(proposal);
        console.log('----------------------------');

    } catch (error: any) {
        console.error('Test failed:', error.message);
    }
}

testAgent();
