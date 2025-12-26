import { NextResponse } from 'next/server';
import { StateManager } from '@/lib/state-manager';

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const planId = searchParams.get('planId');

    if (!planId) {
        return NextResponse.json({ error: "Missing planId" }, { status: 400 });
    }

    const plan = StateManager.getPlan(planId);
    const logs = StateManager.getLogs(planId);

    if (!plan) {
        return NextResponse.json({ error: "Plan not found" }, { status: 404 });
    }

    return NextResponse.json({ plan, logs });
}
