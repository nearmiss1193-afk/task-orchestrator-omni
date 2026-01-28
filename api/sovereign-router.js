/**
 * SOVEREIGN COMMAND CENTER
 * Unified AI Router - Routes requests to specialized AI agents
 * 
 * Specialists:
 * - Claude: Chief Strategy Officer (planning, copywriting, campaigns)
 * - ChatGPT: Research Director (market research, data gathering)
 * - Grok: Intelligence Officer (trending news, real-time data)
 * - Gemini: Code Specialist (Python, JavaScript, technical tasks)
 * - Manis: Deployment & Scraping (task queue pattern)
 */

// Intent patterns for routing
const INTENT_PATTERNS = {
    manis_deploy: {
        keywords: ['deploy', 'build website', 'create website', 'launch site'],
        specialist: 'manis',
        sequential: ['claude', 'manis'], // Claude plans, Manis executes
        description: 'Deployment tasks'
    },
    grok: {
        keywords: ['trending', 'news', 'latest', 'twitter', 'x.com', 'viral', 'whats happening'],
        specialist: 'grok',
        description: 'Real-time intelligence'
    },
    chatgpt: {
        keywords: ['research', 'analyze', 'find data', 'market research', 'competitor', 'statistics'],
        specialist: 'chatgpt',
        description: 'Research & analysis'
    },
    gemini: {
        keywords: ['code', 'script', 'python', 'javascript', 'typescript', 'debug', 'function', 'algorithm'],
        specialist: 'gemini',
        description: 'Code generation'
    },
    manis_scrape: {
        keywords: ['leads', 'scrape', 'extract', 'crawl', 'harvest'],
        specialist: 'manis',
        description: 'Data extraction'
    },
    claude: {
        keywords: ['strategy', 'plan', 'campaign', 'write', 'copy', 'email', 'post', 'content', 'social media'],
        specialist: 'claude',
        description: 'Strategy & copywriting'
    }
};

// Detect intent from message
function detectIntent(message) {
    const lowerMessage = message.toLowerCase();

    for (const [intentKey, intent] of Object.entries(INTENT_PATTERNS)) {
        for (const keyword of intent.keywords) {
            if (lowerMessage.includes(keyword)) {
                return {
                    intent: intentKey,
                    specialist: intent.specialist,
                    sequential: intent.sequential || null,
                    description: intent.description,
                    matchedKeyword: keyword
                };
            }
        }
    }

    // Default to Claude for general requests
    return {
        intent: 'default',
        specialist: 'claude',
        sequential: null,
        description: 'General assistant (defaulted to Claude)',
        matchedKeyword: null
    };
}

// Claude connector (Anthropic)
async function callClaude(message, systemPrompt = null) {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
        return { success: false, error: 'ANTHROPIC_API_KEY not configured' };
    }

    try {
        const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': apiKey,
                'anthropic-version': '2023-06-01'
            },
            body: JSON.stringify({
                model: 'claude-sonnet-4-20250514',
                max_tokens: 2048,
                system: systemPrompt || 'You are a Chief Strategy Officer AI. Be concise and actionable.',
                messages: [{ role: 'user', content: message }]
            })
        });

        if (!response.ok) {
            const error = await response.text();
            return { success: false, error: `Claude API error: ${error}` };
        }

        const data = await response.json();
        return {
            success: true,
            response: data.content[0].text,
            model: 'claude-sonnet-4-20250514',
            usage: data.usage
        };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ChatGPT connector (OpenAI via Vercel AI Gateway) - with retry logic
async function callChatGPT(message, systemPrompt = null, retries = 3) {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
        return { success: false, error: 'OPENAI_API_KEY not configured', available: false };
    }

    for (let attempt = 1; attempt <= retries; attempt++) {
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 30000); // 30s timeout

            const response = await fetch('https://ai-gateway.vercel.sh/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify({
                    model: 'openai/gpt-4o-mini',
                    messages: [
                        { role: 'system', content: systemPrompt || 'You are a Research Director AI. Provide thorough analysis.' },
                        { role: 'user', content: message }
                    ],
                    max_tokens: 2048
                }),
                signal: controller.signal
            });

            clearTimeout(timeout);

            if (!response.ok) {
                const error = await response.text();
                if (attempt < retries) continue;
                return { success: false, error: `ChatGPT API error: ${error}` };
            }

            const data = await response.json();
            return {
                success: true,
                response: data.choices[0].message.content,
                model: 'gpt-4o-mini',
                usage: data.usage
            };
        } catch (error) {
            if (error.name === 'AbortError') {
                if (attempt < retries) continue;
                return { success: false, error: 'ChatGPT request timed out after 30s' };
            }
            if (attempt < retries) continue;
            return { success: false, error: error.message };
        }
    }
}

// Grok connector (xAI)
async function callGrok(message, systemPrompt = null) {
    const apiKey = process.env.GROK_API_KEY;
    if (!apiKey) {
        return { success: false, error: 'GROK_API_KEY not configured', available: false };
    }

    try {
        const response = await fetch('https://api.x.ai/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: 'grok-4-1-fast',
                messages: [
                    { role: 'system', content: systemPrompt || 'You are an Intelligence Officer AI. Provide real-time insights.' },
                    { role: 'user', content: message }
                ],
                max_tokens: 2048
            })
        });

        if (!response.ok) {
            const error = await response.text();
            return { success: false, error: `Grok API error: ${error}` };
        }

        const data = await response.json();
        return {
            success: true,
            response: data.choices[0].message.content,
            model: 'grok-4-1-fast',
            usage: data.usage
        };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Gemini connector (Google)
