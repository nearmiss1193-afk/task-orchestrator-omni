import { NextResponse } from 'next/server';
import { Orchestrator } from '@/lib/orchestrator';

// In a real app, this should probably use a background queue (BullMQ/Redis)
// For this demo, we run it in the request but don't await completion for the response,
// or we just await it if we want to block (but for long running tasks we shouldn't).
// We'll trigger it effectively "background" by not awaiting core processing if we want immediate response,
// but for the sake of simplicity/debugging, the orchestrator.executePlan is async.
// We will fire and forget here to allow polling of status.

import { StateManager } from '@/lib/state-manager';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        let planId = body.planId;

        // If raw plan provided, save it first
        if (!planId && body.planCallback) {
            const plan = body.planCallback;
            planId = plan.id;
            StateManager.savePlan(plan);
        }

        const orchestrator = new Orchestrator();

        // Fire and forget
        orchestrator.executePlan(planId).catch(err => console.error("Background execution error", err));

        return NextResponse.json({ success: true, message: "Execution started" });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
