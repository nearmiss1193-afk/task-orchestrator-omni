import { NeuralLink } from '../lib/neural-link';

async function testNeuralLink() {
    console.log('🧠 Testing Neural Link...');
    const link = new NeuralLink();

    // We can't really test live extraction without a real session, so this will likely fallback to default
    // or we can mock the extractActivity method if we wanted to unit test just the logic.
    // For now, let's see if it runs and handles the "no activity" case gracefully.

    const url = 'https://www.linkedin.com/in/test-user-123/';
    const hook = await link.extractActivity(url);

    console.log(`\nHook Result for ${url}:`);
    console.log(`"${hook}"`);
}

testNeuralLink().catch(console.error);
