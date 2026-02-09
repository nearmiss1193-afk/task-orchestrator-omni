
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// ==========================================
// BaseConnector
// ==========================================
class BaseConnector {
    validate(action, params) {
        return true;
    }

    log(message) {
        console.log(`[${this.name}] ${message}`);
    }
}

// ==========================================
// GHLBrowserConnector
// ==========================================
class GHLBrowserConnector extends BaseConnector {
    constructor() {
        super();
        this.name = 'GHL_Browser';
        this.maxTabs = 10;
        this.browser = null; // Instance ref
    }

    // Singleton Management
    static sharedBrowser = null;

    async execute(action, params) {
        this.log(`[Browser] Executing ${action} with params: ${JSON.stringify(params)}`);

        try {
            await this.ensureBrowser();

            switch (action) {
                case 'create_funnel_page':
                    return await this.createFunnelPage(params, await this.getTab());
                case 'edit_funnel_step':
                    return await this.editFunnelStep(params, await this.getTab());
                default:
                    throw new Error(`Browser Client Action ${action} not implemented`);
            }
        } catch (error) {
            this.log(`[Browser] Error: ${error.message}`);
            throw error;
        }
    }

    async ensureBrowser() {
        if (!GHLBrowserConnector.sharedBrowser) {
            this.log("[Browser] Launching Singleton Puppeteer Instance...");
            const userDataDir = path.join(process.cwd(), '.ghl_browser_data');
            if (!fs.existsSync(userDataDir)) fs.mkdirSync(userDataDir, { recursive: true });

            const lockFile = path.join(userDataDir, 'SingletonLock');
            if (fs.existsSync(lockFile)) {
                try { fs.unlinkSync(lockFile); } catch (e) { }
            }

            GHLBrowserConnector.sharedBrowser = await puppeteer.launch({
                headless: false,
                defaultViewport: null,
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--window-size=1280,800',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars'
                ],
                userDataDir: userDataDir,
                ignoreDefaultArgs: ["--enable-automation"]
            });

            // Auth Setup
            const pages = await GHLBrowserConnector.sharedBrowser.pages();
            const authPage = pages[0];
            await this.setupStealth(authPage);
            await this.performExecutionLogin(authPage);
        }
        this.browser = GHLBrowserConnector.sharedBrowser;
    }

    async setupStealth(page) {
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        await page.evaluateOnNewDocument(() => {
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
        });
    }

    async getTab() {
        if (!this.browser) await this.ensureBrowser();
        const pages = await this.browser.pages();

        if (pages.length >= this.maxTabs) {
            this.log(`[Browser] Tab limit (${this.maxTabs}) reached. Reusing last tab.`);
            return pages[pages.length - 1];
        }

        const newPage = await this.browser.newPage();
        await this.setupStealth(newPage);
        return newPage;
    }

    async performExecutionLogin(page) {
        this.log("[Browser] Verifying/Performing Login...");
        constloginUrl = 'https://app.gohighlevel.com/';
        // Check if already logged in by navigating
        // If we are already on a location page, we are good.
        // But safe to just goto loginUrl.

        await page.goto(loginUrl, { waitUntil: 'domcontentloaded' });

        // Check URL
        if (page.url().includes('location') || page.url().includes('dashboard')) {
            this.log("[Browser] Already logged in.");
            return;
        }

        const email = process.env.GHL_EMAIL;
        const password = process.env.GHL_PASSWORD;

        // Only type if inputs exist
        try {
            const emailInput = await page.waitForSelector('input[type="email"]', { timeout: 5000 });
            if (emailInput && email && password) {
                await page.type('input[type="email"]', email);
                await page.type('input[type="password"]', password);
                await page.click('button[type="submit"], .btn-login');
                await page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => { });
            }
        } catch (e) {
            // Might be already logged in or different page
        }
    }

    // ==========================================
    // ACTIONS
    // ==========================================

    async createFunnelPage({ name, businessType }, page) {
        this.log(`[GHL_Browser] Creating Funnel: ${name}...`);

        // 1. Navigate to Funnels
        const envLocationId = process.env.GHL_LOCATION_ID;
        let targetUrl = "https://app.gohighlevel.com";
        if (envLocationId) {
            // Logic to construct URL if possible, else standard nav
            // Using simple redirect base
            // Actually, cleaner to just click Sidebar if URL logic is complex
        }

        // Try sidebar navigation first as fallback
        try {
            // Find "Sites" or "Funnels"
            // Wait for sidebar
            await page.waitForSelector('#sb_sites, a[href*="funnels"]', { timeout: 15000 }).catch(() => { });

            // Navigate directly if we can guess url
            if (envLocationId) {
                await page.goto(`https://app.gohighlevel.com/v2/location/${envLocationId}/funnels/funnel`, { waitUntil: 'networkidle2' });
            } else {
                // Try clicking
                await page.click('#sb_sites').catch(() => { });
            }
        } catch (e) { }

        await new Promise(r => setTimeout(r, 5000));

        // 2. Click "New Funnel"
        let newFunnelClicked = false;
        try {
            // Close modals
            await page.evaluate(() => {
                document.querySelectorAll('.modal .close').forEach(el => el.click());
            });

            newFunnelClicked = await page.evaluate(() => {
                const buttons = Array.from(document.querySelectorAll('button, a'));
                const btn = buttons.find(b => b.textContent.toLowerCase().includes('new funnel') || b.textContent.toLowerCase().includes('create funnel'));
                if (btn) { btn.click(); return true; }
                return false;
            });
        } catch (e) { }

        if (!newFunnelClicked) {
            // Try header action
            await page.click('.header-actions button').catch(() => { });
        }

        await new Promise(r => setTimeout(r, 2000));

        // 3. "From Scratch"
        await page.evaluate(() => {
            const els = Array.from(document.querySelectorAll('div, span, h4'));
            const target = els.find(e => e.textContent.toLowerCase().includes('from scratch'));
            if (target) target.click();
        });

        await new Promise(r => setTimeout(r, 1000));

        // Start Building / Continue
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const btn = btns.find(b => b.textContent.toLowerCase().includes('start') || b.textContent.toLowerCase().includes('continue'));
            if (btn) btn.click();
        });

        // 4. Name It
        const inputSel = 'input[placeholder*="Name"], input[name="name"]';
        await page.waitForSelector(inputSel, { timeout: 5000 }).catch(() => { });
        await page.type(inputSel, name).catch(() => { });

        // Create
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const btn = btns.find(b => b.textContent.trim().toLowerCase() === 'create');
            if (btn) btn.click();
        });

        await new Promise(r => setTimeout(r, 8000));

        // 5. Add Step
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const btn = btns.find(b => b.textContent.toLowerCase().includes('add new step') || b.textContent.toLowerCase().includes('add step'));
            if (btn) btn.click();
        });

        await new Promise(r => setTimeout(r, 2000));

        const stepNameInput = "input[placeholder*='Name']";
        const stepPathInput = "input[placeholder*='Path']";

        await page.waitForSelector(stepNameInput, { timeout: 5000 }).catch(() => { });
        await page.type(stepNameInput, "Landing Page").catch(() => { });
        await page.type(stepPathInput, "landing-" + Date.now()).catch(() => { });

        // Create Step
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const btn = btns.find(b => b.textContent.toLowerCase().includes('create funnel step') || b.textContent.toLowerCase().includes('create step'));
            if (btn) btn.click();
        });

        this.log("[GHL_Browser] Funnel + Step Created.");
        return { success: true, funnelName: name };
    }

    async editFunnelStep({ funnelName, stepName, htmlContent }, page) {
        this.log(`[GHL_Edit] Opening Editor for ${stepName}...`);

        await new Promise(r => setTimeout(r, 3000));

        // 1. Click "Edit" -> "Edit Page"
        const editClicked = await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button, a'));
            const edit = btns.find(b => b.textContent.trim() === 'Edit');
            if (edit) { edit.click(); return true; }
            return false;
        });

        if (editClicked) {
            await new Promise(r => setTimeout(r, 1000));
            // Find "Edit Page" in dropdown
            await page.evaluate(() => {
                const links = Array.from(document.querySelectorAll('a, div'));
                const target = links.find(l => l.textContent.includes('Edit Page'));
                if (target) target.click();
            });
        }

        // 2. Wait for Builder
        this.log("[GHL_Edit] Waiting for Builder Canvas...");
        try {
            await page.waitForSelector('.builder-canvas, #app, .editor-canvas', { timeout: 45000 });
        } catch (e) {
            // Handle new tab
            const pages = await page.browser().pages();
            const lastPage = pages[pages.length - 1];
            if (lastPage !== page) {
                page = lastPage;
                await page.waitForSelector('.builder-canvas, #app', { timeout: 45000 });
            }
        }

        await new Promise(r => setTimeout(r, 5000));

        // 3. Add Custom HTML Element
        this.log("[GHL_Edit] Adding Custom HTML Element...");

        // Open Elements "Plus"
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button, .icon-btn'));
            const plus = btns.find(b => b.innerHTML.includes('fa-plus') || b.textContent.includes('Add element'));
            if (plus) plus.click();
        });

        await new Promise(r => setTimeout(r, 2000));

        // Click "Custom JS/HTML"
        const added = await page.evaluate(() => {
            const items = Array.from(document.querySelectorAll('.element-item, .item, div'));
            const target = items.find(i => i.textContent.includes('Custom JS/HTML') || i.textContent.includes('Code'));
            if (target) { target.click(); return true; }
            return false;
        });

        if (!added) {
            this.log("[GHL_Edit] Could not find Custom JS/HTML element button.");
            return { success: false };
        }

        await new Promise(r => setTimeout(r, 3000));

        // 4. Open Code Editor (Sidebar)
        this.log("[GHL_Edit] Opening Code Editor...");
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const target = btns.find(b => b.textContent.includes('Open Code Editor'));
            if (target) target.click();
        });

        await new Promise(r => setTimeout(r, 2000));

        // 5. Paste Code
        this.log("[GHL_Edit] Pasting Content...");
        await page.evaluate((content) => {
            // Try standard textarea first (CodeMirror often uses a hidden textarea or contenteditable)
            const textareas = document.querySelectorAll('textarea');
            // often the ace editor or monaco has a class
            const editorArea = document.querySelector('.ace_text-input') || document.querySelector('textarea.code-editor') || textareas[textareas.length - 1];

            if (editorArea) {
                editorArea.value = content;
                editorArea.dispatchEvent(new Event('input', { bubbles: true }));
                editorArea.focus();
                // Simulate keystroke if needed?
            }

            // Fallback: If global ace exposed
            // @ts-ignore
            if (window.ace && window.ace.edit) {
                // @ts-ignore
                const editor = window.ace.edit(document.querySelector('.ace_editor'));
                editor.setValue(content);
            }
        }, htmlContent);

        await new Promise(r => setTimeout(r, 1000));

        // 6. Save Code
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const save = btns.find(b => b.textContent.trim() === 'Yes, Save' || b.textContent.trim() === 'Save');
            if (save) save.click();
        });

        await new Promise(r => setTimeout(r, 2000));

        // 7. Save Page
        this.log("[GHL_Edit] Saving Page...");
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const save = btns.find(b => b.textContent.trim() === 'Save');
            if (save) save.click();
        });

        await new Promise(r => setTimeout(r, 5000));
        this.log("[GHL_Edit] DONE. Page Saved.");
        return { success: true };
    }
}

// ==========================================
// MAIN EXECUTION
// ==========================================
(async () => {
    console.log("🚀 Launching GHL Standalone Deployment...");

    // Load Payload
    const hvacPath = "c:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified\\apps\\portal\\public\\landing\\hvac.html";
    let hvacCode = "";
    try {
        hvacCode = fs.readFileSync(hvacPath, 'utf-8');
    } catch (e) {
        console.error("Failed to load payload", e);
        process.exit(1);
    }

    const connector = new GHLBrowserConnector();

    try {
        // Create Funnel
        const funnel = await connector.execute('create_funnel_page', {
            name: "Lakeland Promo " + Date.now(),
            businessType: "HVAC"
        });

        if (funnel.success) {
            // Edit Step
            await connector.execute('edit_funnel_step', {
                funnelName: funnel.funnelName,
                stepName: "Landing Page",
                htmlContent: hvacCode
            });
        }

    } catch (e) {
        console.error("Execution Failed:", e);
    }

    // Keep open specifically for debugging? Or close?
    // User wants "test him out", seeing the browser stay open or finish is fine.
    // process.exit(0);
})();
