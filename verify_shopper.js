const puppeteer = require('puppeteer');

(async () => {
    console.log('🛒 INITIALIZING SHOPPER BOT: V3.0 (Strict Mode)');

    // HEADLESS must be false so user sees it, per request "shopper loop always includes local browser launched on my pc"
    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: null,
        args: ['--start-maximized']
    });

    const page = await browser.newPage();
    const TARGET = 'https://empire-sovereign-cloud.vercel.app/hvac.html';

    console.log(`🌐 CHECKING LIVE DEPLOYMENT: ${TARGET}`);
    await page.goto(TARGET, { waitUntil: 'domcontentloaded' });

    // 1. STRICT VERSION CHECK (VEO)
    const content = await page.content();
    if (!content.includes('Veo Visionary App')) {
        console.error('❌ CRITICAL FAILURE: Live Site is STALE.');
        console.error('   Expected: "Veo Visionary App" card.');
        console.error('   Found: Old Content.');

        // Visual Alert on page
        await page.evaluate(() => {
            document.body.innerHTML = '<h1 style="color:red; font-size:50px; text-align:center; margin-top:20%">❌ DEPLOYMENT FAILED<br>SITE IS STALE</h1>';
        });

        await new Promise(r => setTimeout(r, 5000));
        await browser.close();
        process.exit(1);
    }

    // 2. CHECK ENTERPRISE
    const entBtn = await page.$('a[href^="mailto:sales"]');
    if (!entBtn) {
        console.error('❌ CRITICAL FAILURE: Enterprise Button Missing.');
        await browser.close();
        process.exit(1);
    }

    // 3. SUCCESS DANCE
    console.log('✅ LIVE VERIFICATION PASSED: Site is Updated.');
    await page.evaluate(() => {
        // Scroll to catch user eye
        const el = document.querySelector('.bento-grid');
        if (el) el.scrollIntoView({ behavior: 'smooth' });

        // Highlight Success
        const banner = document.createElement('div');
        banner.style = 'position:fixed; top:0; left:0; width:100%; height:10px; background:#00ff00; z-index:9999';
        document.body.appendChild(banner);
    });

    await new Promise(r => setTimeout(r, 4000));
    await browser.close();
})();
