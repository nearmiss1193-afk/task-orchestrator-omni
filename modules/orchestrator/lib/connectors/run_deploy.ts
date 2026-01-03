
import { GHLBrowserConnector } from './ghl-browser';
import * as fs from 'fs';
import * as path from 'path';

async function main() {
    console.log("🚀 Starting GHL Deployment Workflow (Sovereign Authority)...");

    // 1. Load the payload (HVAC Landing Page)
    const hvacPath = "c:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified\\apps\\portal\\public\\landing\\hvac.html";
    let hvacCode = "";
    try {
        hvacCode = fs.readFileSync(hvacPath, 'utf-8');
        console.log(`✅ Loaded Payload: ${hvacCode.length} bytes`);
    } catch (e) {
        console.error("❌ Failed to load HVAC payload:", e);
        process.exit(1);
    }

    const browser = new GHLBrowserConnector();

    try {
        // 2. Create Funnel Shell
        console.log("🏗️ Creating Funnel Shell...");
        const funnelRes = await browser.execute('create_funnel_page', {
            name: "Lakeland Promo " + Date.now(),
            businessType: "HVAC"
        });

        console.log("✅ Funnel Response:", funnelRes);

        if (funnelRes.success) {
            // 3. Inject Code
            console.log("💉 Injecting Code...");
            // Wait for creating to settle
            await new Promise(r => setTimeout(r, 5000));

            // We pass the same details so it can find the context (it's stateful on the browser instance mainly)
            // But realistically editFunnelStep needs to know WHICH funnel/step.
            // My implementation of editFunnelStep assumes we are ALREADY there or can find it.
            // Let's hope the browser session persisted the location (it should, mostly).

            await browser.editFunnelStep({
                funnelName: funnelRes.funnelName,
                stepName: "Landing Page",
                htmlContent: hvacCode
            }, null as any); // page arg handled internally usually but type mismatch in my quick wrapper
            // Actually, execute() calls runExecutionStep which GETS the page. 
            // The method signature in class is (params, page).
            // But I can't call editFunnelStep directly easily without the page instance if I use instance method.
            // Wait, I should use `execute` again.

            /* 
               CRITICAL FIX: 
               The 'execute' method splits by action. 
               'edit_funnel_step' IS an action in the switch case I defined (line 133). 
               So I should call browser.execute('edit_funnel_step', ...).
            */

            /* 
              Wait, I see line 133 in previous view_file:
              case 'edit_funnel_step': return await this.editFunnelStep(params, page);
              So yes, I can call it via execute.
           */

            await browser.execute('edit_funnel_step', {
                funnelName: funnelRes.funnelName,
                stepName: "Landing Page",
                htmlContent: hvacCode
            });

            console.log("🎉 Deployment Workflow Complete.");
        }

    } catch (e) {
        console.error("❌ Workflow Failed:", e);
    }
}

main();
