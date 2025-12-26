
import { google } from '@ai-sdk/google';
import { streamText } from 'ai';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req: Request) {
    const { messages } = await req.json();

    const result = await streamText({
        model: google('gemini-1.5-flash'),
        system: "You are the 'Empire Oracle', an AI system interface for the 'Sovereign Stack' autonomous agency. You answer questions about the system status, leads, and strategy. Be concise, technical, and 'Spartan' in tone.",
        messages,
    });

    return result.toDataStreamResponse();
}
