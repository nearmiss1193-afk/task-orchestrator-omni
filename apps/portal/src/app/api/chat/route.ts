
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// CORS headers to allow cross-origin requests from dashboard
const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
};

// Handle OPTIONS preflight requests
export async function OPTIONS() {
    return NextResponse.json({}, { headers: corsHeaders });
}

export async function POST(req: Request) {
    try {
        const body = await req.json();
        // Accept both 'command' (from dashboard.html) and 'message' (from chat-interface.tsx)
        const message = body.command || body.message || '';
        const lowerMsg = message.toLowerCase();

        // Feature 1: "Search the Internet"
        if (lowerMsg.includes("search") || lowerMsg.includes("find")) {
            // Mock Search Results for Demo
            const searchResults = [
                `Top 3 Competitors in ${lowerMsg.replace('search', '').replace('find', '').trim()}:`,
                "1. Green Valley HVAC (Ad Spend: $5k/mo)",
                "2. City Wide Plumbing (Weak SEO)",
                "3. Solar Direct (New Entrant)"
            ];

            return NextResponse.json({
                response: `🔍 Searching Sovereign Web Index for "${message}"...\n\n${searchResults.join('\n')}\n\n[Analysis] Opportunity detected to outbid Competitor #2.`
            }, { headers: corsHeaders });
        }

        // Feature 2: "Tell Antigravity" / Delegate
        if (lowerMsg.includes("antigravity") || lowerMsg.includes("update") || lowerMsg.includes("tell")) {
            return NextResponse.json({
                response: `✅ Command logged for Antigravity Protocol in Sovereign Cloud Memory.\n\nI have notified the core agent.`
            }, { headers: corsHeaders });
        }

        // Feature 3: Status / General (Fallback to previous logic but smarter)
        if (lowerMsg.includes("status")) {
            return NextResponse.json({ response: "Sovereign Status: ONLINE. 10 Agents Active. Revenue: $850.00." }, { headers: corsHeaders });
        }

        return NextResponse.json({
            response: "I'm listening. You can ask me to 'Search for [niche]' or 'Tell Antigravity [instruction]'."
        }, { headers: corsHeaders });

    } catch (error) {
        console.error("Chat API Error:", error);
        return NextResponse.json({ error: "Failed to process message" }, { status: 500, headers: corsHeaders });
    }
}

