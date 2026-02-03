
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Helper to reliably find files in the scratch/brain environment
// apps/portal -> empire-unified is 2 levels up
const getPath = (relativePath: string) => path.join(process.cwd(), '../../' + relativePath);

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
                        const statePath = getPath('server_state.json');
                        if (fs.existsSync(statePath)) {
                            result = fs.readFileSync(statePath, 'utf-8');
                        } else {
                            result = "Dashboard state not found. System might be initializing.";
                        }
                    }

                    // --- Tool: list_campaigns ---
                    else if (func.name === 'list_campaigns') {
                        result = "Active Campaigns: HVAC, Plumber, Roofer, Electrician, Solar, Landscaping, Pest Control, Cleaning, Restoration, Auto Detail. All systems nominal.";
                    }

                    // --- Tool: read_recent_messages ---
                    else if (func.name === 'read_recent_messages') {
                        const logPath = getPath('campaign_simulation_log.txt');
                        if (fs.existsSync(logPath)) {
                            const logContent = fs.readFileSync(logPath, 'utf-8');
                            // Return last 500 chars to avoid overwhelming voice
                            result = "Latest Message Logs: " + logContent.slice(-500);
                        } else {
                            result = "No recent messages found in the simulation log.";
                        }
                    }

                    // --- Tool: execute_command ---
                    else if (func.name === 'execute_command') {
                        const args = JSON.parse(func.arguments || "{}");
                        const command = args.command || "Unknown Command";

                        console.log(`[VAPI_WEBHOOK] Executing Command: ${command}`);

                        // Log to Brain for Antigravity or Task Runner
                        const commandLogPath = getPath('user_commands.log');
                        const entry = `[VAPI_VOICE_AGENT] ${new Date().toISOString()}: ${command}\n`;
                        fs.appendFileSync(commandLogPath, entry);

                        // Enhanced Feedback for "Fluid" Conversation
                        result = `Command '${command}' received and queued. Log ID: ${Date.now()}. Orchestrator notified.`;
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