async function callGemini(message, systemPrompt = null) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
        return { success: false, error: 'GEMINI_API_KEY not configured', available: false };
    }

    try {
        const response = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=${apiKey}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: systemPrompt
                                ? `${systemPrompt}\n\nUser request: ${message}`
                                : message
                        }]
                    }],
                    generationConfig: {
                        maxOutputTokens: 2048
                    }
                })
            }
        );

        if (!response.ok) {
            const error = await response.text();
            return { success: false, error: `Gemini API error: ${error}` };
        }

        const data = await response.json();
        return {
            success: true,
            response: data.candidates[0].content.parts[0].text,
            model: 'gemini-1.5-pro',
            usage: { prompt_tokens: 0, completion_tokens: 0 } // Gemini doesn't return usage same way
        };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Manis connector (Supabase task queue)
async function queueManisTask(message, taskType = 'general') {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_KEY;

    if (!supabaseUrl || !supabaseKey) {
        return { success: false, error: 'Supabase not configured for Manis tasks', available: false };
    }

    try {
        const taskId = `manis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        const response = await fetch(`${supabaseUrl}/rest/v1/manis_tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': supabaseKey,
                'Authorization': `Bearer ${supabaseKey}`,
                'Prefer': 'return=representation'
            },
            body: JSON.stringify({
                task_id: taskId,
                task_type: taskType,
                payload: { message, created_at: new Date().toISOString() },
                status: 'pending',
                created_at: new Date().toISOString()
            })
        });

        if (!response.ok) {
            const error = await response.text();
            return { success: false, error: `Manis queue error: ${error}` };
        }

        return {
            success: true,
            response: `Task queued for Manis (ID: ${taskId}). Manis will process this asynchronously.`,
            taskId,
            model: 'manis-queue',
            async: true
        };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Main router function
async function routeRequest(message, options = {}) {
    const startTime = Date.now();
    const intent = detectIntent(message);

    let result;
    const metadata = {
        intent: intent.intent,
        specialist: intent.specialist,
        matchedKeyword: intent.matchedKeyword,
        description: intent.description,
        timestamp: new Date().toISOString()
    };

    // Handle sequential routing (e.g., Claude plans, Manis executes)
    if (intent.sequential) {
        const results = [];
        for (const specialist of intent.sequential) {
            const stepResult = await callSpecialist(specialist, message, options);
            results.push({ specialist, ...stepResult });
            if (!stepResult.success) break;
        }
        result = {
            success: results.every(r => r.success),
            responses: results,
            sequential: true
        };
    } else {
        result = await callSpecialist(intent.specialist, message, options);
    }

    return {
        success: result.success,
        response: result.response || result.responses,
        metadata: {
            ...metadata,
            model: result.model,
            usage: result.usage,
            latencyMs: Date.now() - startTime,
            sequential: result.sequential || false
        },
        error: result.error
    };
}

// Call specific specialist
async function callSpecialist(specialist, message, options = {}) {
    switch (specialist) {
        case 'claude':
            return callClaude(message, options.systemPrompt);
        case 'chatgpt':
            return callChatGPT(message, options.systemPrompt);
        case 'grok':
            return callGrok(message, options.systemPrompt);
        case 'gemini':
            return callGemini(message, options.systemPrompt);
        case 'manis':
            return queueManisTask(message, options.taskType || 'general');
        default:
            return callClaude(message, options.systemPrompt); // Default to Claude
    }
}

// Vercel serverless handler
export default async function handler(req, res) {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method === 'GET') {
        // Health check / info endpoint
        return res.status(200).json({
            name: 'Sovereign Command Center',
            version: '1.0.0',
            specialists: {
                claude: { role: 'Chief Strategy Officer', status: process.env.ANTHROPIC_API_KEY ? 'configured' : 'not configured' },
                chatgpt: { role: 'Research Director', status: process.env.OPENAI_API_KEY ? 'configured' : 'not configured' },
                grok: { role: 'Intelligence Officer', status: process.env.GROK_API_KEY ? 'configured' : 'not configured' },
                gemini: { role: 'Code Specialist', status: process.env.GEMINI_API_KEY ? 'configured' : 'not configured' },
                manis: { role: 'Deployment & Scraping', status: process.env.SUPABASE_URL ? 'configured' : 'not configured' }
            },
            endpoints: {
                route: 'POST /api/sovereign-router',
                health: 'GET /api/sovereign-router'
            }
        });
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { message, specialist, systemPrompt, taskType } = req.body;

        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }

        let result;

        // If specialist is explicitly specified, use it directly
        if (specialist) {
            result = await callSpecialist(specialist, message, { systemPrompt, taskType });
            result.metadata = {
                specialist,
                intent: 'explicit',
                description: `Directly called ${specialist}`,
                timestamp: new Date().toISOString()
            };
        } else {
            // Auto-route based on intent
            result = await routeRequest(message, { systemPrompt, taskType });
        }

        return res.status(200).json(result);

    } catch (error) {
        console.error('Sovereign Router Error:', error);
        return res.status(500).json({
            success: false,
            error: error.message,
            metadata: { timestamp: new Date().toISOString() }
        });
    }
}
