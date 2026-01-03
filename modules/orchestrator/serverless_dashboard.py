
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import google.generativeai as genai
from supabase import create_client
import datetime

web_app = FastAPI()

# Enable CORS
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DEPENDENCIES ---
def get_supabase():
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    return create_client(url, key)

def get_gemini():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-pro')

# --- UI HTML (Single File) ---
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EMPIRE COMMAND CENTER | CLOUD</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body { font-family: 'JetBrains Mono', monospace; background-color: #050505; color: #e0e0e0; }
        .terminal-box { background: #0a0a0a; border: 1px solid #333; box-shadow: 0 0 20px rgba(0, 255, 65, 0.05); }
        .glow-text { text-shadow: 0 0 10px rgba(0, 255, 65, 0.5); color: #00ff41; }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .animate-pulse-slow { animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
    </style>
</head>
<body class="h-screen flex flex-col p-6 overflow-hidden">
    <!-- HEADER -->
    <header class="flex justify-between items-center mb-6">
        <div>
            <h1 class="text-3xl font-bold tracking-tighter text-white">EMPIRE <span class="text-[#00ff41]">COMMAND CENTER</span></h1>
            <div class="flex items-center gap-2 mt-1">
                <span class="relative flex h-3 w-3">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                </span>
                <p class="text-xs text-green-500 tracking-widest font-bold">SOVEREIGN STACK V2 // CLOUD ACTIVE</p>
            </div>
        </div>
        <div class="text-right">
            <p class="text-xs text-gray-500">SYSTEM TIME</p>
            <p class="text-xl font-bold" id="clock">00:00:00</p>
        </div>
    </header>

    <!-- MAIN GRID -->
    <div class="grid grid-cols-12 gap-6 flex-1 min-h-0">
        
        <!-- LEFT COL: METRICS & LOGS -->
        <div class="col-span-8 flex flex-col gap-6 h-full min-h-0">
            <!-- KPI CARDS -->
            <div class="grid grid-cols-3 gap-4 h-32 shrink-0">
                <div class="terminal-box p-4 rounded-lg bg-[#0f0f0f]">
                    <p class="text-xs text-gray-400 uppercase">Total Targets</p>
                    <p class="text-4xl font-bold text-white mt-1" id="stat-leads">---</p>
                    <i data-lucide="users" class="text-gray-700 absolute top-4 right-4 h-6 w-6"></i>
                </div>
                <div class="terminal-box p-4 rounded-lg bg-[#0f0f0f]">
                    <p class="text-xs text-gray-400 uppercase">Pending Approvals</p>
                    <p class="text-4xl font-bold text-yellow-500 mt-1" id="stat-pending">---</p>
                    <i data-lucide="activity" class="text-gray-700 absolute top-4 right-4 h-6 w-6"></i>
                </div>
                <div class="terminal-box p-4 rounded-lg bg-[#0f0f0f]">
                    <p class="text-xs text-gray-400 uppercase">System Health</p>
                    <p class="text-4xl font-bold text-green-500 mt-1">100%</p>
                    <i data-lucide="cpu" class="text-gray-700 absolute top-4 right-4 h-6 w-6"></i>
                </div>
            </div>

            <!-- LIVE LOGS -->
            <div class="terminal-box rounded-lg flex-1 flex flex-col min-h-0 overflow-hidden relative">
                <div class="p-3 border-b border-[#333] flex justify-between items-center bg-[#0a0a0a] sticky top-0 z-10">
                    <span class="text-xs font-bold text-green-500 flex items-center gap-2">
                        <i data-lucide="terminal" class="h-3 w-3"></i> LIVE INTELLIGENCE FEED
                    </span>
                    <span class="text-[10px] text-gray-600">STREAMING FROM SUPABASE</span>
                </div>
                <div class="flex-1 overflow-y-auto p-4 space-y-2 font-mono text-sm" id="log-container">
                    <div class="text-gray-500 animate-pulse">Initializing Uplink...</div>
                </div>
                <div class="absolute bottom-0 left-0 right-0 h-10 bg-gradient-to-t from-[#0a0a0a] to-transparent pointer-events-none"></div>
            </div>
        </div>

        <!-- RIGHT COL: ORACLE CHAT -->
        <div class="col-span-4 h-full min-h-0">
            <div class="terminal-box rounded-lg h-full flex flex-col bg-[#0c0c0c] relative overflow-hidden">
                <!-- Header -->
                <div class="p-4 border-b border-[#333] bg-[#0c0c0c] z-10 sticky top-0">
                    <div class="flex items-center gap-2">
                        <div class="h-8 w-8 rounded-full bg-indigo-900/30 flex items-center justify-center border border-indigo-500/30">
                            <i data-lucide="bot" class="text-indigo-400 h-4 w-4"></i>
                        </div>
                        <div>
                            <h2 class="font-bold text-sm text-indigo-400">Empire Oracle</h2>
                            <p class="text-[10px] text-gray-500">GEMINI 1.5 PRO // INTEGRATED</p>
                        </div>
                    </div>
                </div>

                <!-- Chat Area -->
                <div class="flex-1 overflow-y-auto p-4 space-y-4" id="chat-messages">
                    <div class="flex justify-start">
                        <div class="bg-[#1a1a1a] p-3 rounded-lg rounded-tl-none max-w-[85%] text-sm text-gray-300 border border-[#333]">
                           I am online. I have access to your leads, system status, and logs. What is your command?
                        </div>
                    </div>
                </div>

                <!-- Input -->
                <div class="p-4 border-t border-[#333] bg-[#0c0c0c]">
                    <form id="chat-form" class="flex gap-2">
                        <input type="text" id="chat-input" 
                            class="flex-1 bg-[#151515] border border-[#333] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 text-white placeholder-gray-600"
                            placeholder="Ask me about leads or status..." autocomplete="off">
                        <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white p-2 rounded-md transition-colors">
                            <i data-lucide="send" class="h-4 w-4"></i>
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- SCRIPTS -->
    <script>
        lucide.createIcons();
        
        // --- CLOCK ---
        setInterval(() => {
            document.getElementById('clock').innerText = new Date().toLocaleTimeString();
        }, 1000);

        // --- STATE ---
        const logContainer = document.getElementById('log-container');
        let lastLogId = null;

        // --- POLL LOGS & STATS ---
        async function fetchSystemData() {
            try {
                // Fetch Stats
                const statsRes = await fetch('/api/stats');
                const stats = await statsRes.json();
                document.getElementById('stat-leads').innerText = stats.total_leads;
                document.getElementById('stat-pending').innerText = stats.pending_approvals;

                // Fetch Logs
                const logsRes = await fetch('/api/logs');
                const logs = await logsRes.json();
                
                // Render Logs
                // Simple clear and redraw for now to keep order (optimized later)
                logContainer.innerHTML = ''; 
                logs.forEach(log => {
                    const el = document.createElement('div');
                    el.className = 'border-l-2 border-green-900 pl-2 py-1';
                    const time = new Date(log.created_at).toLocaleTimeString();
                    el.innerHTML = `<span class="text-xs text-gray-500">[${time}]</span> <span class="text-green-400 font-mono text-xs">${log.message}</span>`;
                    logContainer.appendChild(el);
                });
            } catch (e) {
                console.error("Poll Error:", e);
            }
        }

        // --- CHAT LOGIC ---
        const chatForm = document.getElementById('chat-form');
        const chatInput = document.getElementById('chat-input');
        const chatContainer = document.getElementById('chat-messages');

        function appendMessage(role, text) {
            const div = document.createElement('div');
            div.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
            
            const bubble = document.createElement('div');
            bubble.className = role === 'user' 
                ? 'bg-indigo-900/50 p-3 rounded-lg rounded-tr-none max-w-[85%] text-sm text-white border border-indigo-500/30'
                : 'bg-[#1a1a1a] p-3 rounded-lg rounded-tl-none max-w-[85%] text-sm text-gray-300 border border-[#333]';
            
            bubble.innerText = text;
            div.appendChild(bubble);
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const msg = chatInput.value.trim();
            if (!msg) return;

            // User Message
            appendMessage('user', msg);
            chatInput.value = '';

            // Loading state
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'flex justify-start';
            loadingDiv.innerHTML = `<div class="bg-[#1a1a1a] p-3 rounded-lg rounded-tl-none text-xs text-gray-500 animate-pulse">Oracle thinking...</div>`;
            chatContainer.appendChild(loadingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: msg })
                });
                const data = await res.json();
                
                // Remove loading
                chatContainer.removeChild(loadingDiv);
                
                if (data.reply) {
                    appendMessage('ai', data.reply);
                }
            } catch (err) {
                chatContainer.removeChild(loadingDiv);
                appendMessage('ai', "System Error: Connection severed.");
            }
        });

        // Initialize
        fetchSystemData();
        setInterval(fetchSystemData, 3000); // Poll every 3s
    </script>
