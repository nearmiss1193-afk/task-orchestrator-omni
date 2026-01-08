const { test, expect } = require('@playwright/test');

test('Landing Pages dropdown is visible and not obscured', async ({ page }) => {
    // Serve the dashboard locally (assumes python http server is running on port 8000)
    await page.goto('http://localhost:8000/public/dashboard.html');

    // Click the Landing Pages button
    const landingBtn = page.locator('button', { hasText: 'Landing Pages' });
    await landingBtn.click();

    // Wait for portal to become visible
    const portal = page.locator('#portalLanding');
    await expect(portal).toBeVisible({ timeout: 3000 });

    // Verify expected items exist
    const items = [
        '🔧 HVAC',
        '🔧 Plumber',
        '⚡ Electrician',
        '🏠 Roofer',
        '☀️ Solar',
        '🌿 Landscaping',
        '🧹 Cleaning',
        '🐜 Pest Control',
        '🔨 Restoration',
        '🚗 Auto Detail'
    ];
    for (const txt of items) {
        await expect(portal.locator('a', { hasText: txt })).toBeVisible();
    }
});
