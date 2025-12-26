import { IntelPredator } from '../lib/intel-predator';

function testVibeScore() {
    console.log('🧪 Testing Vibe Score Logic...');
    const predator = new IntelPredator();

    const cases = [
        {
            name: 'Perfect Lead',
            features: { hasLeadMagnet: true, hasRecentReviews: true, mobileLoadSpeed: 'fast' as const },
            expected: 100
        },
        {
            name: 'No Magnet (-20)',
            features: { hasLeadMagnet: false, hasRecentReviews: true, mobileLoadSpeed: 'fast' as const },
            expected: 80
        },
        {
            name: 'No Reviews (-30)',
            features: { hasLeadMagnet: true, hasRecentReviews: false, mobileLoadSpeed: 'fast' as const },
            expected: 70
        },
        {
            name: 'Slow Mobile (-10)',
            features: { hasLeadMagnet: true, hasRecentReviews: true, mobileLoadSpeed: 'slow' as const },
            expected: 90
        },
        {
            name: 'Disaster Lead (-60 total)',
            features: { hasLeadMagnet: false, hasRecentReviews: false, mobileLoadSpeed: 'slow' as const },
            expected: 40
        }
    ];

    for (const c of cases) {
        const score = predator.calculateVibeScore(c.features);
        const pass = score === c.expected;
        console.log(`[${pass ? 'PASS' : 'FAIL'}] ${c.name}: Expected ${c.expected}, Got ${score}`);
    }
}

testVibeScore();
