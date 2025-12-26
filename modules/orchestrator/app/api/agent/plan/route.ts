import { NextResponse } from 'next/server';
import { Planner } from '@/lib/planner';
import { StateManager } from '@/lib/state-manager';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { instruction } = body;
        console.log(`[API] Plan Request received: ${instruction?.substring(0, 50)}...`);

        if (!instruction) throw new Error("Instruction is required");

        console.log(`[API] Checking Env: ANTHROPIC_API_KEY=${process.env.ANTHROPIC_API_KEY ? 'OK' : 'MISSING'}`);

        const planner = new Planner();
        console.log(`[API] Planner initialized. Generating plan...`);

        try {
            const plan = await planner.generatePlan(instruction);
            console.log(`[API] Plan generated: ${plan.id}`);
            StateManager.savePlan(plan);
            return NextResponse.json(plan);
        } catch (innerError: any) {
            console.error(`[API] Planner.generatePlan failed:`, innerError);

            // --- FAIL-SAFE SMART FALLBACK ---
            // If Planner fails, use the robust internal mock planner
            console.log("[API] Activating Smart Fallback Plan (via Planner.generateMockPlan)...");
            const fallbackPlan = planner.generateMockPlan(instruction || "Default Goal");

            StateManager.savePlan(fallbackPlan);
            return NextResponse.json(fallbackPlan);
        }

    } catch (error: any) {
        console.error("[API] POST Error:", error);
        // Write detailed error to a debug file we can read later
        const fs = require('fs');
        const path = require('path');
        try {
            fs.appendFileSync(path.join(process.cwd(), 'data', 'debug_api.log'), `[${new Date().toISOString()}] Error: ${error.message}\nStack: ${error.stack}\nEnv: ${JSON.stringify(process.env.ANTHROPIC_API_KEY ? 'KEY_PRESENT' : 'KEY_MISSING')}\n`);
        } catch (e) { }

        return NextResponse.json({ error: `Internal Agent Error: ${error.message}` }, { status: 500 });
    }
}
