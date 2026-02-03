const puppeteer = require('puppeteer');

(async () => {
    console.log('🛒 INITIALIZING VISUAL SHOPPER (Live User View)...');
    // Launch with Headless: FALSE to show browser on user's PC
    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: null, // Full width
        args: ['--start-maximized', '--window-size=1920,1080']
    });

    const page = await browser.newPage();

    // LIVE URL Verification
    const TARGET = 'https://empire-sovereign-cloud.vercel.app/hvac.html';
    console.log(`🌐 NAVIGATING TO: ${TARGET}`);

    await page.goto(TARGET, { waitUntil: 'domcontentloaded' });

    console.log('👀 Visual Inspection: Scrolling for User...');

    // Smooth scroll to Features (Veo check)
    await page.evaluate(() => {
        document.getElementById('features').scrollIntoView({ behavior: 'smooth' });
    });
    await new Promise(r => setTimeout(r, 2000)); // Wait for user to see

    // Scroll to Pricing (Enterprise check)
    await page.evaluate(() => {
        document.getElementById('pricing').scrollIntoView({ behavior: 'smooth' });
    });
    await new Promise(r => setTimeout(r, 2000));

    // Check for Veo
    const content = await page.content();
    if (content.includes('Veo Visionary')) {
        console.log('✅ Veo Feature: DETECTED');
    } else {
        console.warn('⚠️ Veo Feature: NOT FOUND on Live Site');
    }

    // Check for Enterprise
    const entBtn = await page.$('a[href^="mailto:sales"]');
    if (entBtn) {
        console.log('✅ Enterprise Button: DETECTED');
        // Highlight it
        await page.evaluate((btn) => {
            btn.style.border = '5px solid #00ff00';
            btn.style.transform = 'scale(1.2)';
        }, entBtn);
    } else {
        console.warn('⚠️ Enterprise Button: NOT FOUND');
    }

    await new Promise(r => setTimeout(r, 5000)); // Keep open for 5s
    await browser.close();
    console.log('🛒 VISUAL AUDIT COMPLETE.');
})();