</body>
</html>
"""

# --- ROUTES ---

@web_app.get("/")
async def root():
    return HTMLResponse(content=HTML_CONTENT)

@web_app.get("/api/stats")
async def stats():
    try:
        supabase = get_supabase()
        # Count Leads
        counts = supabase.table("contacts_master").select("*", count="exact").execute()
        total = counts.count
        
        # Pending Replies
        pending = supabase.table("staged_replies").select("*", count="exact").eq("status", "pending_approval").execute()
        p_count = pending.count
        
        return {"total_leads": total, "pending_approvals": p_count}
    except Exception as e:
        return {"error": str(e), "total_leads": 0, "pending_approvals": 0}

@web_app.get("/api/logs")
async def logs():
    try:
        supabase = get_supabase()
        res = supabase.table("brain_logs").select("message, created_at").order("created_at", desc=True).limit(50).execute()
        return res.data
    except Exception as e:
        return []

@web_app.post("/api/chat")
async def chat(payload: dict):
    msg = payload.get("message")
    
    # 1. Fetch Context
    supabase = get_supabase()
    logs_res = supabase.table("brain_logs").select("message, created_at").order("created_at", desc=True).limit(10).execute()
    logs = logs_res.data
    
    # 2. Build Prompt
    system_prompt = f"""
    You are the EMPIRE ORACLE, the interface for the Sovereign Stack.
    
    SYSTEM STATUS:
    - Recent Logs:
    {json.dumps(logs, indent=2)}
    
    USER QUERY: {msg}
    
    MISSION:
    - Answer the user's question using the logs above.
    - If they ask about status, summarize the recent logs.
    - Be brief, professional, and confident.
    """
    
    # 3. Generate
    model = get_gemini()
    try:
        res = model.generate_content(system_prompt)
        return {"reply": res.text}
    except Exception as e:
        return {"reply": f"Oracle Error: {str(e)}"}
