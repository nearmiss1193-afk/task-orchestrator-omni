import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
    try {
        // Path to server_state.json in the project root (3 levels up from this file)
        // Or absolute path if we know it. Assuming execution context allows reading relative.
        // apps/portal/src/app/api/status -> apps/portal -> empire-unified

        // Use process.cwd() to find the root.
        const statePath = path.join(process.cwd(), '../../../server_state.json');

        let statusData;
        if (fs.existsSync(statePath)) {
            const fileContent = fs.readFileSync(statePath, 'utf-8');
            statusData = JSON.parse(fileContent);
            statusData.network_status = "Live (Sovereign)";
        } else {
            // Fallback if file not found
            statusData = {
                active_agents: 10,
                system_load: "15%",
                network_status: "Simulated",
                notifications: 2,
                revenue_today: "$450.00"
            };
        }

        return NextResponse.json(statusData);
    } catch (error) {
        console.error("API Error:", error);
        return NextResponse.json({ error: "Failed to fetch status" }, { status: 500 });
    }
}
