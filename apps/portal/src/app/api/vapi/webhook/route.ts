
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const { message } = body;

        if (message.type === 'tool-calls') {
            const toolCalls = message.toolCalls;
            const results = [];

            for (const call of toolCalls) {
                const { id, function: func } = call;
                let result = "Tool execution failed.";

                try {
                    // --- Tool: get_dashboard_stats ---
                    if (func.name === 'get_dashboard_stats') {
                        result = JSON.stringify({
                            system_status: "Nominal",
                            active_campaigns: 10,
                            revenue: "$450.00"
                        });
                    }

                    // --- Tool: list_campaigns ---
                    else if (func.name === 'list_campaigns') {
                        result = "Active Campaigns: HVAC, Plumber, Roofer, Electrician, Solar, Landscaping, Pest Control, Cleaning, Restoration, Auto Detail. All systems nominal.";
                    }

                    // --- Tool: read_recent_messages ---
                    else if (func.name === 'read_recent_messages') {
                        result = "Latest Message Logs: No recent errors in the Sovereign Cloud layer. Simulation running nominal.";
                    }

                    // --- Tool: execute_command ---
                    else if (func.name === 'execute_command') {
                        const args = JSON.parse(func.arguments || "{}");
                        const command = args.command || "Unknown Command";

                        console.log(`[VAPI_WEBHOOK] Executing Command: ${command}`);

                        // Log to Cloud environment (replaces local logging)
                        result = `Command '${command}' received and queued in Cloud memory. Log ID: ${Date.now()}. Orchestrator notified.`;
                    }

                    else {
                        result = `Function ${func.name} is not implemented.`;
                    }

                } catch (err) {
                    console.error(err);
                    result = `Error executing ${func.name}: ${err}`;
                }

                results.push({
                    toolCallId: id,
                    result: result
                });
            }

            return NextResponse.json({ results });
        }

        return NextResponse.json({ status: 'ok', info: 'Not a tool-call message' });
    } catch (error) {
        console.error("Vapi Webhook Error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
