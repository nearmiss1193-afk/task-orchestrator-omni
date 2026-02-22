import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabaseClient';

export const runtime = 'edge';

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const { command } = body;

        if (!command || typeof command !== 'string') {
            return NextResponse.json({ message: "Invalid payload format." }, { status: 400 });
        }

        // 1. Zero-Trust Authentication via PIN Prefix
        const pinPrefix = "1175:";
        if (!command.startsWith(pinPrefix)) {
            return NextResponse.json({ message: "AUTH REJECTED: Invalid or missing Security PIN." }, { status: 401 });
        }

        // 2. Parse Instruction Payload
        const instruction = command.substring(pinPrefix.length).trim().toLowerCase();

        // HALT PROTCOL
        if (instruction.includes("halt") || instruction.includes("stop") || instruction.includes("pause") || instruction.includes("suspend")) {

            // Dispatch hard halt to Database system_state overriding the crons
            const { error } = await supabase
                .from('system_state')
                .update({ status: 'stopped', updated_at: new Date().toISOString() })
                .eq('key', 'campaign_mode');

            if (error) {
                console.error("Supabase override failed:", error);
                return NextResponse.json({ message: "Database Exception: Unable to engage Halt Protocol." }, { status: 500 });
            }

            return NextResponse.json({ message: "Override Accepted. Halt Protocol Engaged. All campaigns suspended." }, { status: 200 });
        }

        // RESUME PROTOCOL
        if (instruction.includes("resume") || instruction.includes("start") || instruction.includes("engage") || instruction.includes("activate")) {

            const { error } = await supabase
                .from('system_state')
                .update({ status: 'working', updated_at: new Date().toISOString() })
                .eq('key', 'campaign_mode');

            if (error) {
                return NextResponse.json({ message: "Database Exception: Unable to engage Resume Protocol." }, { status: 500 });
            }

            return NextResponse.json({ message: "Override Accepted. Live Autonomous Campaigns Resumed." }, { status: 200 });
        }

        // UNKNOWN COMMAND
        return NextResponse.json({ message: "Command authenticated but not recognized. Available protocols: [Halt, Resume]" }, { status: 400 });

    } catch (e: any) {
        return NextResponse.json({ message: `Fatal Edge Exception: ${e.message}` }, { status: 500 });
    }
}
