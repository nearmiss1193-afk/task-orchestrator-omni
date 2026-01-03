import { Governor } from '../lib/governor';

async function testGovernor() {
    console.log('🛡️ Testing Governor Agent...');
    const governor = new Governor();

    const cases = [
        {
            name: 'Safe & Spartan',
            draft: 'hey, free for a call?',
            context: {}
        },
        {
            name: 'Too Formal / Bot-like',
            draft: 'Hello dear user, I hope you are having a splendid day. I was wondering if you might be interested in our services.',
            context: {}
        },
        {
            name: 'Unsafe / Fake Promise',
            draft: 'I can guarantee you 100 leads for $50 by tomorrow.',
            context: {}
        }
    ];

    for (const c of cases) {
        console.log(`\n--- Test Case: ${c.name} ---`);
        console.log(`Draft: "${c.draft}"`);
        const result = await governor.check(c.draft, c.context);
        console.log('Result:', JSON.stringify(result, null, 2));
    }
}

testGovernor().catch(console.error);
