
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const { name, phone, email, industry } = body;

        // Validate
        if (!phone) {
            return NextResponse.json({ error: "Phone required" }, { status: 400 });
        }

        const timestamp = new Date().toISOString();
        const logEntry = `[LEAD] ${timestamp} | ${industry || 'General'} | ${name} | ${phone} | ${email}\n`;

        // Log to Brain (Sovereign Database Placeholder)
        const logPath = path.join(process.cwd(), '../../../campaign_simulation_log.txt');
        fs.appendFileSync(logPath, logEntry);

        // Also Log to User Commands so Antigravity sees it
        const commandLogPath = path.join(process.cwd(), '../../../user_commands.log');
        fs.appendFileSync(commandLogPath, `[SYSTEM_ALERT] New Lead Received: ${name} (${industry})\n`);

        // 🔥 Phase 13: Trigger Onboarding Automation (SMS + DB)
        const { exec } = require('child_process');
        const triggerPath = path.join(process.cwd(), '../../../modules/communications/onboarding_trigger.py');
        const cmd = `python "${triggerPath}" "${phone}" "${name}" "${industry || 'General'}"`;

        exec(cmd, (error: any, stdout: any, stderr: any) => {
            if (error) {
                console.error(`[ONBOARDING_FAIL] ${error.message}`);
                return;
            }
            if (stderr) {
                console.error(`[ONBOARDING_STDERR] ${stderr}`);
                return;
            }
            console.log(`[ONBOARDING_SUCCESS] ${stdout}`);
        });

        return NextResponse.json({ success: true, message: "Lead Captured & Onboarding Initiated" });
    } catch (error) {
        console.error("Lead API Error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
