
import { GoogleGenerativeAI } from '@google/generative-ai';
import { GoogleGenerativeAIStream, Message, StreamingTextResponse } from 'ai';

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY || '');

export const runtime = 'edge';

const buildGoogleGenAIPrompt = (messages: Message[]) => ({
    contents: messages
        .filter(message => message.role === 'user' || message.role === 'assistant')
        .map(message => ({
            role: message.role === 'user' ? 'user' : 'model',
            parts: [{ text: message.content }],
        })),
});


import { createClient } from '@supabase/supabase-js';

// Create a private Supabase client for the API route (server-side)
// We use the env vars directly since this runs on the server
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
const supabase = createClient(supabaseUrl, supabaseKey);

export async function POST(req: Request) {
    const { messages } = await req.json();

    // 1. Fetch Live Context (The "Link" to the System)
    const { data: logs } = await supabase
        .from('brain_logs')
        .select('message, created_at')
        .order('created_at', { ascending: false })
        .limit(10);

    const { count: leadCount } = await supabase
        .from('contacts_master')
        .select('*', { count: 'exact', head: true });

    // 2. Construct System Context
    const systemContext = `
    SYSTEM STATUS REPORT:
    - Total Leads: ${leadCount || 'Unknown'}
    - Recent Activity Logs:
    ${logs?.map(l => `  [${new Date(l.created_at).toLocaleTimeString()}] ${l.message}`).join('\n') || 'No recent logs'}
    
    IDENTITY:
    You are the 'Empire Oracle', the voice of the Sovereign Stack.
    You have direct access to the system logs above. 
    Use them to answer the user's questions specifically.
    If the logs show a deployment or scrape, mention it.
    Be concise, technical, and 'Spartan'.
    `;

    // 3. Call Gemini
    const geminiStream = await genAI
        .getGenerativeModel({ model: 'gemini-1.5-pro', systemInstruction: systemContext })
        .generateContentStream(buildGoogleGenAIPrompt(messages));

    const stream = GoogleGenerativeAIStream(geminiStream);

    return new StreamingTextResponse(stream);
}
